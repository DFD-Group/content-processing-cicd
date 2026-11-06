from pywinauto import Application
from pywinauto.timings import wait_until_passes
from app.viber.confirm_viber_is_closed import confirm_viber_is_closed

def close_app(app_window):
    """Terminate Viber and wait up to 30 seconds for its window to close.

    Args:
        app_window: The Viber window specification.
    """

    if not app_window.exists(timeout=1):
        return

    process_id = app_window.element_info.process_id

    viber_application = Application(
        backend="uia",
    ).connect(
        process=process_id,
    )

    viber_application.kill()

    wait_until_passes(
        timeout=30,
        retry_interval=0.25,
        func=lambda: confirm_viber_is_closed(app_window),
        exceptions=(RuntimeError,),
    )