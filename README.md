# Sistema de Análisis Inteligente

Sistema basado en IA que democratiza acceso a estos datos e información, y automatiza la generación de insights accionables.
---

## Requisitos

- Python 3.10+
- API Key de Anthropic

## Instalación

**1. Crea y activa un entorno virtual**
```bash
# Crear el entorno virtual
python -m venv .venv

# Activar en macOS/Linux
source .venv/bin/activate

# Activar en Windows
.venv\Scripts\activate
```

**2. Instala las dependencias**
```bash
pip install -r requirements.txt
```

**3. Configura las variables de entorno**

Crea un archivo `.env` en la raíz del proyecto:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Configuración

Edita `config/config.cfg` para ajustar el modelo, la ventana de memoria y los umbrales de detección de insights.

## Ejecución

```bash
python app.py
```

- **Frontend (Streamlit):** http://localhost:8501
- **Backend (FastAPI):** http://localhost:8000

## Estructura

```
├── app.py                  # Punto de entrada
├── config/config.cfg       # Configuración general
├── data/                   # CSVs de métricas y órdenes
├── prompts/                # Prompts del LLM
├── src/
│   ├── backend/
│   │   ├── api/            # Endpoints FastAPI
│   │   ├── core/           # Ejecutor de código, data loader, storage
│   │   ├── insights/       # Detección de anomalías, tendencias, benchmark, correlaciones
│   │   ├── llm/            # Cliente LLM (Anthropic)
│   │   └── services/       # Lógica de negocio del chat e insights
│   └── frontend/
│       └── pages/          # Páginas Streamlit (chat, reporte)
└── tests/
    └── pricing.py          # Cálculo de costos de tokens
```

## Costo estimado

Ver `tests/pricing.py` para calcular el costo acumulado según los tokens consumidos.