from pywinauto import Application


def restart_app(app_window, close_app_func, app_path):
    """Restart an application, wait until ready, and focus its window."""
    close_app_func(app_window)

    Application(
        backend="uia",
    ).start(
        app_path,
    )

    app_window.wait(
        "exists visible ready",
        timeout=30,
    )

    app_window.set_focus()

    return app_window