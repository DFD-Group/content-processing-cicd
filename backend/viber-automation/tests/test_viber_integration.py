import os
import platform
import unittest


RUN_INTEGRATION_TEST = (
    os.getenv("RUN_VIBER_INTEGRATION") == "1"
)

IS_WINDOWS = platform.system() == "Windows"


@unittest.skipUnless(
    IS_WINDOWS,
    "Viber UI automation is supported only on Windows.",
)
@unittest.skipUnless(
    RUN_INTEGRATION_TEST,
    "Set RUN_VIBER_INTEGRATION=1 to run this test.",
)
class ViberIntegrationTests(unittest.TestCase):
    def test_send_real_viber_message(self):
        from app.viber_client import (
            prepare_viber_message,
        )

        chat_name = os.getenv(
            "VIBER_TEST_CHAT",
            "Калибровка #CAL-0001",
        )
        message_text = os.getenv(
            "VIBER_TEST_MESSAGE",
            "ТЕСТ НА VIBER AUTOMATION",
        )

        prepare_viber_message(
            chat_name,
            message_text,
        )


if __name__ == "__main__":
    unittest.main()