import ctypes
import logging

user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.SetCursorPos.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
]
user32.SetCursorPos.restype = ctypes.c_bool


def diagnostic_set_cursor(x=500, y=300):
    """Check whether Windows allows cursor movement."""
    ctypes.set_last_error(0)

    result = user32.SetCursorPos(x, y)

    if not result:
        error = ctypes.get_last_error()

        logging.error(
            "SetCursorPos FAILED | "
            "x=%s y=%s | "
            "Windows error=%s | %s",
            x,
            y,
            error,
            ctypes.FormatError(error),
        )
        return False

    logging.info(
        "SetCursorPos SUCCESS | x=%s y=%s",
        x,
        y,
    )
    return True