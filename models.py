from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

### From all-MiniLM-L6-v2 HuggingFace Page Example Code
### https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Sentences we want sentence embeddings for
sentences = ["approximately", "around the same"]

# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

# Compute token embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Perform pooling
sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])

# Normalize embeddings -> big 1D tensors capturing semantic meaning of sentences
sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

# Compute cosine similarity between the sentence embeddings
similarity = F.cosine_similarity(
    sentence_embeddings[0].unsqueeze(0), sentence_embeddings[1].unsqueeze(0)
)
# .item() outputs python number from 1D tensor
print(f"Sentence similarity: {similarity.item()}") 
