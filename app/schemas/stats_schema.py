from datetime import datetime
from pydantic import BaseModel


class VisitCreate(BaseModel):
    page_url: str


class StatisticsResponse(BaseModel):
    id: int
    user_id: int | None
    page_url: str
    timestamp: datetime
