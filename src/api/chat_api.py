from fastapi import APIRouter, HTTPException
from src.services import chat_service
from src.models.chat_models import ChatRequest, ChatResponse
 
router = APIRouter(prefix="/chat")


@router.get("/health")
async def health():
    print('INFO: /health')
    return {"status": "ok"}


@router.post("/request")
async def ask(request: ChatRequest):
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


@router.post("/basic_metrics_ops")
async def ask_metrics_ops(request: ChatRequest):
    print('INFO: /basic_metrics_ops')

    try:
        if request.type_request == 'basic':
            response = await chat_service.get_basic_metrics_ops_answer(
                question = request.question,
            )

        return ChatResponse(
            answer = response["answer"],
            model = response["model"],
            tokens_in = response["tokens_in"],
            tokens_out = response["tokens_out"],
            type_request = request.type_request
        )
 
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))