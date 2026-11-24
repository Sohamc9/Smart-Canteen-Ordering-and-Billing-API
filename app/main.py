import os
from pathlib import Path
from fastapi import FastAPI
from app.logic import CanteenService
from app.routes import build_router
from app.storage import JsonStore

DATA_DIR = Path(os.environ.get("CANTEEN_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
service = CanteenService(JsonStore(DATA_DIR / "menu.json", []), JsonStore(DATA_DIR / "orders.json", []))
app = FastAPI(title="Smart Canteen Ordering and Billing API", version="1.0.0", description="Teaching prototype; no real payment processing.")
app.include_router(build_router(service), prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
