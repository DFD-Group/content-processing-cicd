import uuid
from datetime import date

from pydantic import BaseModel, Field


class CreateViberJobRequest(BaseModel):
    chat_name: str = Field(min_length=1, max_length=100)
    plate_size: str = Field(max_length=32)
    sign: str = Field(max_length=64)
    plate_count: int = Field(gt=0)
    dfd_order_number: str = Field(max_length=32)
    customer_order_number: str = Field(max_length=32)
    expedition_date: date
    message_text: str = Field(min_length=1)


class CreateViberJobResponse(BaseModel):
    id: uuid.UUID
    status: str
    chat_name: str
    message: str