import os
import unittest
import uuid
from datetime import date
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError


os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://localhost/test",
)

from app.api_models import (  # noqa: E402
    CreateViberJobRequest,
)
from app.main import (  # noqa: E402
    create_viber_job,
    send_viber_message,
)


class FakeSession:
    def __init__(self):
        self.job = None
        self.commit_count = 0

    def add(self, job):
        self.job = job

    def commit(self):
        self.commit_count += 1

    def refresh(self, job):
        if job.id is None:
            job.id = uuid.uuid4()


def create_request():
    return CreateViberJobRequest(
        chat_name="Калибровка #CAL-0001",
        plate_size="100x200",
        sign="TEST",
        plate_count=2,
        dfd_order_number="DFD-TEST",
        customer_order_number="CUSTOMER-TEST",
        expedition_date=date(2026, 10, 21),
        message_text="Тестово Viber съобщение.",
    )


class ViberClientFallbackTests(
    unittest.TestCase
):
    @patch(
        "app.main.backup_viber_client"
    )
    @patch(
        "app.main.primary_viber_client"
    )
    def test_primary_client_succeeds(
        self,
        primary_viber_client,
        backup_viber_client,
    ):
        result = send_viber_message(
            "Test chat",
            "Test message",
        )

        primary_viber_client.assert_called_once_with(
            "Test chat",
            "Test message",
        )

        backup_viber_client.assert_not_called()

        self.assertEqual(
            result,
            "primary",
        )

    @patch(
        "app.main.backup_viber_client"
    )
    @patch(
        "app.main.primary_viber_client",
        side_effect=RuntimeError(
            "Primary failure."
        ),
    )
    def test_backup_is_used_when_primary_fails(
        self,
        primary_viber_client,
        backup_viber_client,
    ):
        result = send_viber_message(
            "Test chat",
            "Test message",
        )

        primary_viber_client.assert_called_once_with(
            "Test chat",
            "Test message",
        )

        backup_viber_client.assert_called_once_with(
            "Test chat",
            "Test message",
        )

        self.assertEqual(
            result,
            "backup",
        )

    @patch(
        "app.main.backup_viber_client",
        side_effect=RuntimeError(
            "Backup failure."
        ),
    )
    @patch(
        "app.main.primary_viber_client",
        side_effect=RuntimeError(
            "Primary failure."
        ),
    )
    def test_error_when_both_clients_fail(
        self,
        primary_viber_client,
        backup_viber_client,
    ):
        with self.assertRaises(
            RuntimeError
        ) as context:
            send_viber_message(
                "Test chat",
                "Test message",
            )

        primary_viber_client.assert_called_once_with(
            "Test chat",
            "Test message",
        )

        backup_viber_client.assert_called_once_with(
            "Test chat",
            "Test message",
        )

        self.assertEqual(
            str(context.exception),
            "Backup failure.",
        )


class CreateViberJobTests(unittest.TestCase):
    @patch(
        "app.main.send_viber_message",
        return_value="primary",
    )
    def test_successful_job_uses_request_message(
        self,
        send_viber_message_mock,
    ):
        session = FakeSession()
        request = create_request()

        response = create_viber_job(
            data=request,
            session=session,
        )

        send_viber_message_mock.assert_called_once_with(
            request.chat_name,
            request.message_text,
        )

        self.assertEqual(
            response.status,
            "sent",
        )

        self.assertEqual(
            response.chat_name,
            request.chat_name,
        )

        self.assertEqual(
            response.message,
            (
                "Viber message sent successfully "
                "using the primary client."
            ),
        )

        self.assertEqual(
            session.job.message_text,
            request.message_text,
        )

        self.assertEqual(
            session.job.status,
            "sent",
        )

        self.assertIsNotNone(
            session.job.sent_at,
        )

        self.assertEqual(
            session.commit_count,
            2,
        )

    @patch(
        "app.main.send_viber_message",
        side_effect=RuntimeError(
            "Simulated Viber failure."
        ),
    )
    def test_failed_job_is_recorded(
        self,
        send_viber_message_mock,
    ):
        session = FakeSession()
        request = create_request()

        with self.assertRaises(
            HTTPException
        ) as context:
            create_viber_job(
                data=request,
                session=session,
            )

        send_viber_message_mock.assert_called_once_with(
            request.chat_name,
            request.message_text,
        )

        self.assertEqual(
            context.exception.status_code,
            500,
        )

        self.assertEqual(
            session.job.status,
            "failed",
        )

        self.assertEqual(
            session.job.error_message,
            "Simulated Viber failure.",
        )

        self.assertEqual(
            session.commit_count,
            2,
        )

    def test_message_text_is_required(self):
        request_data = {
            "chat_name": (
                "Калибровка #CAL-0001"
            ),
            "plate_size": "100x200",
            "sign": "TEST",
            "plate_count": 2,
            "dfd_order_number": "DFD-TEST",
            "customer_order_number": (
                "CUSTOMER-TEST"
            ),
            "expedition_date": "2026-10-21",
        }

        with self.assertRaises(
            ValidationError
        ):
            CreateViberJobRequest(
                **request_data
            )

    def test_empty_message_text_is_rejected(
        self,
    ):
        request_data = {
            "chat_name": (
                "Калибровка #CAL-0001"
            ),
            "plate_size": "100x200",
            "sign": "TEST",
            "plate_count": 2,
            "dfd_order_number": "DFD-TEST",
            "customer_order_number": (
                "CUSTOMER-TEST"
            ),
            "expedition_date": "2026-10-21",
            "message_text": "",
        }

        with self.assertRaises(
            ValidationError
        ):
            CreateViberJobRequest(
                **request_data
            )


if __name__ == "__main__":
    unittest.main()