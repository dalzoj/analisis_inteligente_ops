from pydantic import BaseModel

class ChatRequestBasic(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    model: str
    tokens_in: int
    tokens_out: int