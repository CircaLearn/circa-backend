from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

### https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# Load tokenizer and model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def main():
    # Example
    ref = "counterbalances: neglect impacts by exerting an opposite effect"
    rest = ["works against", "balances the overall effect", "counterbalances"]
    similarities = compute_similarity(ref, rest)
    pretty_print_similarities(ref, similarities)


def mean_pooling(model_output, attention_mask):
    """
    Perform mean pooling on the model output, taking the attention mask into
    account. This combines token embeddings into an overall sentence embedding.

    Args:
        model_output (torch.Tensor): The output tensor from the model containing
        token embeddings. attention_mask (torch.Tensor): The attention mask
        tensor indicating the valid tokens.

    Returns:
        torch.Tensor: The pooled token embeddings.
    """
    token_embeddings = model_output[0]  # First element contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def compute_similarity(ref: str, rest: list[str]) -> list[tuple[str, float]]:
    """
    Compute the cosine similarity between a reference sentence and a list of
    other sentences.

    Args:
        ref (str): The sentence to compare against. 
        rest (list): A list of sentences to compare with the reference sentence.

    Returns:
        list: A list of tuples containing each sentence and its similarity
        score.
    """
    sentences = [ref] + rest
    # Tokenize sentences
    encoded_input = tokenizer(
        sentences, padding=True, truncation=True, return_tensors="pt"
    )

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

    ref_embedding = sentence_embeddings[0]
    similarities = []
    for other_embedding, sentence in zip(sentence_embeddings[1:], rest):
        # Compute cosine similarity between the sentence embeddings
        similarity = F.cosine_similarity(
            ref_embedding.unsqueeze(0), other_embedding.unsqueeze(0)
        )
        # Append the sentence and its similarity score to the list
        similarities.append((sentence, round(similarity.item(), 5)))
    return similarities


def pretty_print_similarities(
    ref: str, similarities: list[tuple[str, float]]
) -> None:
    """
    Print the similarities between the reference sentence and a list of other
    sentences in a readable format.

    Args:
        ref (str): The sentence to compare against. similarities (list):
        A list of tuples containing each sentence and its similarity score.

    Returns:
        None
    """
    print(f"Sentence similarities to '{ref}'")
    print("-" * 80)
    for index, (sentence, similarity) in enumerate(similarities, start=1):
        print(f"{index}. '{sentence}': {similarity}")


if __name__ == "__main__":
    main()
