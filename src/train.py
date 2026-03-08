import os
import certifi
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split

os.environ["SSL_CERT_FILE"] = certifi.where()

# LOAD DATASET
# Load the dataset containing prompts and labels.
# Example of the CSV content: "Ignore previous instructions",1

data = pd.read_csv("dataset/prompts.csv")

prompts = data["prompt"].tolist()
labels = data["label"].tolist()

# TEXT → VECTOR EMBEDDINGS
# This model converts text into semantic vectors.

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Generating embeddings...")

embeddings = embedding_model.encode(prompts)

print("Embeddings shape:", embeddings.shape)

# TRAIN / TEST SPLIT
# Machine learning models must be evaluated on data that they've never seen during training.

X_train, X_test, y_train, y_test = train_test_split(
    embeddings,
    labels,
    test_size=0.2,
    random_state=42
)

# CONVERT DATA TO PYTORCH TENSORS
# PyTorch operates on tensors instead of numpy arrays.

X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)

y_train = torch.tensor(y_train, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

# DEFINE THE CLASSIFIER MODEL
# This neural network will take the embedding vectors and classify them as malicious or safe.

class PromptClassifier(nn.Module):

    def __init__(self, input_size):

        super(PromptClassifier, self).__init__()

        # First linear layer transforms embedding space
        self.fc1 = nn.Linear(input_size, 128)

        # ReLU activation introduces non-linearity
        self.relu = nn.ReLU()

        # Second layer reduces to a single output
        self.fc2 = nn.Linear(128, 1)

        # Sigmoid converts output to probability
        self.sigmoid = nn.Sigmoid()


    def forward(self, x):

        x = self.fc1(x)

        x = self.relu(x)

        x = self.fc2(x)

        x = self.sigmoid(x)

        return x

# MODEL INITIALIZATION
# all-MiniLM-L6-v2 produces embeddings of size 384.

input_size = embeddings.shape[1]

model = PromptClassifier(input_size)

# LOSS FUNCTION
# Binary Cross Entropy is used for binary classification.

criterion = nn.BCELoss()

# OPTIMIZER
# Adam optimizer adjusts the neural network weights.

optimizer = optim.Adam(model.parameters(), lr=0.001)

# TRAINING LOOP
# The model learns by minimizing the loss function.

epochs = 20

for epoch in range(epochs):

    model.train()

    optimizer.zero_grad()

    outputs = model(X_train).squeeze()

    loss = criterion(outputs, y_train)

    loss.backward()

    optimizer.step()

    print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

# MODEL EVALUATION
# After training evaluates on the test set.

model.eval()

with torch.no_grad():

    predictions = model(X_test).squeeze()

    predicted_labels = (predictions > 0.5).float()

    accuracy = (predicted_labels == y_test).float().mean()

print("Test Accuracy:", accuracy.item())

# SAVE TRAINED MODEL
# Saving the model allows us to load it later for inference or deployment.

torch.save(model.state_dict(), "models/prompt_classifier.pt")

print("Model saved as prompt_classifier.pt")