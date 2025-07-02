import numpy as np
import cv2
from PIL import Image
import io
import base64

def decode_image(file_bytes):
    image_np = np.frombuffer(file_bytes, np.uint8)
    return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

def encode_image_to_base64(image_array):
    img_pil = Image.fromarray(image_array)
    buffer = io.BytesIO()
    img_pil.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
