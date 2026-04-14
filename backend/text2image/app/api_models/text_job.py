from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.api_models.text_image import TextImageResponse

class TextJobRequest(BaseModel):
    prompt: str

class TextJobResponse(BaseModel):
    id: UUID
    prompt: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    images: list[TextImageResponse]

    model_config = {"from_attributes": True}