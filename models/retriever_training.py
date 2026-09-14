"""Train the local transformer retriever with query/document pairs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import torch
from torch import Tensor
from torch.optim import AdamW
from transformers import AutoModel, AutoTokenizer


@dataclass(frozen=True)
class RetrievalExample:
    query: str
    positive_text: str
    positive_source: str


def load_book_records(corpus_path: str | Path) -> dict[str, str]:
    records: dict[str, str] = {}
    current: list[str] = []

    def add_record(lines: list[str]) -> None:
        if not lines or not lines[0].startswith("BOOK: "):
            return
        source = lines[0].removeprefix("BOOK: ").strip()
        records[source] = "\n".join(lines).strip()

    for line in Path(corpus_path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            current.append(line.strip())
        elif current:
            add_record(current)
            current = []
    add_record(current)
    return records


def load_examples(pairs_path: str | Path, corpus_path: str | Path) -> list[RetrievalExample]:
    records = load_book_records(corpus_path)
    examples: list[RetrievalExample] = []
    for line_number, line in enumerate(
        Path(pairs_path).read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            item: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error
        query = str(item.get("query", "")).strip()
        source = str(item.get("positive_source", "")).strip()
        if not query or not source:
            raise ValueError(f"Line {line_number} needs query and positive_source")
        if source not in records:
            raise ValueError(f"Line {line_number} references unknown source: {source}")
        examples.append(RetrievalExample(query, records[source], source))
    if len(examples) < 2:
        raise ValueError("At least two retrieval examples are required")
    return examples


def mean_pool(last_hidden_state: Tensor, attention_mask: Tensor) -> Tensor:
    mask = attention_mask.unsqueeze(-1).to(last_hidden_state.dtype)
    pooled = (last_hidden_state * mask).sum(dim=1)
    return pooled / mask.sum(dim=1).clamp(min=1e-9)


def contrastive_loss(query_embeddings: Tensor, document_embeddings: Tensor, temperature: float = 0.05) -> Tensor:
    if query_embeddings.shape != document_embeddings.shape:
        raise ValueError("query and document embeddings must have the same shape")
    if query_embeddings.shape[0] < 2:
        raise ValueError("contrastive loss requires at least two examples")
    query_embeddings = torch.nn.functional.normalize(query_embeddings, p=2, dim=1)
    document_embeddings = torch.nn.functional.normalize(document_embeddings, p=2, dim=1)
    logits = query_embeddings @ document_embeddings.T / temperature
    labels = torch.arange(logits.shape[0], device=logits.device)
    return torch.nn.functional.cross_entropy(logits, labels)


def _encode(tokenizer: Any, model: Any, texts: Iterable[str], device: torch.device) -> Tensor:
    inputs = tokenizer(
        list(texts),
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    ).to(device)
    outputs = model(**inputs)
    return mean_pool(outputs.last_hidden_state, inputs["attention_mask"])


def train_retriever(
    examples: list[RetrievalExample],
    output_dir: str | Path,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    epochs: int = 3,
    learning_rate: float = 2e-5,
    batch_size: int = 8,
    device: str = "cpu",
) -> Path:
    if epochs < 1 or batch_size < 2 or learning_rate <= 0:
        raise ValueError("epochs >= 1, batch_size >= 2, and learning_rate > 0 are required")

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(torch.device(device))
    model.train()
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    device_object = torch.device(device)

    for _ in range(epochs):
        for start in range(0, len(examples), batch_size):
            batch = examples[start : start + batch_size]
            if len(batch) < 2:
                continue
            queries = _encode(tokenizer, model, (item.query for item in batch), device_object)
            documents = _encode(tokenizer, model, (item.positive_text for item in batch), device_object)
            loss = contrastive_loss(queries, documents)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    model.save_pretrained(target)
    tokenizer.save_pretrained(target)
    (target / "training_config.json").write_text(
        json.dumps(
            {
                "base_model": model_name,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "batch_size": batch_size,
                "example_count": len(examples),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fine-tune a transformer retriever on reviewed query/book pairs.")
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    examples = load_examples(args.pairs, args.corpus)
    output_dir = train_retriever(
        examples,
        args.output_dir,
        model_name=args.model,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        device=args.device,
    )
    print(f"Saved retriever checkpoint to {output_dir}")


if __name__ == "__main__":
    main()
