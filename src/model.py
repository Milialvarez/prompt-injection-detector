import torch
import torch.nn as nn

class PromptClassifier(nn.Module):

    def __init__(self, vocab_size, embed_dim):
        super().__init__()

        # converts text into numeric vectors to understand semantic relations
        self.embedding = nn.Embedding(vocab_size, embed_dim)

        # determinates the probability of the attack
        self.fc = nn.Linear(embed_dim, 1)

        # converts the output in a number between 0 and 1, so 0,1 = safe, 0,9 = most probably malicious
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):

        embeds = self.embedding(x)

        pooled = embeds.mean(dim=1)

        out = self.fc(pooled)

        out = self.sigmoid(out)

        return out