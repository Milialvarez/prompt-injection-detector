import os
import certifi
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split

# Importamos nuestro nuevo modelo multiclase
from model import PromptClassifierMulticlass

os.environ["SSL_CERT_FILE"] = certifi.where()

# 1. LOAD DATASET
data = pd.read_csv("dataset/prompts_multiclass.csv") # Asumiendo que generaste el nuevo CSV

prompts = data["prompt"].tolist()
labels = data["label"].tolist()

# Detectamos cuántas clases únicas hay en tu dataset
num_classes = len(set(labels))
print(f"Detectadas {num_classes} clases diferentes.")

# 2. TEXT → VECTOR EMBEDDINGS
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("Generating embeddings...")
embeddings = embedding_model.encode(prompts)
print("Embeddings shape:", embeddings.shape)

# 3. TRAIN / TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    embeddings,
    labels,
    test_size=0.2,
    random_state=42
)

# 4. CONVERT DATA TO PYTORCH TENSORS
X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)

# IMPORTANTE: Para CrossEntropyLoss, los labels deben ser enteros (long), no float.
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

# 5. MODEL INITIALIZATION
input_size = embeddings.shape[1]
model = PromptClassifierMulticlass(input_size, num_classes)

# 6. LOSS FUNCTION & OPTIMIZER
# CrossEntropyLoss es la estándar para clasificación multiclase
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 7. TRAINING LOOP
epochs = 100

for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    
    outputs = model(X_train)
    
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    
    print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

# 8. MODEL EVALUATION
model.eval()
with torch.no_grad():
    predictions = model(X_test)
    
    # Argmax elige el índice de la clase con la probabilidad más alta
    predicted_labels = torch.argmax(predictions, dim=1)
    
    accuracy = (predicted_labels == y_test).float().mean()

print(f"\nTest Accuracy: {accuracy.item():.4f}")

# 9. SAVE TRAINED MODEL
torch.save(model.state_dict(), "models/prompt_classifier_multiclass.pt")
print("Model saved as prompt_classifier_multiclass.pt")