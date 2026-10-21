import unittest
from unittest.mock import patch

from app.viber_client import (
    escape_for_send_keys,
    wait_until_rectangle_is_stable,
)


class Rectangle:
    def __init__(
        self,
        left,
        top,
        right,
        bottom,
    ):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


class Control:
    def __init__(self, rectangles):
        self.rectangles = list(rectangles)
        self.last_rectangle = self.rectangles[-1]

    def rectangle(self):
        if self.rectangles:
            self.last_rectangle = self.rectangles.pop(0)

        return self.last_rectangle


class ViberClientHelperTests(unittest.TestCase):
    def test_wait_until_rectangle_is_stable(
        self,
    ):
        moving_rectangle = Rectangle(
            0,
            0,
            100,
            100,
        )
        stable_rectangle = Rectangle(
            10,
            10,
            110,
            110,
        )

        control = Control(
            [
                moving_rectangle,
                stable_rectangle,
                stable_rectangle,
                stable_rectangle,
                stable_rectangle,
            ]
        )

        result = wait_until_rectangle_is_stable(
            control,
            timeout=1,
            interval=0,
            required_stable_checks=3,
        )

        self.assertIs(result, stable_rectangle)

    def test_wait_until_rectangle_raises_timeout(
        self,
    ):
        control = Control(
            [
                Rectangle(0, 0, 100, 100),
            ]
        )

        with (
            patch(
                "app.viber_client.time.time",
                side_effect=[0, 0, 1],
            ),
            patch(
                "app.viber_client.time.sleep",
            ),
        ):
            with self.assertRaises(TimeoutError):
                wait_until_rectangle_is_stable(
                    control,
                    timeout=0.5,
                    interval=0.15,
                )

    def test_escape_for_send_keys(
        self,
    ):
        result = escape_for_send_keys(
            "A+B%",
        )

        self.assertEqual(
            result,
            "A{+}B{%}",
        )


if __name__ == "__main__":
    unittest.main()