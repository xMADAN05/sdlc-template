from pydantic import BaseModel, Field
from typing import Optional

class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    status: str
