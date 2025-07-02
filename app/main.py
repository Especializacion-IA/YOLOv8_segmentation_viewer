from fastapi import FastAPI
from app.routes.view import router as view_router
from app.routes.detect import router as detect_router

app = FastAPI()

app.include_router(view_router)
app.include_router(detect_router)
