import unittest
from unittest.mock import patch

from app.viber.validate_group_name import (
    validate_group_name,
)
from app.viber.validate_last_message import (
    validate_last_message,
)


class ElementInfo:
    def __init__(self, automation_id):
        self.automation_id = automation_id


class Rectangle:
    def __init__(
        self,
        bottom=0,
        height=20,
    ):
        self.bottom = bottom
        self._height = height

    def height(self):
        return self._height


class Control:
    def __init__(
        self,
        automation_id="",
        text="",
        visible=True,
        bottom=0,
        height=20,
        children=None,
    ):
        self.element_info = ElementInfo(
            automation_id,
        )
        self._text = text
        self._visible = visible
        self._rectangle = Rectangle(
            bottom=bottom,
            height=height,
        )
        self._children = children or []

    def descendants(self, control_type=None):
        return self._children

    def children(self, control_type=None):
        return self._children

    def is_visible(self):
        return self._visible

    def rectangle(self):
        return self._rectangle

    def window_text(self):
        return self._text


class ValidateGroupNameTests(unittest.TestCase):
    @patch(
        "app.viber.validate_group_name."
        "group_name_input_id_pattern",
        r"^group-name-input$",
    )
    def test_correct_group_name(self):
        group_name_input = Control(
            automation_id="group-name-input",
            text="Калибровка #CAL-0001",
        )
        info_sidebar = Control(
            children=[group_name_input],
        )

        result = validate_group_name(
            info_sidebar,
            "Калибровка #CAL-0001",
        )

        self.assertEqual(
            result,
            "Калибровка #CAL-0001",
        )

    @patch(
        "app.viber.validate_group_name."
        "group_name_input_id_pattern",
        r"^group-name-input$",
    )
    def test_wrong_group_name(self):
        group_name_input = Control(
            automation_id="group-name-input",
            text="Грешна група",
        )
        info_sidebar = Control(
            children=[group_name_input],
        )

        with self.assertRaises(RuntimeError):
            validate_group_name(
                info_sidebar,
                "Калибровка #CAL-0001",
            )


class ValidateLastMessageTests(unittest.TestCase):
    @patch(
        "app.viber.validate_last_message."
        "chat_message_id_pattern",
        r"^chat-message$",
    )
    def test_correct_last_message(self):
        older_message_text = Control(
            text="Старо съобщение",
        )
        newest_message_text = Control(
            text="ТЕСТ НА VIBER AUTOMATION",
        )

        older_message = Control(
            automation_id="chat-message",
            bottom=100,
            children=[older_message_text],
        )
        newest_message = Control(
            automation_id="chat-message",
            bottom=200,
            children=[newest_message_text],
        )

        chat_pane = Control(
            children=[
                older_message,
                newest_message,
            ],
        )

        result = validate_last_message(
            chat_pane,
            "ТЕСТ НА VIBER AUTOMATION",
        )

        self.assertEqual(
            result,
            "ТЕСТ НА VIBER AUTOMATION",
        )

    @patch(
        "app.viber.validate_last_message."
        "chat_message_id_pattern",
        r"^chat-message$",
    )
    def test_wrong_last_message(self):
        newest_message_text = Control(
            text="Грешно съобщение",
        )
        newest_message = Control(
            automation_id="chat-message",
            bottom=200,
            children=[newest_message_text],
        )
        chat_pane = Control(
            children=[newest_message],
        )

        with self.assertRaises(RuntimeError):
            validate_last_message(
                chat_pane,
                "ТЕСТ НА VIBER AUTOMATION",
            )


if __name__ == "__main__":
    unittest.main()