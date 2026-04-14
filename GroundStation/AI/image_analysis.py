import os
import csv
import onnxruntime as ort
import numpy as np
from PIL import Image
from torchvision import transforms

IMG_SIZE = 256

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "haze_model.onnx")

class_names = ["calima", "no_calima"]

folder_path = os.path.join(BASE_DIR, "../Server/static/uploads")
valid_ext = [".jpg", ".jpeg", ".png", ".bmp"]

output_file = os.path.join(BASE_DIR, "results.csv")

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

session = ort.InferenceSession(MODEL_PATH)

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image)
    image = image.unsqueeze(0).numpy().astype(np.float32)

    outputs = session.run([output_name], {input_name: image})
    logits = outputs[0][0]

    exp_vals = np.exp(logits - np.max(logits))
    probs = exp_vals / np.sum(exp_vals)

    pred = np.argmax(probs)
    confidence = np.max(probs)

    return class_names[pred], float(confidence)

def analyse(req_img=""):
    results = []

    if req_img == "":
        files_to_analyse = [
            file for file in os.listdir(folder_path)
            if any(file.lower().endswith(ext) for ext in valid_ext)
        ]
    else:
        if not any(req_img.lower().endswith(ext) for ext in valid_ext):
            print(f"Formato no valido: {req_img}")
            return
        path = os.path.join(folder_path, req_img)
        if not os.path.exists(path):
            print(f"No existe la imagen: {req_img}")
            return
        files_to_analyse = [req_img]

    for file in files_to_analyse:
        path = os.path.join(folder_path, file)
        pred, conf = predict(path)
        results.append([file, pred, conf])
        print(f"{file} → {pred} ({conf:.2f})")

    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "prediction", "confidence"])
        writer.writerows(results)
    print(f"\nResultados guardados en {output_file}")

if __name__ == "__main__":
    analyse()
