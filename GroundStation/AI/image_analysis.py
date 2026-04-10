import os
import csv
import torch
import torch.nn as nn
import timm
from torchvision import transforms
from PIL import Image

# ======================
# CONFIG
# ======================
IMG_SIZE = 256
MODEL_NAME = "mobilenetv3_small_100"
MODEL_PATH = "haze_model.pth"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

class_names = ["calima", "no_calima"]

# ======================
# TRANSFORM
# ======================
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

# ======================
# MODEL
# ======================
model = timm.create_model(MODEL_NAME, pretrained=False)
model.classifier = nn.Linear(model.classifier.in_features, len(class_names))

model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

# ======================
# PREDICCIÓN
# ======================
def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image)
    image = image.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred = torch.max(probs, 1)

    return class_names[pred.item()], confidence.item()

# ======================
# CARPETA DE IMÁGENES
# ======================
folder_path = "../Server/uploads"
valid_ext = [".jpg", ".jpeg", ".png", ".bmp"]

# ======================
# GUARDAR RESULTADOS
# ======================
output_file = "results.csv"

def analyse():
    results = []

    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in valid_ext):

            path = os.path.join(folder_path, file)

            pred, conf = predict(path)

            results.append([file, pred, conf])

            print(f"{file} → {pred} ({conf:.2f})")

    # ======================
    # ESCRIBIR CSV
    # ======================
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)

        # encabezado
        writer.writerow(["image", "prediction", "confidence"])

        # datos
        writer.writerows(results)

    print(f"\nResultados guardados en {output_file}")

analyse()
