from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    id: int
    text: str
    # not a proper datetime because we just propagate it
    timestamp: str
    report_id: Optional[int] = None


class Report(BaseModel):
    id: int
    name: str
    credit_cost: float


class Usage(BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    credits_used: float
