from pywinauto import keyboard

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

The function clicks `message_input_field`, splits `message_text` into
separate lines, and types each line after escaping the special pywinauto
characters. Shift+Enter is used between lines to preserve line breaks.
After the input field becomes stable, Enter is pressed to send the message.

Args:
    message_input_field: The Viber message input control.
    message_text: The complete message that will be typed and sent.

Returns:
    None
"""

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