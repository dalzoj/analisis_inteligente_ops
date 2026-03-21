from pydantic import BaseModel

class Response(BaseModel):
    type_response: str
    mode: str
    model_name: str
    tokens_in: int
    tokens_out: int
    answer: str