from pydantic import BaseModel

class InsightsRequest(BaseModel):
    country: str | None = None
    metrics: list[str] | None = None