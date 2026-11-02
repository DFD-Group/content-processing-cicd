import re

from pywinauto.timings import wait_until_passes

from app.helpers.wait_until_rectangle_is_stable import (
    wait_until_rectangle_is_stable,
)
from app.viber.selectors import (
    info_button_id_pattern,
    info_sidebar_id_pattern,
)


def open_info_sidebar(chat_pane):
    """Find and return the visible Viber info sidebar.

    The function searches for `info_sidebar` among the controls next to
    `chat_pane`. If `info_sidebar` is already visible, it is used directly
    without clicking `info_button`. Otherwise, `info_button` is clicked and
    the function waits up to 30 seconds for `info_sidebar` to become visible.
    Finally, it waits for the sidebar position to stabilize.

    Args:
        chat_pane: The current Viber chat pane control.

    Returns:
        UIAWrapper: The visible and stabilized `info_sidebar`.

    Raises:
        StopIteration: If `info_button` cannot be found.
        TimeoutError: If `info_sidebar` does not appear within 30 seconds
            or its position does not stabilize.
        RuntimeError: If `info_sidebar` is still None after the opening attempt.
    """

    info_button = next(
        control
        for control in chat_pane.descendants(
            control_type="Button",
        )
        if re.search(
            info_button_id_pattern,
            control.element_info.automation_id or "",
        )
    )

    info_sidebar = next(
        (
            control
            for control in (
                chat_pane.parent().children()
            )
            if (
                re.search(
                    info_sidebar_id_pattern,
                    (
                        control
                        .element_info
                        .automation_id
                        or ""
                    ),
                )
                and control.is_visible()
            )
        ),
        None,
    )

    if info_sidebar is None:
        info_button.click_input()

        info_sidebar = wait_until_passes(
            timeout=30,
            retry_interval=0.25,
            func=lambda: next(
                control
                for control in (
                    chat_pane.parent().children()
                )
                if (
                    re.search(
                        info_sidebar_id_pattern,
                        (
                            control
                            .element_info
                            .automation_id
                            or ""
                        ),
                    )
                    and control.is_visible()
                )
            ),
        )

    if info_sidebar is None:
        raise RuntimeError(
            "Info sidebar не успя да се отвори."
        )

    wait_until_rectangle_is_stable(
        info_sidebar,
    )

    print(
        "SIDEBAR (стабилен):",
        info_sidebar.rectangle(),
    )

    return info_sidebar