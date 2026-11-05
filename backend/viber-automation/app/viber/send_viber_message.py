
from pywinauto import keyboard

from app.helpers.diagnose_desktop import diagnose_desktop
from app.helpers.escape_for_send_keys import (
    escape_for_send_keys,
)
from app.helpers.wait_until_rectangle_is_stable import (
    wait_until_rectangle_is_stable,
)


def send_viber_message(
    message_input_field,
    message_text: str,
) -> None:
    """Type and send `message_text` through `message_input_field`.

    The function diagnoses desktop access before clicking the input
    field, then types each line with escaped pywinauto characters.
    Shift+Enter preserves line breaks, and Enter sends the message.

    Args:
        message_input_field: The Viber message input control.
        message_text: The complete message to send.

    Returns:
        None
    """
    # Diagnose desktop access before clicking the message field.
    rect = message_input_field.rectangle()

    diagnose_desktop(
        (rect.left + rect.right) // 2,
        (rect.top + rect.bottom) // 2,
    )

    message_input_field.click_input()

    message_lines = message_text.splitlines()

    for index, line in enumerate(
        message_lines,
    ):
        keyboard.send_keys(
            escape_for_send_keys(line),
            with_spaces=True,
            pause=0.05,
        )

        if index < len(message_lines) - 1:
            keyboard.send_keys(
                "+{ENTER}",
            )

    wait_until_rectangle_is_stable(
        message_input_field,
    )

    keyboard.send_keys(
        "{ENTER}",
    )