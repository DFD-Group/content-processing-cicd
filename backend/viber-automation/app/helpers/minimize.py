import ctypes
from pywinauto.timings import wait_until

def minimize(app_window):
    """Minimize `app_window` and wait for Windows to confirm it.

        Args:
            app_window: The application window that will be minimized.

        Returns:
            None
    """
    if not app_window.exists(timeout=1):
        return

    window_handle = app_window.handle

    ctypes.windll.user32.ShowWindow(
        window_handle,
        6,
    )

    wait_until(
        timeout=30,
        retry_interval=0.25,
        func=lambda: bool(
            ctypes.windll.user32.IsIconic(
                window_handle,
            )
        ),
    )