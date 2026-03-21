from fastapi import APIRouter, HTTPException
from src.backend.services import insights_service
from src.backend.models.insights_models import InsightsRequest
from src.backend.models.response_models import Response
from src.backend.core.storage import save_response

router = APIRouter(prefix="/insights")


@router.get("/health")
async def health():
    print('INFO: Call /health')
    return {"status": "ok"}


@router.post("/generate_report", response_model=Response)
async def generate_report(request: InsightsRequest):
    print('INFO: Call /generate_report')
    
    try:
        result = await insights_service.generate(
            country = request.country,
            metrics = request.metrics,
            group_columns = request.group_columns
        )
    
        response = Response(
            type_response = 'reporte_ejecutivo',
            mode = 'basic',
            model_name = result["model_name"],
            tokens_in = result["tokens_in"],
            tokens_out = result["tokens_out"],
            answer = result["answer"],
        )

        save_response(response)

        return response
 
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))