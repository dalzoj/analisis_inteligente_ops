from fastapi import FastAPI
 
app = FastAPI(
    title="Análisis Inteligente Operaciones",
    description="Sistema basado en IA que democratiza acceso a estos datos e información, y automatiza la generación de insights accionables.",
    version="1.0.0",
)
 
@app.get("/health")
async def health_check():
    return {"status": "ok"}