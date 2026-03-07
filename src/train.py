import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

# get dataset
data = pd.read_csv("dataset/prompts.csv")

# embeddings model to translate text to vectors
model = SentenceTransformer("all-MiniLM-L6-v2")

# generate embeddings 
embeddings = model.encode(data["prompt"].tolist())

print("Shape de embeddings:", embeddings.shape)