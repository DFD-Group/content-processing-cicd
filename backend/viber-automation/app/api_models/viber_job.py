from datetime import date

from pydantic import BaseModel, Field


class CreateViberJobRequest(BaseModel):
    plate_size: str
    sign: str
    plate_count: int = Field(gt=0)
    dfd_order_number: str
    expedition_date: date

#Тук може са метне грешка заради датата