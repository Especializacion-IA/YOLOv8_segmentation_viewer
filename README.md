# Prodity AI Risk Detection

# 🛠️ YOLOv8 FastAPI Backend - Detección de Casco con Segmentación

Este repositorio contiene la API de detección de riesgos laborales, construida con FastAPI, para el software Prodity de Grupo Espiral.

Utiliza un modelo YOLOv8 re-entrenado para analizar imágenes de entornos laborales, detectando personas y evaluando el uso de protección en la cabeza (cascos de seguridad, otros elementos o ausencia de estos).

## Clases Detectadas

El modelo ha sido entrenado para detectar las siguientes 4 clases:

👷  `person`: Personas en la imagen.

⛑️  `hard_hat`: Casco de seguridad en la cabeza de una persona.

👒  `no_hard_hat`: Algo en la cabeza de una persona que no es un casco de seguridad.

🙆‍♂️  `no_head_wear`: Ausencia de cualquier elemento en la cabeza de una persona.


## 📁 ESTRUCTURA DEL PROYECTO
```
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
```

## Uso

### 🚀 Requisitos

* Python 3.10 o superior
* `pip`

### 🔧 Clonar el repositorio:

```bash
git clone https://github.com/Especializacion-IA/YOLOv8_segmentation_viewer.git
cd YOLOv8_segmentation_viewer
```

### 🔧 Instalación manual de dependencias:

Comprueba si tienes `pip` instalado:

```bash
pip --version
```

Ejecuta requirements.txt con:

```
pip install -r requirements.txt
```

### ▶️ COMO EJECUTAR EL SERVIDOR

Desde la raíz del proyecto, ejecuta:

```bash

uvicorn app.main:app --reload
```
Esto iniciará la API a la que se accede en http://localhost:8000/

![image](https://github.com/user-attachments/assets/afb77c2c-a7ae-4c79-8103-47e22302b0ef)

Esto abrira el [Swagger UI](http://localhost:8000/docs), para cargar la imagen hacer clic en POST y después Try it out

![image](https://github.com/user-attachments/assets/584f8289-92ef-4e86-a0ee-b6f7d9c6308b)

En este punto se selecciona el archivo y se ejecuta:

![image](https://github.com/user-attachments/assets/fd93c2cc-e6a8-44ec-9523-90893afecd11)

Esto te devolvera todos los detalles de analisis de la imagen:

![Screenshot from 2025-07-02 19-56-16](https://github.com/user-attachments/assets/3b66cf74-3ea2-45f3-ad7e-8838a5447c76)

Para visualizar la imagen procesada accede a [aqui](http://localhost:8000/) donde aparece un resumen de la última imagen analizada y pulsa en Ver Imagen.

![Screenshot from 2025-07-03 09-22-08](https://github.com/user-attachments/assets/5d47358f-3bd1-4af4-b707-71ed2dd7880f)

![Screenshot from 2025-07-03 09-22-29](https://github.com/user-attachments/assets/8032a38d-cc3a-4e25-90d8-678ef0fa061d)

### 📡 ENDPOINTS DISPONIBLES:

🔍 POST /detect

Envía una imagen y devuelve:

* Detecciones con: clase, confianza, bounding box
* Imagen segmentada codificada en base64
* Resumen textual y numérico
* Verificación si hay más cascos que personas

Ejemplo con curl:

```bash

curl -X 'POST' \
  'http://localhost:8000/detect' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@ruta/a/una/imagen.jpg'
```

🖼 GET /image

Devuelve una página HTML que muestra la última imagen procesada con segmentación aplicada.

🏠 GET /

Muestra un resumen textual de la última inferencia y enlaces a Swagger e imagen segmentada.

📑 GET /docs

Abre la interfaz Swagger generada automáticamente por FastAPI.

## 🧠 Notas para el desarrollador Frontend

El frontend debe enviar imágenes al endpoint /detect como multipart/form-data bajo el campo file.

La respuesta incluye:

* "image_base64": para incrustar directamente en un <img src="...">
* "summary_text": resumen en texto plano
* "summary": conteo por clase

La lógica incluye una advertencia si hay más cascos detectados que personas.

### Proyecto creado con ❤️ por el equipo de especialización en IA. Promoción Techcamp de [Factoría F5](https://www.linkedin.com/school/factoriaf5/)

<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" height="20" alt="GitHub icon"> [Naudelyn Lucena](https://github.com/NaudelynLucena), <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" height="20" alt="GitHub icon"> [Eva G. Muñoz](https://github.com/Emagmunioz), <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" height="20" alt="GitHub icon"> [Grigory Pereira](https://github.com/Grigory-Vladimiro), <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" height="20" alt="GitHub icon"> [Jesús Enjamio](https://github.com/JesusEnjamio), <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" height="20" alt="GitHub icon"> [Mabel Rincón](https://github.com/MabelRincon)
