from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model_name = "sentence-transformers/all-MiniLM-L6-v2"
device = torch.device("cpu")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

query = "How do I use Python?"
candidates = [
    "Python is a programming language.",
    "The weather is sunny today.",
    "A recipe needs flour and water.",
]
texts = [query, *candidates]
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)
    mask = inputs["attention_mask"].unsqueeze(-1)
    embeddings = (outputs.last_hidden_state * mask).sum(dim=1)
    embeddings = embeddings / mask.sum(dim=1).clamp(min=1e-9)
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

scores = embeddings[1:] @ embeddings[0]
ranking = torch.argsort(scores, descending=True)

print(f"Query: {query}")
for index in ranking:
    candidate_index = index.item()
    print(f"{scores[candidate_index].item():.3f}  {candidates[candidate_index]}")
print(f"Prediction: {candidates[ranking[0].item()]}")


