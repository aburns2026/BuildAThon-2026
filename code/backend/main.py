from datetime import datetime
from fastapi import FastAPI

app = FastAPI(title="BuildAThon 2026 MVP API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
