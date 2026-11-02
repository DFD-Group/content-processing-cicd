import re

from app.viber.selectors import (
    chat_message_id_pattern,
)


def validate_last_message(
    chat_pane,
    expected_message_text: str,
) -> str:
    """Validate that the latest visible message matches `expected_message_text`.

    The function finds all visible `chat_messages` inside `chat_pane` whose
    automation IDs match `chat_message_id_pattern`. It selects
    `newest_message` as the control positioned lowest in the chat and reads
    `newest_message_text` from its Edit control. The text is then compared
    with `expected_message_text`, ignoring leading and trailing whitespace.

    Args:
        chat_pane: The currently open Viber chat pane control.
        expected_message_text: The complete message expected to appear last.

    Returns:
        str: The validated `newest_message_text`.

    Raises:
        RuntimeError: If no visible messages are found or if
            `newest_message_text` does not match `expected_message_text`.
        StopIteration: If `newest_message` does not contain an Edit control.
    """
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
            "Не бяха намерени видими Viber съобщения."
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

    if (
        newest_message_text.strip()
        != expected_message_text.strip()
    ):
        raise RuntimeError(
            "Последното Viber съобщение "
            "не съвпада с очаквания текст."
        )

    return newest_message_text