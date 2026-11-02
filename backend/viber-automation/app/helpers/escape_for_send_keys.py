import re
def escape_for_send_keys(text):
    """Prepare special characters so pywinauto types them as text."""

    return re.sub(
        r"([+^%~(){}\[\]])",
        r"{\1}",
        text,
    )