from __future__ import annotations

import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entities.base import Base

if TYPE_CHECKING:
    from app.entities.text_job import TextJob

class TextImage(Base):
    __tablename__ = "text_images"
    __table_args__ = {"schema": "app"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    image_path: Mapped[str] = mapped_column(
        Text,
        nullable=False)
    image_sha256: Mapped[str] = mapped_column(
        Text,
        nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    text_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app.text_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text_job: Mapped["TextJob"] = relationship(
        back_populates="images",
    )