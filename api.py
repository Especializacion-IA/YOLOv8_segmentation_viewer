from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from ultralytics import YOLO
import numpy as np
import cv2
import base64
from PIL import Image
import io

app = FastAPI()

# Carga del modelo de segmentación
model = YOLO("model/best.pt")

last_image_bytes = None
last_summary_text = ""

COLOR_MAP = {
    "person": (0, 0, 255),
    "hard_hat": (0, 255, 0),
    "no_hard_hat": (0, 165, 255),
    "no_head_wear": (0, 0, 139),
}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    global last_image_bytes, last_summary_text

    try:
        image_bytes = await file.read()
        image_np = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        results = model(img_array, conf=0.39)
        result = results[0]

        boxes = result.boxes
        names = model.names

        if boxes is None or len(boxes) == 0:
            return JSONResponse(content={
                "summary_text": "⚠️ No se reconocieron objetos.",
                "summary": {},
                "detections": [],
                "image_base64": ""
            })

        detections = []
        conteo = {"person": 0, "hard_hat": 0, "no_hard_hat": 0, "no_head_wear": 0}

        for box in boxes:
            conf = float(box.conf)
            if conf <= 0.39:
                continue

            class_id = int(box.cls)
            class_name = names[class_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append({
                "class": class_name,
                "confidence": round(conf, 2),
                "bbox": [x1, y1, x2, y2]
            })
            conteo[class_name] = conteo.get(class_name, 0) + 1

        if not detections:
            return JSONResponse(content={
                "summary_text": "⚠️ No se detectaron objetos con confianza >= 0.39.",
                "summary": {},
                "detections": [],
                "image_base64": ""
            })

        # 🖼 Dibujar segmentación
        img_segmented = result.plot()

        img_pil_result = Image.fromarray(img_segmented)
        buffer = io.BytesIO()
        img_pil_result.save(buffer, format="JPEG")
        last_image_bytes = buffer.getvalue()

        # 📊 Resumen
        resumen = (
            f"Se detectaron {len(detections)} objetos.\n"
            f"- Personas detectadas: {conteo.get('person', 0)}\n"
            f"- Personas con casco: {conteo.get('hard_hat', 0)}\n"
            f"- Personas con algo en la cabeza sin protección: {conteo.get('no_hard_hat', 0)}\n"
            f"- Personas sin nada en la cabeza: {conteo.get('no_head_wear', 0)}"
        )

        # ⚠️ Verificación adicional
        if conteo.get('hard_hat', 0) > conteo.get('person', 0):
            resumen += (
                "\n\n⚠️ Advertencia: Se detectaron más cascos que personas. "
                "Esto puede indicar un uso inadecuado del equipo de protección o errores en la detección."
            )

        last_summary_text = resumen

        return {
            "summary_text": resumen,
            "summary": conteo,
            "detections": detections,
            "image_base64": f"data:image/jpeg;base64,{base64.b64encode(last_image_bytes).decode('utf-8')}"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/image")
def get_last_image():
    if not last_image_bytes:
        return JSONResponse(status_code=404, content={"error": "No hay imagen procesada aún."})

    base64_img = base64.b64encode(last_image_bytes).decode("utf-8")
    html = f"""
    <html>
        <head><title>Imagen Detectada</title></head>
        <body style="font-family:sans-serif;">
            <h2>Última imagen procesada</h2>
            <img src="data:image/jpeg;base64,{base64_img}" alt="Imagen detectada"
                 style="width:640px; border:1px solid #ccc; object-fit:contain;" />
        </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/", response_class=HTMLResponse)
def home():
    if not last_summary_text:
        resumen = "<p><i>No hay imagen procesada aún.</i></p>"
    else:
        resumen = f"""
        <h3>Resumen de la última imagen:</h3>
        <pre style='background:#f4f4f4; padding:10px; border-radius:8px;'>{last_summary_text}</pre>
        """

    html = f"""
    <html>
        <head><title>YOLOv8 Detección</title></head>
        <body style="font-family:sans-serif; text-align:center; padding:40px;">
            <h1>🚧 Análisis de Casco con YOLOv8 (Segmentación)</h1>
            <p>Usa los siguientes botones para interactuar con la API:</p>
            <a href="/docs" style="padding: 10px 20px; background: #0b5ed7; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Abrir Swagger</a>
            <a href="/image" style="padding: 10px 20px; background: #198754; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Ver Imagen Procesada</a>
            <hr style="margin:40px 0;">
            {resumen}
        </body>
    </html>
    """
    return HTMLResponse(content=html)
