
import ctypes
import os
from ctypes import wintypes


def diagnose_desktop() -> None:
    """Log the current Windows session and desktop context."""
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

    user32.GetThreadDesktop.argtypes = [
        wintypes.DWORD,
    ]
    user32.GetThreadDesktop.restype = wintypes.HANDLE

    user32.GetUserObjectInformationW.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetUserObjectInformationW.restype = wintypes.BOOL

    user32.CloseDesktop.argtypes = [
        wintypes.HANDLE,
    ]
    user32.CloseDesktop.restype = wintypes.BOOL

    def get_desktop_name(handle):
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
            return buffer.value, 0

        return None, ctypes.get_last_error()

    pid = os.getpid()
    thread_id = kernel32.GetCurrentThreadId()

    session_id = wintypes.DWORD()

    ctypes.set_last_error(0)
    session_ok = kernel32.ProcessIdToSessionId(
        pid,
        ctypes.byref(session_id),
    )
    session_error = (
        0 if session_ok else ctypes.get_last_error()
    )

    ctypes.set_last_error(0)
    input_desktop = user32.OpenInputDesktop(
        0,
        False,
        desktop_readobjects,
    )
    input_error = (
        0 if input_desktop else ctypes.get_last_error()
    )

    input_name, input_name_error = get_desktop_name(
        input_desktop,
    )

    ctypes.set_last_error(0)
    thread_desktop = user32.GetThreadDesktop(
        thread_id,
    )
    thread_error = (
        0 if thread_desktop else ctypes.get_last_error()
    )

    thread_name, thread_name_error = get_desktop_name(
        thread_desktop,
    )

    print("\n===== WINDOWS DESKTOP DIAGNOSTICS =====", flush=True)
    print("PID:", pid, flush=True)
    print("Thread ID:", thread_id, flush=True)
    print(
        "Session ID:",
        session_id.value if session_ok else "UNKNOWN",
        flush=True,
    )
    print("Session error:", session_error, flush=True)

    print("Input desktop:", input_name, flush=True)
    print("OpenInputDesktop error:", input_error, flush=True)
    print(
        "Input desktop name error:",
        input_name_error,
        flush=True,
    )

    print("Thread desktop:", thread_name, flush=True)
    print("GetThreadDesktop error:", thread_error, flush=True)
    print(
        "Thread desktop name error:",
        thread_name_error,
        flush=True,
    )
    print("=======================================\n", flush=True)

    if input_desktop:
        user32.CloseDesktop(input_desktop)
