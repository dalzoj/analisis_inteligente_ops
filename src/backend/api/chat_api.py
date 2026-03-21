from fastapi import APIRouter, HTTPException
from src.backend.services import chat_service
from src.backend.models.chat_models import ChatRequest
from src.backend.models.response_models import Response
from src.backend.core.storage import save_response
 
router = APIRouter(prefix="/chat")


@router.get("/health")
async def health():
    print('INFO: Call /health')
    return {"status": "ok"}


@router.post("/basic_metrics_ops", response_model=Response)
async def ask_metrics_ops(request: ChatRequest):
    print('INFO: Call /basic_metrics_ops')

    try:
        if request.type_request == 'basic':
            result = await chat_service.get_basic_metrics_ops_answer(
                question = request.question,
            )

        response = Response(
            type_response = 'metricas_ops',
            mode = request.type_request,
            model_name = result["model_name"],
            tokens_in = result["tokens_in"],
            tokens_out = result["tokens_out"],
            answer = result["answer"],
        )

        save_response(response)

        return response
 
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))