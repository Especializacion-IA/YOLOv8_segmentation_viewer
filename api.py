from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from ultralytics import YOLO
import numpy as np
import cv2
import base64
from PIL import Image

app = FastAPI()


model = YOLO("model/best.pt")  


last_image_bytes = None
last_summary_text = ""


def encode_image(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode("utf-8")


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    global last_image_bytes, last_summary_text

    image_bytes = await file.read()
    img_pil = Image.open(file.file).convert("RGB")
    img_array = np.array(img_pil)
    height, width = img_array.shape[:2]

    
    results = model.predict(source=img_array, conf=0.3, task="segment", save=False)
    result = results[0]
    masks = result.masks
    boxes = result.boxes
    names = model.names

    mask_overlay = np.zeros_like(img_array, dtype=np.uint8)
    detections = []
    conteo = {"hard_hat": 0, "no_hard_hat": 0, "no_head_wear": 0, "person": 0}

    if masks is not None and boxes is not None:
        for i, (mask, box) in enumerate(zip(masks.data, boxes.xyxy)):
            conf = float(boxes.conf[i])
            if conf < 0.3:
                continue

            binary_mask = mask.cpu().numpy()
            resized_mask = cv2.resize(binary_mask, (width, height))
            color = np.random.randint(0, 255, size=3)

            for c in range(3):
                mask_overlay[:, :, c] += (resized_mask * color[c]).astype(np.uint8)

            class_id = int(boxes.cls[i])
            class_name = names[class_id]
            x1, y1, _, _ = box.cpu().numpy().astype(int)

            cv2.putText(mask_overlay, class_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            conteo[class_name] = conteo.get(class_name, 0) + 1
            detections.append({
                "class": class_name,
                "confidence": round(conf, 2),
                "bbox": box.cpu().numpy().tolist()
            })

        
        combined = cv2.addWeighted(img_array, 0.6, mask_overlay, 0.4, 0)
        _, buffer = cv2.imencode('.jpg', combined)
        last_image_bytes = buffer.tobytes()

    
        resumen = (
            f"Se detectaron {len(detections)} objetos.\n"
            f"- Personas detectadas: {conteo.get('person', 0)}\n"
            f"- Con casco (hard_hat): {conteo.get('hard_hat', 0)}\n"
            f"- Con algo sin protección (no_hard_hat): {conteo.get('no_hard_hat', 0)}\n"
            f"- Sin nada en la cabeza (no_head_wear): {conteo.get('no_head_wear', 0)}"
        )

        last_summary_text = resumen

        return {
            "summary_text": resumen,
            "summary": conteo,
            "detections": detections,
            "image_base64": f"data:image/jpeg;base64,{base64.b64encode(last_image_bytes).decode('utf-8')}"
        }

    return JSONResponse(content={
        "summary_text": "⚠️ No se encontraron objetos.",
        "summary": {},
        "detections": [],
        "image_base64": ""
    })


@app.get("/image")
def get_last_image():
    if not last_image_bytes:
        return JSONResponse(status_code=404, content={"error": "No hay imagen procesada aún."})

    base64_img = base64.b64encode(last_image_bytes).decode("utf-8")
    html = f"""
    <html>
        <head><title>Imagen Segmentada</title></head>
        <body style="font-family:sans-serif;">
            <h2>Última imagen segmentada</h2>
            <img src="data:image/jpeg;base64,{base64_img}" alt="Segmentación" style="max-width:100%; border:1px solid #ccc;" />
        </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/", response_class=HTMLResponse)
def home():
    if not last_image_bytes:
        resumen = "<p><i>No hay imagen procesada aún.</i></p>"
    else:
        resumen = f"""
        <h3>Resumen de la última imagen:</h3>
        <pre style='background:#f4f4f4; padding:10px; border-radius:8px;'>{last_summary_text}</pre>
        """

    html = f"""
    <html>
        <head><title>YOLOv8 Segmentación</title></head>
        <body style="font-family:sans-serif; text-align:center; padding:40px;">
            <h1>🚧 Segmentador de Casco YOLOv8</h1>
            <p>Usa los siguientes botones para interactuar con la API:</p>
            <a href="/docs" style="padding: 10px 20px; background: #0b5ed7; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Abrir Swagger (/docs)</a>
            <a href="/image" style="padding: 10px 20px; background: #198754; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Ver Última Imagen</a>
            <hr style="margin:40px 0;">
            {resumen}
        </body>
    </html>
    """
    return html
