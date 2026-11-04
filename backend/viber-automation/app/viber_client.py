
import os
import re

from pywinauto import Desktop, keyboard
from pywinauto.timings import wait_until_passes

from app.helpers.close_app import close_app
from app.helpers.diagnose_desktop import diagnose_desktop
from app.helpers.escape_for_send_keys import escape_for_send_keys
from app.helpers.minimize import minimize
from app.helpers.restart_app import restart_app
from app.helpers.wait_until_rectangle_is_stable import (
    wait_until_rectangle_is_stable,
)

from app.viber.click_first_search_result import (
    click_first_search_result,
)
from app.viber.find_chat_pane import find_chat_pane
from app.viber.open_info_sidebar import open_info_sidebar
from app.viber.selectors import (
    edit_group_name_button_id_pattern,
    message_input_id_pattern,
    search_container_id_pattern,
    search_input_id_pattern,
)
from app.viber.send_viber_message import send_viber_message
from app.viber.validate_group_name import validate_group_name
from app.viber.validate_last_message import validate_last_message

# Validate desktop and mouse access before Viber automation.
diagnose_desktop()


def prepare_viber_message(
    chat_name: str,
    message_text: str,
) -> None:
    """Open a Viber group, send a message, and validate the result.

    The function restarts Viber, finds the search field, searches for
    `chat_name`, and opens the first matching result. It then opens the
    chat info sidebar and validates that the opened group name matches
    `chat_name`.

    After the group is validated, `message_text` is entered and sent.
    The latest visible message is checked to confirm that it matches
    the sent text. Finally, the Viber window is minimized.

    Args:
        chat_name: The exact name of the Viber group.
        message_text: The complete message that will be sent.

    Returns:
        None

    Raises:
        KeyError: If the LOCALAPPDATA environment variable is missing.
        StopIteration: If a required Viber UI control cannot be found.
        RuntimeError: If the opened group or sent message is incorrect.
        TimeoutError: If a UI control does not appear or become stable
            within the configured timeout.
    """
    group_search_text = chat_name
    expected_message_text = message_text

    app_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    viber_path = os.path.join(
        os.environ["LOCALAPPDATA"],
        "Viber",
        "Viber.exe",
    )

    viber_window = restart_app(
        app_window,
        close_app,
        viber_path,
    )

    wait_until_rectangle_is_stable(
        viber_window,
    )

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
                (
                    control
                    .element_info
                    .automation_id
                    or ""
                ),
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

    # Diagnose Windows desktop before mouse interaction.
    diagnose_desktop()

    search_input_field.click_input()

    keyboard.send_keys(
        escape_for_send_keys(
            group_search_text,
        ),
        with_spaces=True,
    )

    wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=click_first_search_result,
    )

    chat_pane = wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=find_chat_pane,
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

    info_sidebar = open_info_sidebar(
        chat_pane,
    )

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
                    (
                        control
                        .element_info
                        .automation_id
                        or ""
                    ),
                )
                and (
                    control.rectangle().top
                    > sidebar_rect.top + 80
                )
            )
        ),
        key=lambda control: (
            control.rectangle().left
        ),
    )

    print(
        "EDIT BUTTON:",
        edit_group_name_button.rectangle(),
    )

    edit_group_name_button.click_input()

    wait_until_rectangle_is_stable(
        info_sidebar,
    )

    validate_group_name(
        info_sidebar,
        group_search_text,
    )

    send_viber_message(
        message_input_field,
        expected_message_text,
    )

    newest_message_text = wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=lambda: validate_last_message(
            chat_pane,
            expected_message_text,
        ),
        exceptions=(
            RuntimeError,
            StopIteration,
        ),
    )

    print(
        "ПОСЛЕДНО СЪОБЩЕНИЕ:",
        repr(newest_message_text),
        flush=True,
    )

    print(
        "Съобщението е изпратено успешно.",
        flush=True,
    )

    minimize(
        viber_window,
    )