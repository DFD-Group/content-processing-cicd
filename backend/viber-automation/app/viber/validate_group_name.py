import re

from app.viber.selectors import (
    group_name_input_id_pattern,
)


def validate_group_name(
    info_sidebar,
    expected_group_name: str,
) -> str:
    """Validate that `info_sidebar` belongs to `expected_group_name`.

    The function finds the visible `group_name_input_field` inside
    `info_sidebar`, reads `current_group_name`, and compares it with
    `expected_group_name`. Leading and trailing spaces are ignored, and
    the comparison is case-insensitive.

    Args:
        info_sidebar: The visible Viber info sidebar control.
        expected_group_name: The exact name of the expected Viber group.

    Returns:
        str: The validated `current_group_name`.

    Raises:
        StopIteration: If the visible `group_name_input_field` is not found.
        RuntimeError: If `current_group_name` does not match
            `expected_group_name`.
    """
    group_name_input_field = next(
        control
        for control in info_sidebar.descendants(
            control_type="Edit",
        )
        if (
            re.search(
                group_name_input_id_pattern,
                control.element_info.automation_id or "",
            )
            and control.is_visible()
        )
    )

    print(
        "GROUP NAME INPUT:",
        group_name_input_field.rectangle(),
        repr(group_name_input_field.window_text()),
    )

    current_group_name = (
        group_name_input_field
        .window_text()
        .strip()
    )

    print(
        current_group_name,
        flush=True,
    )

    if (
        current_group_name.casefold()
        != expected_group_name.strip().casefold()
    ):
        raise RuntimeError(
            "Отворена е грешна Viber група. "
            f"Търсена група: {expected_group_name!r}. "
            f"Отворена група: {current_group_name!r}."
        )

    return current_group_name