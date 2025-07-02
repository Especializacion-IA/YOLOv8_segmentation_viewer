from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import base64

from app.core import state

router = APIRouter()

@router.get("/image")
def get_last_image():
    if state.last_image_bytes is None:
        return JSONResponse(status_code=404, content={"error": "No hay imagen procesada aún."})

    base64_img = base64.b64encode(state.last_image_bytes).decode("utf-8")
    html = f"""
    <html>
        <body style="font-family:sans-serif;">
            <h2>Última imagen procesada</h2>
            <img src="data:image/jpeg;base64,{base64_img}" style="width:640px; border:1px solid #ccc;" />
        </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/", response_class=HTMLResponse)
def home():
    resumen = (
        "<p><i>No hay imagen procesada aún.</i></p>" if not state.last_summary_text else
        f"<h3>Resumen de la última imagen:</h3><pre style='background:#f4f4f4; padding:10px;'>{state.last_summary_text}</pre>"
    )

    html = f"""
    <html>
        <body style="font-family:sans-serif; text-align:center; padding:40px;">
            <h1>🚧 Detección con YOLOv8</h1>
            <a href="/docs" style="padding:10px; background:#0b5ed7; color:white; text-decoration:none; border-radius:5px;">Swagger</a>
            <a href="/image" style="padding:10px; background:#198754; color:white; text-decoration:none; border-radius:5px;">Ver Imagen</a>
            <hr style="margin:40px 0;">
            {resumen}
        </body>
    </html>
    """
    return HTMLResponse(content=html)
