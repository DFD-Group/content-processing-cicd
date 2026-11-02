def confirm_viber_is_closed(app_window):
    """Check whether the Viber window is closed.

    Args:
        app_window: The Viber window specification.

    Returns:
        bool: True if the window no longer exists.

    Raises:
        RuntimeError: If the window still exists.
    """
    if app_window.exists(timeout=0):
        raise RuntimeError("Viber is still open.")

    return True