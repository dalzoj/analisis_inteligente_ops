import httpx

BASE_URL = "http://localhost:8000"

TIMEOUT_CHAT = 90 
TIMEOUT_INSIGHTS = 180 


def send_question(question, mode="basic", history=None):
    payload = {
        "question": question,
        "type_request": mode,
        "history": history or [],
    }
    with httpx.Client(timeout=TIMEOUT_CHAT) as client:
        response = client.post(f"{BASE_URL}/chat/metrics_ops", json=payload)
        response.raise_for_status()
        return response.json()


def generate_insights(country, metrics, group_columns):

    payload: dict = {}
    
    if country:
        payload["country"] = country
    
    if metrics:
        payload["metrics"] = metrics
    
    if group_columns:
        payload["group_columns"] = group_columns

    with httpx.Client(timeout=TIMEOUT_INSIGHTS) as client:
        response = client.post(f"{BASE_URL}/insights/generate_report", json=payload)
        response.raise_for_status()
        return response.json()


def check_health():
    try:
        with httpx.Client(timeout=3) as client:
            r = client.get(f"{BASE_URL}/health")
            return r.status_code == 200
    except Exception:
        return False