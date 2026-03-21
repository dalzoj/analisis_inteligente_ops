from fastapi import APIRouter, HTTPException
from src.services import chat_service
from src.models.chat_models import ChatRequestBasic, ChatResponse
 
router = APIRouter(prefix="/chat")


@router.get("/health")
async def health():
    print('INFO: /health')
    return {"status": "ok"}


@router.post("/request")
async def ask(request: ChatRequestBasic):
    print('INFO: /request')

    try:
        response = await chat_service.get_basic_answer(
            question = request.question
        )

        return ChatResponse(
            answer = response["answer"],
            model = response["model"],
            tokens_in = response["tokens_in"],
            tokens_out = response["tokens_out"]
        )
 
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))