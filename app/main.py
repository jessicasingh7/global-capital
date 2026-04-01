from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.chat import router as chat_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Global Capital")

# API routes first
app.include_router(chat_router)

# Serve pipeline-generated JSON data
app.mount("/data", StaticFiles(directory=BASE_DIR / "data"), name="data")

# Serve frontend (HTML, JS, CSS, static assets)
app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")
