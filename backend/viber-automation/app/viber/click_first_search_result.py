from pywinauto import Desktop

from app.viber.selectors import (
    main_content_id_suffix,
    search_result_automation_id,
)


def click_first_search_result() -> bool:
    """Click the topmost visible Viber search result in the first matching group.

    Returns:
        bool: True after clicking the result.

    Raises:
        LookupError: If no visible search result with nonzero dimensions is found.
    """

    current_viber_window = Desktop(
        backend="uia",
    ).window(
        title="Rakuten Viber",
    )

    for main_content in current_viber_window.descendants(
        control_type="Group",
    ):
        automation_id = (
            main_content.element_info.automation_id or ""
        )

        if not automation_id.endswith(
            main_content_id_suffix
        ):
            continue

        search_results = [
            control
            for control in main_content.children()
            if (
                control.element_info.automation_id
                == search_result_automation_id
                and control.is_visible()
                and control.rectangle().width() > 0
                and control.rectangle().height() > 0
            )
        ]

        if not search_results:
            continue

        first_search_result = min(
            search_results,
            key=lambda control: (
                control.rectangle().top
            ),
        )

        first_search_result.click_input()

        return True

    raise LookupError(
        "Първият резултат от търсенето не е намерен."
    )