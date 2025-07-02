# 🛠️ YOLOv8 FastAPI Backend - Detección de Casco con Segmentación

Este proyecto proporciona una API construida con **FastAPI** que utiliza un modelo de **YOLOv8 segmentación** entrenado para detectar:

- Personas
- Cascos de seguridad (`hard_hat`)
- Personas con objetos en la cabeza sin protección (`no_hard_hat`)
- Personas sin nada en la cabeza (`no_head_wear`)

---

## 🚀 Requisitos

- Python 3.8 o superior
- Paquetes: `ultralytics`, `opencv-python`, `fastapi`, `pillow`, `uvicorn`, `numpy`

Instala las dependencias con:

```bash
pip install -r requirements.txt
```



## 📁 Estructura de archivos

```
project/
├── api.py                   # Código principal para levantar la API
├── main.py                  # Script para pruebas locales con visualización
├── model/
│   └── best.pt              # Modelo YOLOv8 entrenado con segmentación
├── requirements.txt
└── README.md



---

## ▶️ Cómo ejecutar el servidor

Desde la raíz del proyecto, ejecuta:

```bash
uvicorn api:app --reload
```

Esto levantará la API en:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Página resumen: [http://localhost:8000/](http://localhost:8000/)
- Imagen procesada: [http://localhost:8000/image](http://localhost:8000/image)

---

## ▶️ Endpoints disponibles

### 🔍 `POST /detect`

Sube una imagen y devuelve:

- Lista de detecciones con: clase, confianza, coordenadas
- Imagen segmentada codificada en base64
- Resumen textual y numérico

**Ejemplo con `curl`:**

```bash
curl -X 'POST' \
  'http://localhost:8000/detect' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@ruta/a/una/imagen.jpg'
```

---

### 🖼 `GET /image`

Devuelve una página HTML que muestra la **última imagen procesada** con segmentación aplicada.

---

### 🏠 `GET /`

Página HTML con resumen textual y enlace para visualizar la imagen segmentada.

---

### 📑 `GET /docs`

Interfaz Swagger (auto-generada por FastAPI) para probar y documentar la API desde el navegador.

---

## 🧠 Notas para el desarrollador Frontend

- El frontend debe enviar imágenes a `/detect` como `multipart/form-data` bajo el campo `file`.
- La respuesta incluye la imagen procesada como `image_base64`, útil para mostrar directamente en el frontend con `<img src="..." />`.
- También se devuelve un resumen textual (`summary_text`) y un conteo por clase (`summary`).

---


