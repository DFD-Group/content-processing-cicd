from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TextImageResponse(BaseModel):
    id: UUID
    image_path: str
    image_sha256: str
    created_at: datetime
    text_job_id: UUID

    model_config = {"from_attributes": True}