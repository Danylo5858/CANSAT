import os
import csv
import onnxruntime as ort
import numpy as np
from PIL import Image
from torchvision import transforms

# ======================
# CONFIG
# ======================
IMG_SIZE = 256
MODEL_PATH = "haze_model.onnx"

class_names = ["calima", "no_calima"]

folder_path = "../Server/static/uploads"
valid_ext = [".jpg", ".jpeg", ".png", ".bmp"]

output_file = "results.csv"

# ======================
# TRANSFORM
# ======================
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

# ======================
# ONNX MODEL
# ======================
session = ort.InferenceSession(MODEL_PATH)

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# ======================
# PREDICCIÓN
# ======================
def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image)

    image = image.unsqueeze(0).numpy().astype(np.float32)

    outputs = session.run([output_name], {input_name: image})

    logits = outputs[0][0]

    # softmax manual
    exp_vals = np.exp(logits - np.max(logits))
    probs = exp_vals / np.sum(exp_vals)

    pred = np.argmax(probs)
    confidence = np.max(probs)

    return class_names[pred], float(confidence)

# ======================
# ANÁLISIS DE CARPETA
# ======================
def analyse():
    results = []

    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in valid_ext):

            path = os.path.join(folder_path, file)

            pred, conf = predict(path)

            results.append([file, pred, conf])

            print(f"{file} → {pred} ({conf:.2f})")

    # ======================
    # GUARDAR CSV
    # ======================
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["image", "prediction", "confidence"])
        writer.writerows(results)

    print(f"\nResultados guardados en {output_file}")

analyse()
