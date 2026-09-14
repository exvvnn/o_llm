import json

import pytest
import torch

from o_agent.models.retriever_training import (
    contrastive_loss,
    load_examples,
    load_book_records,
)


def test_load_examples_resolves_book_sources(tmp_path):
    corpus = tmp_path / "books.txt"
    corpus.write_text("BOOK: Example (2024)\nTopics: testing\n\n", encoding="utf-8")
    pairs = tmp_path / "pairs.jsonl"
    pairs.write_text(
        json.dumps({"query": "testing", "positive_source": "Example (2024)"}) + "\n"
        + json.dumps({"query": "another", "positive_source": "Example (2024)"}) + "\n",
        encoding="utf-8",
    )

    records = load_book_records(corpus)
    examples = load_examples(pairs, corpus)

    assert records["Example (2024)"].startswith("BOOK: Example")
    assert examples[0].positive_source == "Example (2024)"
    assert examples[0].positive_text == records["Example (2024)"]


def test_load_examples_rejects_unknown_source(tmp_path):
    corpus = tmp_path / "books.txt"
    corpus.write_text("BOOK: Example (2024)\nTopics: testing\n", encoding="utf-8")
    pairs = tmp_path / "pairs.jsonl"
    pairs.write_text(
        json.dumps({"query": "testing", "positive_source": "Missing"}) + "\n"
        + json.dumps({"query": "another", "positive_source": "Missing"}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown source"):
        load_examples(pairs, corpus)


def test_contrastive_loss_prefers_matching_documents():
    queries = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    documents = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

    loss = contrastive_loss(queries, documents)

    assert loss.item() < 0.1
