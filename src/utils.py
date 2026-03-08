import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset(path):

    df = pd.read_csv(path)

    prompts = df["prompt"].tolist()
    labels = df["label"].tolist()

    return train_test_split(
        prompts,
        labels,
        test_size=0.2,
        random_state=42
    )

# creates a dict with the prompt words
def build_vocab(prompts):

    vocab = {"<PAD>":0}

    idx = 1

    for p in prompts:

        for word in p.split():

            if word not in vocab:

                vocab[word] = idx
                idx += 1

    return vocab

# converts prompts in numbers
def encode_prompt(prompt, vocab, max_len=20):

    tokens = prompt.split()

    ids = [vocab.get(t,0) for t in tokens]

    ids = ids[:max_len]

    while len(ids) < max_len:
        ids.append(0)

    return ids