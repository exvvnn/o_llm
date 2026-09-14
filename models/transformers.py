import re
import math
from dataclasses import dataclass
from typing import Dict, List, Set



WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)

# Common English stop words to filter
STOP_WORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "will", "with", "i", "you", "we", "they",
    "this", "which", "who", "what", "when", "where", "why", "how"
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    normalized = normalize_text(text)
    tokens = WORD_RE.findall(normalized)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return tokens


def vectorize(text: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for token in tokenize(text):
        counts[token] = counts.get(token, 0) + 1
    return counts


def dot_product(left: Dict[str, int], right: Dict[str, int]) -> int:
    return sum(left.get(term, 0) * value for term, value in right.items())


def magnitude(vector: Dict[str, int]) -> float:
    return sum(value * value for value in vector.values()) ** 0.5


def cosine_similarity(left: Dict[str, int], right: Dict[str, int]) -> float:
    if not left or not right:
        return 0.0
    denom = magnitude(left) * magnitude(right)
    return dot_product(left, right) / denom if denom != 0 else 0.0


def compute_idf(all_tokens: List[List[str]]) -> Dict[str, float]:
    """Compute Inverse Document Frequency for all terms."""
    doc_count = len(all_tokens)
    if doc_count == 0:
        return {}
    
    term_doc_count: Dict[str, int] = {}
    for tokens in all_tokens:
        unique_terms = set(tokens)
        for term in unique_terms:
            term_doc_count[term] = term_doc_count.get(term, 0) + 1
    
    idf: Dict[str, float] = {}
    for term, count in term_doc_count.items():
        idf[term] = math.log(doc_count / count) if count > 0 else 0.0
    
    return idf


def tfidf_vectorize(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    """Convert tokens to TF-IDF vector."""
    tf: Dict[str, int] = {}
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1
    
    # Normalize TF by document length
    doc_length = len(tokens)
    tfidf: Dict[str, float] = {}
    
    for term, count in tf.items():
        tf_normalized = count / doc_length if doc_length > 0 else 0
        idf_val = idf.get(term, 0.0)
        tfidf[term] = tf_normalized * idf_val
    
    return tfidf


def tfidf_cosine_similarity(left: Dict[str, float], right: Dict[str, float]) -> float:
    """Compute cosine similarity for TF-IDF vectors."""
    if not left or not right:
        return 0.0
    
    dot_prod = sum(left.get(term, 0) * value for term, value in right.items())
    left_mag = math.sqrt(sum(v * v for v in left.values()))
    right_mag = math.sqrt(sum(v * v for v in right.values()))
    
    denom = left_mag * right_mag
    return dot_prod / denom if denom > 0 else 0.0


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 200) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return [chunk for chunk in chunks if chunk]


@dataclass
class TextChunk:
    text: str
    source: str
    position: int
    metadata: Dict[str, str]


class SimpleTextRetriever:
    def __init__(self):
        self.chunks: List[TextChunk] = []
        self.vectors: List[Dict[str, int]] = []

    def fit(self, chunks: List[TextChunk]) -> None:
        self.chunks = chunks
        self.vectors = [vectorize(chunk.text) for chunk in chunks]

    def retrieve(self, query: str, top_k: int = 3) -> List[TextChunk]:
        if not self.chunks:
            return []
        query_vector = vectorize(query)
        scored = []
        for chunk, vector in zip(self.chunks, self.vectors):
            score = cosine_similarity(query_vector, vector)
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for score, chunk in scored if score > 0][:top_k]


class TFIDFRetriever:
    """Enhanced retriever using TF-IDF weighting for better relevance."""
    
    def __init__(self):
        self.chunks: List[TextChunk] = []
        self.vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.all_tokens: List[List[str]] = []

    def fit(self, chunks: List[TextChunk]) -> None:
        self.chunks = chunks
        # Tokenize all chunks
        self.all_tokens = [tokenize(chunk.text) for chunk in chunks]
        # Compute IDF
        self.idf = compute_idf(self.all_tokens)
        # Compute TF-IDF vectors
        self.vectors = [tfidf_vectorize(tokens, self.idf) for tokens in self.all_tokens]

    def retrieve(self, query: str, top_k: int = 3) -> List[TextChunk]:
        if not self.chunks:
            return []
        
        query_tokens = tokenize(query)
        query_vector = tfidf_vectorize(query_tokens, self.idf)
        
        scored = []
        for chunk, vector in zip(self.chunks, self.vectors):
            score = tfidf_cosine_similarity(query_vector, vector)
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for score, chunk in scored if score > 0][:top_k]


class TransformerRetriever:
    """Embedding retriever backed by a Hugging Face encoder model."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        self.model_name = model_name
        self.device_name = device
        self.chunks: List[TextChunk] = []
        self.embeddings = None
        self.tokenizer = None
        self.model = None

    def _load_model(self) -> None:
        if self.model is not None:
            return

        import torch
        from transformers import AutoModel, AutoTokenizer

        device = torch.device(self.device_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(device)
        self.model.eval()

    def _encode(self, texts: List[str]):
        import torch

        self._load_model()
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).to(self.device_name)
        with torch.no_grad():
            outputs = self.model(**inputs)
            mask = inputs["attention_mask"].unsqueeze(-1)
            embeddings = (outputs.last_hidden_state * mask).sum(dim=1)
            embeddings = embeddings / mask.sum(dim=1).clamp(min=1e-9)
            return torch.nn.functional.normalize(embeddings, p=2, dim=1)

    def fit(self, chunks: List[TextChunk]) -> None:
        self.chunks = chunks
        self.embeddings = self._encode([chunk.text for chunk in chunks])

    def retrieve(self, query: str, top_k: int = 3) -> List[TextChunk]:
        if not self.chunks:
            return []

        query_embedding = self._encode([query])[0]
        scores = self.embeddings @ query_embedding
        ranking = scores.argsort(descending=True)[:top_k]
        return [self.chunks[index.item()] for index in ranking]
