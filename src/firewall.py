import os
import certifi
import torch
from sentence_transformers import SentenceTransformer

# Importamos nuestro modelo
from model import PromptClassifierMulticlass

os.environ["SSL_CERT_FILE"] = certifi.where()

# Mapeo de clases (Ajusta según tu dataset)
CLASS_MAP = {
    0: "safe",
    1: "data_exfiltration",
    2: "jailbreak",
    3: "obfuscation",
    4: "prompt_injection"
}
num_classes = len(CLASS_MAP)

# Inicializamos modelos
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
input_size = 384
model = PromptClassifierMulticlass(input_size, num_classes)

# Asegúrate de que la ruta apunte al modelo correcto
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "prompt_classifier_multiclass.pt")
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

def apply_policy(score):
    if score > 0.65:
        return "BLOCK"
    elif score > 0.50:
        return "FLAG"
    return "ALLOW"

def analyze_prompt(prompt):
    embedding = embedding_model.encode([prompt])
    embedding_tensor = torch.tensor(embedding, dtype=torch.float32)

    with torch.no_grad():
        raw_outputs = model(embedding_tensor)
        probabilities = torch.softmax(raw_outputs, dim=1)[0]
        
        # La probabilidad de que sea seguro está en el índice 0
        prob_safe = probabilities[0].item()
        
        # El Threat Score es la suma de las probabilidades de todas las demás clases (ataques)
        threat_score = 1.0 - prob_safe
        
        # También identificamos cuál es el ataque más probable (para los logs)
        predicted_class_idx = torch.argmax(probabilities).item()
        attack_type = CLASS_MAP.get(predicted_class_idx, "Desconocido")

    decision = apply_policy(threat_score)
    return threat_score, decision, attack_type

def interactive_firewall():
    print("\n🛡️ LLM Firewall Avanzado Listo 🛡️\n")

    while True:
        prompt = input("Enter prompt (or type 'exit'): ")
        if prompt.lower() == "exit":
            break

        score, decision, attack_type = analyze_prompt(prompt)

        print(f"\nThreat Score: {score:.2f}")

        if decision == "BLOCK":
            print(f"🚫 BLOCKED: {attack_type} detected\n")
        elif decision == "FLAG":
            print(f"⚠️ FLAGGED: Suspicious behavior ({attack_type})\n")
        else:
            print("✅ ALLOWED: Prompt appears safe\n")

if __name__ == "__main__":
    interactive_firewall()