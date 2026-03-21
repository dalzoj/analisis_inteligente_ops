from pydantic import BaseModel

class ChatRequestBasic(BaseModel):
    question: str