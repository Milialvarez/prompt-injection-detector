import torch
import torch.nn as nn

class PromptClassifierMulticlass(nn.Module):

    def __init__(self, input_size, num_classes):
        super(PromptClassifierMulticlass, self).__init__()

        # First linear layer transforms embedding space
        self.fc1 = nn.Linear(input_size, 128)

        # ReLU activation introduces non-linearity
        self.relu = nn.ReLU()

        # Second layer outputs raw scores (logits) for EACH class
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x