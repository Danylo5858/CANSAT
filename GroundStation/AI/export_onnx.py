import torch
import torch.nn as nn
import timm

# ======================
# CONFIG
# ======================
MODEL_PATH = "haze_model.pth"
ONNX_PATH = "haze_model.onnx"

IMG_SIZE = 256
NUM_CLASSES = 2
MODEL_NAME = "mobilenetv3_small_100"

device = "cpu"

# ======================
# RECREAR MODELO
# ======================
model = timm.create_model(MODEL_NAME, pretrained=False)
model.classifier = nn.Linear(model.classifier.in_features, NUM_CLASSES)

# cargar pesos entrenados
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))

model.eval()

# ======================
# INPUT FALSO (IMPORTANTE)
# ======================
dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

# ======================
# EXPORTAR A ONNX
# ======================
torch.onnx.export(
    model,
    dummy_input,
    ONNX_PATH,
    input_names=["input"],
    output_names=["output"],
    opset_version=11
)

print(f"Modelo exportado a {ONNX_PATH}")
