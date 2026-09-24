import os
import time

from pywinauto import Application, Desktop, keyboard, mouse


def prepare_viber_message(message_text: str) -> None:
    viber = Desktop(backend="uia").window(
        title="Rakuten Viber"
    )

    if not viber.exists():
        Application(backend="uia").start(
            os.path.join(
                os.environ["LOCALAPPDATA"],
                "Viber",
                "Viber.exe",
            )
        )

        viber = Desktop(backend="uia").window(
            title="Rakuten Viber"
        )

        viber.wait("exists", timeout=30)

    viber.restore()
    viber.set_focus()

    # Изчакваме Viber да зареди напълно.
    time.sleep(10)

    # Взимаме полетата от Viber само веднъж.
    fields = viber.descendants(control_type="Edit")

    search = next(
        field
        for field in fields
        if "TextFieldItem"
        in (field.element_info.automation_id or "")
    )

    search_rect = search.rectangle()

    # Само позицията на първия резултат е с отместване.
    first_result_coordinates = (
        search_rect.left + 130,
        search_rect.bottom + 185,
    )

    # Първо намираме и отваряме групата ChatGPT.
    search.click_input()
    search.set_edit_text("#CAL-0001")

    time.sleep(3)

    mouse.click(coords=first_result_coordinates)

    time.sleep(3)

    # След това търсим групата Лазерно рязане.
    search.click_input()
    search.set_edit_text("Лазерно рязане")

    time.sleep(3)

    mouse.click(coords=first_result_coordinates)

    time.sleep(3)

    # След отварянето на групата полето за писане е активно.
    message_lines = message_text.splitlines()

    for index, line in enumerate(message_lines):
        keyboard.send_keys(
            line,
            with_spaces=True,
            pause=0.05,
        )

        if index < len(message_lines) - 1:
            keyboard.send_keys("+{ENTER}")