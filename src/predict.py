import os
import certifi
import torch
from sentence_transformers import SentenceTransformer
from model import PromptClassifierMulticlass

os.environ["SSL_CERT_FILE"] = certifi.where()

CLASS_MAP = {
    0: "safe",
    1: "data_exfiltration",
    2: "jailbreak",
    3: "obfuscation",
    4: "prompt_injection"
}
num_classes = len(CLASS_MAP)

print("Cargando modelo de lenguaje...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

input_size = 384
model = PromptClassifierMulticlass(input_size, num_classes)

MODEL_PATH = "models/prompt_classifier_multiclass.pt"
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

print("\n--- Detector de Inyección de Prompts Multiclase Listo ---\n")

while True:
    prompt = input("Ingresa un prompt para analizar (o escribe 'exit'): ")
    if prompt.lower() == "exit":
        break

    embedding = embedding_model.encode([prompt])
    embedding_tensor = torch.tensor(embedding, dtype=torch.float32)

    with torch.no_grad():
        raw_outputs = model(embedding_tensor) 
        
        probabilities = torch.softmax(raw_outputs, dim=1)[0]
        
        predicted_class_idx = torch.argmax(probabilities).item()
        
        confidence = probabilities[predicted_class_idx].item()

    category_name = CLASS_MAP.get(predicted_class_idx, "Desconocido")
    
    if predicted_class_idx == 0:
        print(f"\nPrompt aparentemente seguro. Confianza: {confidence:.2f}\n")
    else:
        print(f"\n¡ALERTA DE ATAQUE DETECTADA! 🚨")
        print(f"-> Categoría: {category_name}")
        print(f"-> Nivel de confianza: {confidence:.2f}\n")