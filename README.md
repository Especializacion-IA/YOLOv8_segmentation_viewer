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

project/
├── app/
│   ├── main.py               # Punto de entrada de la aplicación FastAPI
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── detect.py         # Lógica de detección
│   │   └── view.py           # Rutas de vista y resumen
│   └── model/
│       └── best.pt           # Modelo entrenado YOLOv8 (segmentación)
├── requirements.txt
└── README.md
▶️ Cómo ejecutar el servidor

Desde la raíz del proyecto, ejecuta:

bash

uvicorn app.main:app --reload
Esto iniciará la API en:

Swagger UI: http://localhost:8000/docs

Página resumen: http://localhost:8000/

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