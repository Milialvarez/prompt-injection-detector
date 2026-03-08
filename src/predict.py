import os
import certifi
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

os.environ["SSL_CERT_FILE"] = certifi.where()

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

# load embedding model

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# load trainer classifier

input_size = 384

model = PromptClassifier(input_size)

# loads the previously trained model
model.load_state_dict(torch.load("prompt_classifier.pt"))

model.eval()


print("\nPrompt Injection Detector Ready\n")

# Allows the user to continuously test prompts.

while True:

    prompt = input("Enter a prompt to analyze (or type 'exit'): ")

    if prompt.lower() == "exit":
        break


    # Convert text → embedding vector
    embedding = embedding_model.encode([prompt])


    # Convert to PyTorch tensor
    embedding_tensor = torch.tensor(embedding, dtype=torch.float32)


    # Run prediction
    with torch.no_grad():

        prediction = model(embedding_tensor)

        probability = prediction.item()


    # Interpret prediction
    if probability > 0.5:

        print(f"\n Malicious prompt detected (probability: {probability:.2f})\n")

    else:

        print(f"\n Prompt appears safe (probability: {probability:.2f})\n")