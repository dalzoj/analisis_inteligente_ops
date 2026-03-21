from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    type_request: str