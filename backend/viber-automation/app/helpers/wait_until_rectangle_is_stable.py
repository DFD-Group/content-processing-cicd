import time

def wait_until_rectangle_is_stable(
    control,
    timeout=5,
    interval=0.15,
    required_stable_checks=3,
):
    """Wait until the control stops moving on the screen.

    The position of `control` is checked every `interval` seconds. It is
    considered stable when its rectangle remains unchanged for
    `required_stable_checks` consecutive checks.

    Args:
        control: The UI control whose position will be checked.
        timeout: Maximum number of seconds to wait.
        interval: Number of seconds between checks.
        required_stable_checks: Required consecutive unchanged checks.

    Returns:
        Rectangle: The stable rectangle of `control`.

    Raises:
        TimeoutError: If the rectangle does not become stable before
            `timeout` expires.
    """

    deadline = time.time() + timeout
    previous_rect = None
    stable_checks_count = 0

    while time.time() < deadline:
        rect = control.rectangle()

        current_rect = (
            rect.left,
            rect.top,
            rect.right,
            rect.bottom,
        )

        if current_rect == previous_rect:
            stable_checks_count += 1
        else:
            stable_checks_count = 0

        if stable_checks_count >= required_stable_checks:
            return rect

        previous_rect = current_rect
        time.sleep(interval)

    raise TimeoutError(
        "Rectangle is not stable."
    )