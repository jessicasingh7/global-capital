from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Capital — Where All the Money Is")

# Serve pipeline-generated JSON data
app.mount("/data", StaticFiles(directory=BASE_DIR / "data"), name="data")

# Serve frontend (HTML, JS, CSS, static assets)
app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")
