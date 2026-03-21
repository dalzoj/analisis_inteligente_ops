import subprocess
import sys
from threading import Thread

import uvicorn
from src.backend.main_backend import app


def start_streamlit():
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/frontend/main_frontend.py",
        "--server.port", "8501",
        "--server.headless", "true",
    ])


if __name__ == "__main__":
    streamlit_thread = Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()

    uvicorn.run("src.backend.main_backend:app", host="0.0.0.0", port=8000, reload=False)