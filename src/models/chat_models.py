from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    type_request: str


class ChatResponse(BaseModel):
    answer: str
    type_request: str
    model: str
    tokens_in: int
    tokens_out: int