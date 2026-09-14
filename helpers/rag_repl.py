"""Interactive question-answering shell for the local RAG corpus."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Optional

from o_agent.models.generation import LocalTextGenerator
from o_agent.models.rag import RAGTimeModel


DEFAULT_TEXT_DIR = Path(__file__).resolve().parents[1] / "data"


def _print_help(output_fn: Callable[[str], None]) -> None:
    output_fn("Commands: :help, :sources, :locate <book>, :quit")
    output_fn("Ask a question to search the indexed documents.")


def _locate_books(model: RAGTimeModel, title: str) -> list[Path]:
    """Find vault files whose names contain the requested book title."""
    if not title:
        return []

    vault_root = Path(model.text_dir).resolve().parents[1]
    normalized_title = title.casefold()
    return sorted(
        path
        for path in vault_root.rglob("*")
        if path.is_file()
        and path.suffix.casefold() == ".pdf"
        and normalized_title in path.stem.casefold()
    )



# RUN RELP
def run_repl(
    model: RAGTimeModel,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:


    """Run a question loop against an already configured RAG model."""
    # Build once before prompting so the first question does not pay the indexing cost.
    model.build_index()
    output_fn("RAG REPL ready. Type :help for commands or :quit to exit.")

    while True:
        try:
            question = input_fn("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("Goodbye.")
            return

        if not question:
            continue
        # Commands control the shell; every other non-empty line is a RAG question.
        if question.lower() in {":quit", ":exit"}:
            output_fn("Goodbye.")
            return
        if question.lower() == ":help":
            _print_help(output_fn)
            continue
        if question.lower() == ":sources":
            output_fn(f"Indexed {len(model.retriever.chunks)} text chunks.")
            continue
        if question.lower().startswith(":locate"):
            title = question[len(":locate") :].strip()
            matches = _locate_books(model, title)
            if matches:
                for match in matches:
                    output_fn(str(match))
            else:
                output_fn(f"No PDF found matching: {title or '[missing title]'}")
            continue

        output_fn(f"\n{model.ask(question)}\n")


# This pattern I might like AI
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask questions of the local RAG corpus.")
    parser.add_argument(
        "--text-dir",
        type=Path,
        default=DEFAULT_TEXT_DIR,
        help="Directory containing source .txt files (default: o_agent/data).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of matching chunks to include (default: 3).",
    )
    parser.add_argument(
        "--retriever",
        choices=("simple", "tfidf", "transformer"),
        default="tfidf",
        help="Retrieval strategy (default: tfidf).",
    )
    parser.add_argument(
        "--retriever-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Local path or Hugging Face ID for the transformer retriever.",
    )
    parser.add_argument(
        "--generator-model",
        help="Local path or Hugging Face seq2seq model ID for answer generation.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=256,
        help="Maximum generated answer length (default: 256).",
    )
    return parser


# This method I might us AI... Argv as Optional
def main(argv: Optional[list[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if args.top_k < 1:
        raise SystemExit("--top-k must be at least 1")
    if args.max_new_tokens < 1:
        raise SystemExit("--max-new-tokens must be at least 1")

    generator = None
    if args.generator_model:
        generator = LocalTextGenerator(
            model_name=args.generator_model,
            max_new_tokens=args.max_new_tokens,
        )

    model = RAGTimeModel(
        text_dir=str(args.text_dir),
        default_top_k=args.top_k,
        retriever_type=args.retriever,
        retriever_model_name=args.retriever_model,
        generator=generator,
    )
    try:
        run_repl(model)
    except FileNotFoundError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()