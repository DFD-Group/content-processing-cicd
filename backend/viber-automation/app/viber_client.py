import ctypes
import os
import re
import time

from pywinauto import Application, Desktop, keyboard
from pywinauto.timings import wait_until, wait_until_passes


# =====================================================================
# ID ШАБЛОНИ И КОНСТАНТИ
# =====================================================================
search_container_id_pattern = (
    r"\.ApplicationWindowContentControl"
    r"\.SearchItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

split_view_id_pattern = (
    r"^QGuiApplication"
    r"\.MainWindow_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.ApplicationWindowContentControl"
    r"\.SplitView_QMLTYPE_\d+(?:_QML_\d+)?$"
)

chat_pane_id_pattern = (
    r"^QGuiApplication"
    r"\.MainWindow_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.ApplicationWindowContentControl"
    r"\.SplitView_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.StackView_QMLTYPE_\d+(?:_QML_\d+)?$"
)

search_input_id_pattern = (
    r"\.TextFieldItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

message_input_id_pattern = (
    r"\.QQuickTextEdit_QML_\d+$"
)

info_button_id_pattern = (
    r"\.InfoButton_QMLTYPE_\d+(?:_QML_\d+)?$"
)

info_sidebar_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?$"
)

edit_group_name_button_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.IconButton_QMLTYPE_\d+(?:_QML_\d+)?$"
)

group_name_input_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.TextFieldItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

chat_message_id_pattern = (
    r"\.FeedDelegate_QMLTYPE_\d+(?:_QML_\d+)?$"
)

main_content_id_suffix = (
    ".ApplicationWindowContentControl"
)

search_result_automation_id = "delegateLoader"


# =====================================================================
# ПОМОЩНИ ФУНКЦИИ
# =====================================================================


def confirm_viber_is_closed():
    viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    if viber_window.exists(timeout=0):
        raise RuntimeError(
            "Viber все още не е затворен."
        )

    return True


def close_viber():
    viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    if not viber_window.exists(timeout=1):
        return

    process_id = viber_window.element_info.process_id

    viber_application = Application(
        backend="uia",
    ).connect(
        process=process_id,
    )

    viber_application.kill()

    wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=confirm_viber_is_closed,
    )


def minimize_viber():
    viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    if not viber_window.exists(timeout=1):
        return

    window_handle = viber_window.handle

    ctypes.windll.user32.ShowWindow(
        window_handle,
        6,
    )

    wait_until(
        timeout=30,
        retry_interval=0.25,
        func=lambda: bool(
            ctypes.windll.user32.IsIconic(
                window_handle,
            )
        ),
    )


def restart_viber():
    close_viber()

    viber_path = os.path.join(
        os.environ["LOCALAPPDATA"],
        "Viber",
        "Viber.exe",
    )

    Application(
        backend="uia",
    ).start(
        viber_path,
    )

    viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    viber_window.wait(
        "exists visible ready",
        timeout=30,
    )

    viber_window.set_focus()

    return viber_window

def wait_until_rectangle_is_stable(
    control,
    timeout=5,
    interval=0.15,
    required_stable_checks=3,
):
    """Чака правоъгълникът да спре да се мести."""

    deadline = time.time() + timeout
    previous_rect = None
    stable_checks_count = 0

    while time.time() < deadline:
        rect = control.rectangle()

        current_rect = (
            rect.left,
            rect.top,
            rect.right,
            rect.bottom,
        )

        if current_rect == previous_rect:
            stable_checks_count += 1
        else:
            stable_checks_count = 0

        if stable_checks_count >= required_stable_checks:
            return rect

        previous_rect = current_rect
        time.sleep(interval)

    raise TimeoutError(
        "Правоъгълникът не се стабилизира."
    )


def escape_for_send_keys(text):
    """Екранира специалните знаци на pywinauto."""

    return re.sub(
        r"([+^%~(){}\[\]])",
        r"{\1}",
        text,
    )


