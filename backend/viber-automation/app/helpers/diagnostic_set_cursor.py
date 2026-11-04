import ctypes
import os

user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.SetCursorPos.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
]
user32.SetCursorPos.restype = ctypes.c_bool


def diagnostic_set_cursor(x, y):
    ctypes.set_last_error(0)

    result = user32.SetCursorPos(x, y)
    error = ctypes.get_last_error()

    print("\n===== SET CURSOR DIAGNOSTICS =====", flush=True)
    print(f"PID: {os.getpid()}", flush=True)
    print(f"user32 DLL: {user32._name}", flush=True)
    print(f"user32 Handle: {user32._handle}", flush=True)
    print(f"SetCursorPos coordinates: x={x}, y={y}", flush=True)
    print(f"SetCursorPos result: {result}", flush=True)
    print(f"GetLastError: {error}", flush=True)
    print(f"Windows error message: {ctypes.FormatError(error)}", flush=True)
    print("==================================\n", flush=True)

    return result