import sys
import os
from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# 📦 Model load
model = YOLO("model/best.pt")  # Model path

# 📷 Image path
if len(sys.argv) > 1:
    img_path = sys.argv[1]
else:
    root = tk.Tk()
    root.withdraw()
    img_path = filedialog.askopenfilename(title="Selecciona una imagen")
    if not img_path:
        print("❌ Imagen no seleccionada. Cancelado.")
        sys.exit()

# 🔍 Inference
results = model.predict(source=img_path, conf=0.5, task="segment", save=False)
img = Image.open(img_path).convert("RGB")
img_array = np.array(img)
height, width = img_array.shape[:2]
mask_overlay = np.zeros_like(img_array, dtype=np.uint8)

masks = results[0].masks
boxes = results[0].boxes
names = model.names

# 🎨 Masks & classes
if masks is not None and boxes is not None:
    for i, (mask, box) in enumerate(zip(masks.data, boxes.xyxy)):
        color = np.random.randint(0, 255, size=3)
        binary_mask = mask.cpu().numpy()
        resized_mask = cv2.resize(binary_mask, (width, height))
        for c in range(3):
            mask_overlay[:, :, c] += (resized_mask * color[c]).astype(np.uint8)

        class_id = int(boxes.cls[i])
        class_name = names[class_id]
        x1, y1, _, _ = box.cpu().numpy().astype(int)
        cv2.putText(mask_overlay, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2, cv2.LINE_AA)

    # 👁️ Results visualization
    combined = cv2.addWeighted(img_array, 0.6, mask_overlay, 0.4, 0)
    plt.figure(figsize=(10, 10))
    plt.imshow(combined)
    plt.axis("off")
    plt.title("Máscaras + Clases")
    plt.show()
else:
    print("⚠️ No se encontraron máscaras.")