def prepare_viber_message(
    chat_name: str,
    message_text: str,
) -> None:
    # =====================================================================
    # 1) РЕСТАРТИРАНЕ НА VIBER
    # =====================================================================

    viber_window = restart_viber()

    wait_until_rectangle_is_stable(
        viber_window,
    )

    # =====================================================================
    # 2) НАМИРАНЕ НА ОСНОВНИТЕ ЕЛЕМЕНТИ
    # =====================================================================
    search_container = wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=lambda: next(
            control
            for control in viber_window.descendants(
                control_type="Group",
            )
            if re.search(
                search_container_id_pattern,
                control.element_info.automation_id or "",
            )
        ),
    )


    search_input_field = next(
        control
        for control in search_container.descendants(
            control_type="Edit",
        )
        if re.search(
            search_input_id_pattern,
            control.element_info.automation_id or "",
        )
    )


    # =====================================================================
    # 3) ТЪРСЕНЕ НА ГРУПАТА И ОТВАРЯНЕ НА ЧАТА
    # =====================================================================
    search_input_field.click_input()

    keyboard.send_keys(
        escape_for_send_keys(chat_name),
        with_spaces=True,
    )

    def click_first_search_result():
        current_viber_window = Desktop(
            backend="uia",
        ).window(
            title="Rakuten Viber",
        )

        for main_content in current_viber_window.descendants(
            control_type="Group",
        ):
            automation_id = (
                main_content.element_info.automation_id or ""
            )

            if not automation_id.endswith(
                main_content_id_suffix
            ):
                continue

            search_results = [
                control
                for control in main_content.children()
                if (
                    control.element_info.automation_id
                    == search_result_automation_id
                    and control.is_visible()
                    and control.rectangle().width() > 0
                    and control.rectangle().height() > 0
                )
            ]

            if not search_results:
                continue

            first_search_result = min(
                search_results,
                key=lambda control: control.rectangle().top,
            )

            first_search_result.click_input()
            return True

        raise LookupError(
            "Първият резултат от търсенето не е намерен."
        )


    wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=click_first_search_result,
    )

    chat_pane = wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=lambda: next(
            current_chat_pane
            for current_search_container in Desktop(
                backend="uia",
            ).window(
                title="Rakuten Viber",
            ).descendants(
                control_type="Group",
            )
            if re.search(
                search_container_id_pattern,
                current_search_container.element_info.automation_id or "",
            )
            for current_split_view in (
                current_search_container.parent().children()
            )
            if re.search(
                split_view_id_pattern,
                current_split_view.element_info.automation_id or "",
            )
            for current_chat_pane in current_split_view.children()
            if re.search(
                chat_pane_id_pattern,
                current_chat_pane.element_info.automation_id or "",
            )
        ),
    )

    wait_until_rectangle_is_stable(
        chat_pane,
    )

    print(
        chat_pane.element_info.automation_id,
        flush=True,
    )

    message_input_field = next(
        control
        for control in chat_pane.children(
            control_type="Edit",
        )
        if re.search(
            message_input_id_pattern,
            control.element_info.automation_id or "",
        )
    )

    info_button = next(
        control
        for control in chat_pane.descendants(
            control_type="Button",
        )
        if re.search(
            info_button_id_pattern,
            control.element_info.automation_id or "",
        )
    )

    # =====================================================================
    # 4) ОТВАРЯНЕ НА INFO SIDEBAR
    # =====================================================================
    info_sidebar = next(
        (
            control
            for control in chat_pane.parent().children()
            if re.search(
                info_sidebar_id_pattern,
                control.element_info.automation_id or "",
            )
            and control.is_visible()
        ),
        None,
    )

    if info_sidebar is None:
        info_button.click_input()

        info_sidebar = wait_until_passes(
            timeout=30,
            retry_interval=0.25,
            func=lambda: next(
                control
                for control in chat_pane.parent().children()
                if re.search(
                    info_sidebar_id_pattern,
                    control.element_info.automation_id or "",
                )
                and control.is_visible()
            ),
        )

    if info_sidebar is None:
        raise RuntimeError(
            "Info sidebar не успя да се отвори."
        )

    wait_until_rectangle_is_stable(
        info_sidebar,
    )

    print(
        "SIDEBAR (стабилен):",
        info_sidebar.rectangle(),
    )


    # =====================================================================
    # 5) НАТИСКАНЕ НА МОЛИВА
    # =====================================================================
    sidebar_rect = info_sidebar.rectangle()

    edit_group_name_button = min(
        (
            control
            for control in info_sidebar.children(
                control_type="Button",
            )
            if (
                re.search(
                    edit_group_name_button_id_pattern,
                    control.element_info.automation_id or "",
                )
                and control.rectangle().top
                > sidebar_rect.top + 80
            )
        ),
        key=lambda control: control.rectangle().left,
    )

    print(
        "EDIT BUTTON:",
        edit_group_name_button.rectangle(),
    )

    edit_group_name_button.click_input()

    # Изчакваме полето за името да се появи.
    wait_until_rectangle_is_stable(
        info_sidebar,
    )


    # =====================================================================
    # 6) ПРОВЕРКА НА ИМЕТО НА ГРУПАТА
    # =====================================================================
    group_name_input_field = next(
        control
        for control in info_sidebar.descendants(
            control_type="Edit",
        )
        if re.search(
            group_name_input_id_pattern,
            control.element_info.automation_id or "",
        )
        and control.is_visible()
    )

    print(
        "GROUP NAME INPUT:",
        group_name_input_field.rectangle(),
        repr(
            group_name_input_field.window_text()
        ),
    )

    current_group_name = (
        group_name_input_field
        .window_text()
        .strip()
    )

    print(
        current_group_name,
        flush=True,
    )

    if (
        current_group_name.casefold()
        != chat_name.strip().casefold()
    ):
        raise RuntimeError(
            "Отворена е грешна Viber група. "
            f"Търсена група: {chat_name!r}. "
            f"Отворена група: {current_group_name!r}."
        )


    # =====================================================================
    # 7) ИЗПРАЩАНЕ НА СЪОБЩЕНИЕТО
    # =====================================================================
    message_input_field.click_input()

    message_lines = (
        message_text.splitlines()
    )

    for index, line in enumerate(message_lines):
        keyboard.send_keys(
            escape_for_send_keys(line),
            with_spaces=True,
            pause=0.05,
        )

        if index < len(message_lines) - 1:
            keyboard.send_keys("+{ENTER}")

    wait_until_rectangle_is_stable(
        message_input_field,
    )

    keyboard.send_keys("{ENTER}")

    # Изчакваме съобщението да се появи в чата.
    wait_until_rectangle_is_stable(
        chat_pane,
    )


    # =====================================================================
    # 8) ПРОВЕРКА НА ПОСЛЕДНОТО СЪОБЩЕНИЕ
    # =====================================================================
    chat_messages = [
        control
        for control in chat_pane.children(
            control_type="Group",
        )
        if (
            re.search(
                chat_message_id_pattern,
                control.element_info.automation_id or "",
            )
            and control.rectangle().height() > 0
        )
    ]

    if not chat_messages:
        raise RuntimeError(
            "Не бяха намерени видими "
            "Viber съобщения."
        )

    newest_message = max(
        chat_messages,
        key=lambda control: (
            control.rectangle().bottom
        ),
    )

    newest_message_text = next(
        control.window_text()
        for control in newest_message.children(
            control_type="Edit",
        )
    )

    print(
        "ПОСЛЕДНО СЪОБЩЕНИЕ:",
        repr(newest_message_text),
        flush=True,
    )

    if (
        newest_message_text.strip()
        != message_text.strip()
    ):
        raise RuntimeError(
            "Последното Viber съобщение "
            "не съвпада с очаквания текст."
        )


    # =====================================================================
    # 9) УСПЕХ И МИНИМИЗИРАНЕ
    # =====================================================================
    print(
        "Съобщението е изпратено успешно.",
        flush=True,
    )

    minimize_viber()
