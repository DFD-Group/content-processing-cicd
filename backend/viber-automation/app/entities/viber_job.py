import datetime
import uuid

from sqlalchemy import Date, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class ViberJob(Base):
    __tablename__ = "viber_jobs"
    __table_args__ = {"schema": "app"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    plate_size: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    plate_sign: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    plate_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    dfd_order_number: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    customer_order_number: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    expedition_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )
    message_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    sent_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )