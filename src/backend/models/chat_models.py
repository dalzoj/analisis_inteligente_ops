from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    type_request: str
    history: list[dict] | None = None