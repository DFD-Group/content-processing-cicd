
import ctypes


def minimize_all() -> None:
    """Minimize all open windows using Windows Show Desktop."""
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "open",
        "explorer.exe",
        "shell:::{3080F90D-D7AD-11D9-BD98-0000947B0257}",
        None,
        1,
    )
