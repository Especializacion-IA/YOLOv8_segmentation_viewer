🛠️ YOLOv8 FastAPI Backend - Detección de Casco con Segmentación
Este proyecto ofrece una API construida con FastAPI que utiliza un modelo entrenado con YOLOv8 para detectar:

👷 Personas

⛑️ Cascos de seguridad (hard_hat)

👒 Objetos en la cabeza sin protección (no_hard_hat)

🙆‍♂️ Personas sin nada en la cabeza (no_head_wear)

🚀 Requisitos
Python 3.8 o superior

🔧 Instalación manual de dependencias:

bash

pip install ultralytics fastapi uvicorn opencv-python numpy pillow

O bien, ejecuta requirements.txt con:

bash

pip install -r requirements.txt


📁 ESTRUCTURA DEL PROYECTO

YOLOv8_SEGMENTATION_VIEWER/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── __init__.py
│   ├── core/
│   │   ├── model.py             # Carga del modelo YOLO
│   │   └── state.py             # Variables compartidas (estado global)
│   ├── routes/
│   │   ├── detect.py            # Endpoint POST /detect
│   │   └── view.py              # Endpoints GET /, /image
│   └── utils/
│       └── image_handler.py     # Utilidades de manejo de imágenes
├── model/
│   └── best.pt                  # Modelo YOLOv8 de segmentación
├── requirements.txt
└── README.md


▶️ COMO EJECUTAR EL SERVIDOR

Desde la raíz del proyecto, ejecuta:

bash

uvicorn app.main:app --reload
Esto iniciará la API en:

Página resumen: http://localhost:8000/

Swagger UI: http://localhost:8000/docs

Imagen procesada: http://localhost:8000/image


📡 ENDPOINTS DISPONIBLES:

🔍 POST /detect
Envía una imagen y devuelve:

Detecciones con: clase, confianza, bounding box

Imagen segmentada codificada en base64

Resumen textual y numérico

Verificación si hay más cascos que personas

Ejemplo con curl:

bash

curl -X 'POST' \
  'http://localhost:8000/detect' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@ruta/a/una/imagen.jpg'
🖼 GET /image
Devuelve una página HTML que muestra la última imagen procesada con segmentación aplicada.

🏠 GET /
Muestra un resumen textual de la última inferencia y enlaces a Swagger e imagen segmentada.

📑 GET /docs
Abre la interfaz Swagger generada automáticamente por FastAPI.

🧠 Notas para el desarrollador Frontend
El frontend debe enviar imágenes al endpoint /detect como multipart/form-data bajo el campo file.

La respuesta incluye:

"image_base64": para incrustar directamente en un <img src="...">

"summary_text": resumen en texto plano

"summary": conteo por clase

La lógica incluye una advertencia si hay más cascos detectados que personas.