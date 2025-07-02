from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import numpy as np
import cv2
import base64
from PIL import Image
import io

from app.core import state  

router = APIRouter()

model = YOLO("model/best.pt")

@router.post("/detect")
async def detect(file: UploadFile = File(...)):
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

        img_segmented = result.plot()
        img_pil_result = Image.fromarray(img_segmented)
        buffer = io.BytesIO()
        img_pil_result.save(buffer, format="JPEG")
        state.last_image_bytes = buffer.getvalue()

        resumen = (
            f"Se detectaron {len(detections)} objetos.\n"
            f"- Personas detectadas: {conteo.get('person', 0)}\n"
            f"- Personas con casco: {conteo.get('hard_hat', 0)}\n"
            f"- Personas con algo en la cabeza sin protección: {conteo.get('no_hard_hat', 0)}\n"
            f"- Personas sin nada en la cabeza: {conteo.get('no_head_wear', 0)}"
        )

        if conteo.get('hard_hat', 0) > conteo.get('person', 0):
            resumen += (
                "\n\n⚠️ Advertencia: Se detectaron más cascos que personas. "
                "Esto puede indicar un uso inadecuado del equipo de protección o errores en la detección."
            )

        state.last_summary_text = resumen

        return {
            "summary_text": resumen,
            "summary": conteo,
            "detections": detections,
            "image_base64": f"data:image/jpeg;base64,{base64.b64encode(state.last_image_bytes).decode('utf-8')}"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
