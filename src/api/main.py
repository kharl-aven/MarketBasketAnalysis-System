from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Pokemon Cafe MBA API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/rules")
def get_rules():
    return {"rules": []}

@app.get("/recommendations")
def get_recommendations():
    return {"recommendations": {}}

@app.get("/drift-report")
def get_drift():
    return {"drift_detected": False}

@app.post("/rollback")
def rollback(body: dict):
    return {"rolled_back_to": body.get("version")}
