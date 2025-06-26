from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from ultralytics import YOLO
import numpy as np
import cv2
import base64
from PIL import Image

app = FastAPI()

# Carga del modelo
model = YOLO("model/best1.pt")

last_image_bytes = None
last_summary_text = ""

# Colores por clase
COLOR_MAP = {
    "person": (0, 0, 255),         # Rojo
    "hard_hat": (0, 255, 0),       # Verde
    "no_hard_hat": (0, 165, 255),  # Naranja
    "no_head_wear": (0, 0, 139),   # Azul oscuro
}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    global last_image_bytes, last_summary_text

    try:
        image_bytes = await file.read()
        img_pil = Image.open(file.file).convert("RGB")
        img_array = np.array(img_pil)

        # 🔍 Inferencia con umbral de confianza
        results = model(img_array, conf=0.35)
        result = results[0]
        boxes = result.boxes
        names = model.names

        if boxes is None:
            return JSONResponse(content={
                "summary_text": "⚠️ No se reconocieron objetos.",
                "summary": {},
                "detections": [],
                "image_base64": ""
            })

        detections = []
        conteo = {"person": 0, "hard_hat": 0, "no_hard_hat": 0, "no_head_wear": 0}

        for i, box in enumerate(boxes):
            conf = float(box.conf)
            if conf < 0.35:
                continue

            class_id = int(box.cls)
            class_name = names[class_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            color = COLOR_MAP.get(class_name, (255, 255, 255))
            cv2.rectangle(img_array, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_array, f"{class_name} {conf:.2f}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            detections.append({
                "class": class_name,
                "confidence": round(conf, 2),
                "bbox": [x1, y1, x2, y2]
            })
            conteo[class_name] = conteo.get(class_name, 0) + 1

        if not detections:
            return JSONResponse(content={
                "summary_text": "⚠️ No se detectaron objetos con confianza >= 0.3.",
                "summary": {},
                "detections": [],
                "image_base64": ""
            })

        # 🖼️ Codificar imagen
        _, buffer = cv2.imencode('.jpg', img_array)
        last_image_bytes = buffer.tobytes()

        # 📊 Resumen en texto plano
        resumen = (
            f"Se detectaron {len(detections)} objetos.\n"
            f"- Personas detectadas: {conteo.get('person', 0)}\n"
            f"- Personas con casco: {conteo.get('hard_hat', 0)}\n"
            f"- Personas con algo en la cabeza sin protección: {conteo.get('no_hard_hat', 0)}\n"
            f"- Personas sin nada en la cabeza: {conteo.get('no_head_wear', 0)}"
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
            <img src="data:image/jpeg;base64,{base64_img}" alt="Imagen detectada" style="max-width:100%; border:1px solid #ccc;" />
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
            <h1>🚧 Análisis de Casco con YOLOv8</h1>
            <p>Usa los siguientes botones para interactuar con la API:</p>
            <a href="/docs" style="padding: 10px 20px; background: #0b5ed7; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Abrir Swagger</a>
            <a href="/image" style="padding: 10px 20px; background: #198754; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Ver Imagen Detectada</a>
            <hr style="margin:40px 0;">
            {resumen}
        </body>
    </html>
    """
    return HTMLResponse(content=html)
