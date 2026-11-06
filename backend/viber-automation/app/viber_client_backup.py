import logging
import re
import time

from pywinauto import Desktop, keyboard, mouse


logger = logging.getLogger("uvicorn.error")


REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1139

SEARCH_INPUT = (207, 60)
FIRST_RESULT = (187, 292)
MESSAGE_INPUT = (922, 1102)


def escape_for_send_keys(text):
    return re.sub(
        r"([+^%~(){}\[\]])",
        r"{\1}",
        text,
    )


def prepare_viber_message(
    chat_name: str,
    message_text: str,
) -> None:
    viber = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    viber.wait(
        "exists visible ready",
        timeout=30,
    )

    viber.restore()
    viber.maximize()
    viber.set_focus()

    rect = viber.rectangle()

    def scale(point):
        x, y = point

        return (
            rect.left
            + round(
                x
                * rect.width()
                / REFERENCE_WIDTH
            ),
            rect.top
            + round(
                y
                * rect.height()
                / REFERENCE_HEIGHT
            ),
        )

    search_input = scale(
        SEARCH_INPUT,
    )

    first_result = scale(
        FIRST_RESULT,
    )

    message_input = scale(
        MESSAGE_INPUT,
    )

    logger.info(
        "Backup Viber client coordinates: "
        "search=%s, result=%s, message=%s.",
        search_input,
        first_result,
        message_input,
    )

    mouse.click(
        coords=search_input,
    )

    keyboard.send_keys(
        "^a{BACKSPACE}",
    )

    keyboard.send_keys(
        escape_for_send_keys(chat_name),
        with_spaces=True,
    )

    time.sleep(2)

    mouse.click(
        coords=first_result,
    )

    time.sleep(2)

    mouse.click(
        coords=message_input,
    )

    message_lines = (
        message_text.splitlines()
    )

    for index, line in enumerate(
        message_lines
    ):
        keyboard.send_keys(
            escape_for_send_keys(line),
            with_spaces=True,
        )

        if index < len(message_lines) - 1:
            keyboard.send_keys(
                "+{ENTER}",
            )

    keyboard.send_keys(
        "{ENTER}",
    )

    logger.info(
        "Backup Viber client sent the "
        "message to chat %r.",
        chat_name,
    )

    viber.minimize()