import os
import certifi
import torch
from sentence_transformers import SentenceTransformer

# Importamos la arquitectura desde nuestro archivo centralizado
from model import PromptClassifierMulticlass

os.environ["SSL_CERT_FILE"] = certifi.where()

# --- CONFIGURACIÓN DE CLASES ---
# IMPORTANTE: Actualiza este diccionario según lo que imprimió tu generador de datasets.
# Asumimos este ejemplo basado en tus carpetas.
CLASS_MAP = {
    0: "Seguro (Safe)",
    1: "Jailbreak",
    2: "Data Exfiltration",
    3: "Obfuscation"
}
num_classes = len(CLASS_MAP)

# 1. Cargar el modelo de Embeddings
print("Cargando modelo de lenguaje...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Cargar nuestro clasificador entrenado
input_size = 384
model = PromptClassifierMulticlass(input_size, num_classes)

# Cargamos los pesos del nuevo modelo multiclase
MODEL_PATH = "models/prompt_classifier_multiclass.pt"
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

print("\n--- Detector de Inyección de Prompts Multiclase Listo ---\n")

while True:
    prompt = input("Ingresa un prompt para analizar (o escribe 'exit'): ")
    if prompt.lower() == "exit":
        break

    # Convertir texto a vector
    embedding = embedding_model.encode([prompt])
    embedding_tensor = torch.tensor(embedding, dtype=torch.float32)

    # Predicción
    with torch.no_grad():
        raw_outputs = model(embedding_tensor) # Obtenemos los logits crudos
        
        # Aplicamos Softmax para obtener las probabilidades (0.0 a 1.0)
        probabilities = torch.softmax(raw_outputs, dim=1)[0]
        
        # Obtenemos el índice de la clase con mayor probabilidad
        predicted_class_idx = torch.argmax(probabilities).item()
        
        # Extraemos la confianza (probabilidad de la clase ganadora)
        confidence = probabilities[predicted_class_idx].item()

    # Interpretar y mostrar resultados
    category_name = CLASS_MAP.get(predicted_class_idx, "Desconocido")
    
    if predicted_class_idx == 0:
        print(f"\n✅ Prompt aparentemente seguro. Confianza: {confidence:.2f}\n")
    else:
        print(f"\n🚨 ¡ALERTA DE ATAQUE DETECTADA! 🚨")
        print(f"-> Categoría: {category_name}")
        print(f"-> Nivel de confianza: {confidence:.2f}\n")