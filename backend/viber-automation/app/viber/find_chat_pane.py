import re

from pywinauto import Desktop

from app.viber.selectors import (
    chat_pane_id_pattern,
    search_container_id_pattern,
    split_view_id_pattern,
)


def find_chat_pane():
    """Find the Viber chat pane by checking the UI hierarchy and automation IDs.

    The function first finds the search container, then its related split view,
    and finally the chat pane whose automation ID matches the configured pattern.

    Returns:
        UIAWrapper: The matching chat pane control.

    Raises:
        StopIteration: If the search container, split view, or chat pane
            cannot be found.
    """

    viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    return next(
        current_chat_pane
        for current_search_container
        in viber_window.descendants(
            control_type="Group",
        )
        if re.search(
            search_container_id_pattern,
            (
                current_search_container
                .element_info
                .automation_id
                or ""
            ),
        )
        for current_split_view in (
            current_search_container
            .parent()
            .children()
        )
        if re.search(
            split_view_id_pattern,
            (
                current_split_view
                .element_info
                .automation_id
                or ""
            ),
        )
        for current_chat_pane in (
            current_split_view.children()
        )
        if re.search(
            chat_pane_id_pattern,
            (
                current_chat_pane
                .element_info
                .automation_id
                or ""
            ),
        )
    )