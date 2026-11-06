
import ctypes
import os
from ctypes import wintypes


def diagnose_desktop(x: int, y: int) -> bool:
    """Diagnose Windows desktop access and mouse cursor availability.

    Checks the current Windows session, input desktop, thread desktop,
    and whether the mouse cursor can be moved to the given coordinates.

    Args:
        x: Target horizontal cursor coordinate.
        y: Target vertical cursor coordinate.

    Returns:
        True if SetCursorPos succeeds, otherwise False.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    desktop_readobjects = 0x0001
    uoi_name = 2

    kernel32.GetCurrentThreadId.restype = wintypes.DWORD

    kernel32.ProcessIdToSessionId.argtypes = [
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.ProcessIdToSessionId.restype = wintypes.BOOL

    user32.OpenInputDesktop.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    user32.OpenInputDesktop.restype = wintypes.HANDLE

    user32.GetThreadDesktop.argtypes = [wintypes.DWORD]
    user32.GetThreadDesktop.restype = wintypes.HANDLE

    user32.GetUserObjectInformationW.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetUserObjectInformationW.restype = wintypes.BOOL

    user32.CloseDesktop.argtypes = [wintypes.HANDLE]
    user32.CloseDesktop.restype = wintypes.BOOL

    user32.SetCursorPos.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
    ]
    user32.SetCursorPos.restype = wintypes.BOOL

    def get_desktop_name(handle):
        """Return the desktop name and its Windows error, if any."""
        if not handle:
            return None, None

        buffer = ctypes.create_unicode_buffer(256)
        needed = wintypes.DWORD()

        ctypes.set_last_error(0)
        success = user32.GetUserObjectInformationW(
            handle,
            uoi_name,
            buffer,
            ctypes.sizeof(buffer),
            ctypes.byref(needed),
        )

        if success:
            return buffer.value, None

        return None, ctypes.get_last_error()

    def describe_error(error):
        """Convert a Windows error code into a readable message."""
        if error is None:
            return "Not available"

        if error == 0:
            return "No Windows error details provided"

        return f"{ctypes.FormatError(error).strip()} (code: {error})"

    pid = os.getpid()
    thread_id = kernel32.GetCurrentThreadId()

    session_id = wintypes.DWORD()

    ctypes.set_last_error(0)
    session_ok = kernel32.ProcessIdToSessionId(
        pid,
        ctypes.byref(session_id),
    )
    session_error = (
        None if session_ok else ctypes.get_last_error()
    )

    ctypes.set_last_error(0)
    input_desktop = user32.OpenInputDesktop(
        0,
        False,
        desktop_readobjects,
    )
    input_error = (
        None if input_desktop else ctypes.get_last_error()
    )

    try:
        input_name, input_name_error = get_desktop_name(
            input_desktop,
        )

        ctypes.set_last_error(0)
        thread_desktop = user32.GetThreadDesktop(thread_id)
        thread_error = (
            None if thread_desktop else ctypes.get_last_error()
        )

        thread_name, thread_name_error = get_desktop_name(
            thread_desktop,
        )

        ctypes.set_last_error(0)
        cursor_success = bool(user32.SetCursorPos(x, y))
        cursor_error = (
            None if cursor_success else ctypes.get_last_error()
        )

        print("\n===== WINDOWS DESKTOP DIAGNOSTICS =====", flush=True)

        print(f"Process ID: {pid}", flush=True)
        print(f"Thread ID: {thread_id}", flush=True)

        print(
            f"Windows Session: "
            f"{session_id.value if session_ok else 'Unavailable'}",
            flush=True,
        )

        if not session_ok:
            print(
                f"Session error: {describe_error(session_error)}",
                flush=True,
            )

        print(
            f"Input Desktop: {input_name or 'Unavailable'}",
            flush=True,
        )

        if not input_name:
            print(
                f"Input desktop error: "
                f"{describe_error(input_name_error or input_error)}",
                flush=True,
            )

        print(
            f"Thread Desktop: {thread_name or 'Unavailable'}",
            flush=True,
        )

        if not thread_name:
            print(
                f"Thread desktop error: "
                f"{describe_error(thread_name_error or thread_error)}",
                flush=True,
            )

        print(
            f"Mouse Cursor Position: x={x}, y={y}",
            flush=True,
        )
        print(
            f"Mouse Cursor Movement: "
            f"{'Success' if cursor_success else 'Failed'}",
            flush=True,
        )

        if not cursor_success:
            print(
                f"Cursor error: {describe_error(cursor_error)}",
                flush=True,
            )

        print(
            f"Desktop Access: "
            f"{'Available' if input_desktop and thread_desktop else 'Unavailable'}",
            flush=True,
        )

        print("=======================================\n", flush=True)

        return cursor_success

    finally:
        if input_desktop:
            user32.CloseDesktop(input_desktop)
