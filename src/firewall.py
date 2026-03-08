import os
import certifi
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

os.environ["SSL_CERT_FILE"] = certifi.where()

# FUNCTIONALITY: this script 
# # 1. analyzes a prompt 
# # 2. calculates the threat score 
# # 3. applies security politics 
# # 4. chooses and clasifyes: allow / flag / block

class PromptClassifier(nn.Module):

    def __init__(self, input_size):

        super(PromptClassifier, self).__init__()

        self.fc1 = nn.Linear(input_size, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):

        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)

        return x

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

input_size = 384

model = PromptClassifier(input_size)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "prompt_classifier.pt")

model.load_state_dict(torch.load(MODEL_PATH))

model.eval()

def apply_policy(score):

    if score > 0.75:
        return "BLOCK"

    elif score > 0.55:
        return "FLAG"

    return "ALLOW"


def analyze_prompt(prompt):

    embedding = embedding_model.encode([prompt])

    embedding_tensor = torch.tensor(embedding, dtype=torch.float32)

    with torch.no_grad():

        prediction = model(embedding_tensor)

        score = prediction.item()

    decision = apply_policy(score)

    return score, decision

def interactive_firewall():

    print("\nLLM Firewall Ready\n")

    while True:

        prompt = input("Enter prompt (or type 'exit'): ")

        if prompt.lower() == "exit":
            break

        score, decision = analyze_prompt(prompt)

        print(f"\nThreat Score: {score:.2f}")

        if decision == "BLOCK":

            print("BLOCKED: Potential prompt injection detected\n")

        elif decision == "FLAG":

            print("FLAGGED: Suspicious prompt\n")

        else:

            print("ALLOWED: Prompt appears safe\n")


# runs only if executed directly

if __name__ == "__main__":
    interactive_firewall()