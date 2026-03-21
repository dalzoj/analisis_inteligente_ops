from fastapi import FastAPI
from src.api import chat_api, insights_api
 
app = FastAPI(
    title="Análisis Inteligente Operaciones",
    description="Sistema basado en IA que democratiza acceso a estos datos e información, y automatiza la generación de insights accionables.",
    version="1.0.0",
)

app.include_router(chat_api.router)
app.include_router(insights_api.router)
 
@app.get("/health")
async def health_check():
    return {"status": "ok"}