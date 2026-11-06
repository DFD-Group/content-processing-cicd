
import re

from pywinauto.timings import wait_until_passes

from app.helpers.diagnose_desktop import diagnose_desktop
from app.helpers.wait_until_rectangle_is_stable import (
    wait_until_rectangle_is_stable,
)
from app.viber.selectors import (
    info_button_id_pattern,
    info_sidebar_id_pattern,
)


def open_info_sidebar(chat_pane):
    """Find and return the visible Viber info sidebar.

    If the sidebar is already visible, return it without clicking.
    Otherwise, diagnose desktop access, click the info button,
    and wait for the sidebar to appear and stabilize.

    Args:
        chat_pane: The current Viber chat pane control.

    Returns:
        UIAWrapper: The visible and stabilized info sidebar.

    Raises:
        StopIteration: If a required UI control cannot be found.
        TimeoutError: If the sidebar does not appear or stabilize.
        RuntimeError: If the sidebar cannot be opened.
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
        # Diagnose desktop access before clicking the info button.
        rect = info_button.rectangle()

        diagnose_desktop(
            (rect.left + rect.right) // 2,
            (rect.top + rect.bottom) // 2,
        )

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