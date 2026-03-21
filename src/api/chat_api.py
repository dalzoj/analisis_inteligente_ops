from fastapi import APIRouter, HTTPException
from src.services import chat_service
from src.models.chat_models import ChatRequest
from src.models.response_models import Response
 
router = APIRouter(prefix="/chat")


@router.get("/health")
async def health():
    print('INFO: /health')
    return {"status": "ok"}


@router.post("/basic_metrics_ops")
async def ask_metrics_ops(request: ChatRequest):
    print('INFO: /basic_metrics_ops')

    try:
        if request.type_request == 'basic':
            result = await chat_service.get_basic_metrics_ops_answer(
                question = request.question,
            )

        return Response(
            type_response = 'metricas_ops',
            mode = request.type_request,
            model = result["model"],
            tokens_in = result["tokens_in"],
            tokens_out = result["tokens_out"],
            answer = result["answer"],
        )
 
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))