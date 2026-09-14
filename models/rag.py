import os
import datetime
import re
from typing import Callable, List, Optional, Tuple

from .transformers import (
    TextChunk,
    SimpleTextRetriever,
    TFIDFRetriever,
    TransformerRetriever,
    chunk_text,
)


class RAGTimeModel:
    def __init__(
        self,
        text_dir: str,
        chunk_size: int = 1200,
        overlap: int = 200,
        default_top_k: int = 3,
        retriever_type: str = "tfidf",
        content_files: Optional[List[str]] = None,
        generator: Optional[Callable[[str], str]] = None,
        retriever_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.text_dir = text_dir
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.default_top_k = default_top_k
        self.retriever_type = retriever_type
        self.content_files = content_files
        self.generator = generator
        
        # Initialize retriever based on type
        if retriever_type.lower() == "tfidf":
            self.retriever = TFIDFRetriever()
        elif retriever_type.lower() == "transformer":
            self.retriever = TransformerRetriever(model_name=retriever_model_name)
        else:
            self.retriever = SimpleTextRetriever()
        
        self.index_built = False
        self.created_at = datetime.datetime.now(datetime.timezone.utc)

    def _selected_filenames(self) -> List[str]:
        if self.content_files is not None:
            return sorted(self.content_files)

        filenames = sorted(
            filename
            for filename in os.listdir(self.text_dir)
            if filename.lower().endswith(".txt")
        )
        semantic_corpus = "book_summaries.txt"
        if semantic_corpus in filenames:
            return [semantic_corpus]
        return filenames

    def load_documents(self) -> List[Tuple[str, str]]:
        if not os.path.isdir(self.text_dir):
            raise FileNotFoundError(f"Text directory not found: {self.text_dir}")

        documents: List[Tuple[str, str]] = []
        for filename in self._selected_filenames():
            path = os.path.join(self.text_dir, filename)
            with open(path, "r", encoding="utf-8", errors="replace") as file:
                documents.append((filename, file.read()))
        return documents

    def load_text_files(self) -> List[str]:
        return [text for _, text in self.load_documents()]

    @staticmethod
    def _split_records(filename: str, text: str) -> List[Tuple[str, str]]:
        if filename == "book_summaries.txt":
            records = [record.strip() for record in text.split("\n\n") if record.strip()]
            return [
                (record.splitlines()[0].removeprefix("BOOK: "), record)
                for record in records
            ]
        return [(filename, text)]

    def build_index(self, texts: Optional[List[str]] = None) -> None:
        if texts is None:
            documents = self.load_documents()
        else:
            documents = [
                (f"document_{index}", text)
                for index, text in enumerate(texts, start=1)
            ]

        chunks: List[TextChunk] = []
        for source_name, source_text in documents:
            records = self._split_records(source_name, source_text)
            for record_name, text in records:
                source = record_name or source_name
                for position, chunk_text_item in enumerate(
                    chunk_text(text, chunk_size=self.chunk_size, overlap=self.overlap),
                    start=1,
                ):
                    chunks.append(
                        TextChunk(
                            text=chunk_text_item,
                            source=source,
                            position=position,
                            metadata={
                                "source_file": source_name,
                                "source_directory": os.path.abspath(self.text_dir),
                            },
                        )
                    )

        self.retriever.fit(chunks)
        self.index_built = True

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[TextChunk]:
        if top_k is None:
            top_k = self.default_top_k
        if not self.index_built:
            self.build_index()
        return self.retriever.retrieve(query, top_k)

    def build_context(self, query: str, top_k: Optional[int] = None) -> str:
        """Return retrieved source text formatted for a generative model."""
        retrieved_chunks = self.retrieve(query, top_k)
        return "\n\n---\n\n".join(
            f"Source: {chunk.source} (chunk {chunk.position})\n"
            f"Directory: {chunk.metadata.get('source_directory', self.text_dir)}\n"
            f"{chunk.text}"
            for chunk in retrieved_chunks
        )

    def answer_with_generator(
        self,
        query: str,
        generator: Callable[[str], str],
        top_k: Optional[int] = None,
    ) -> str:
        """Generate a grounded answer using a provider-specific model callable."""
        context_text = self.build_context(query, top_k)
        if not context_text:
            return (
                "No relevant content found in the indexed text files. "
                "Try a different question or add more source documents."
            )

        prompt = (
            "Answer the user question using only the retrieved context below. "
            "If the context does not contain the answer, say that the evidence "
            "is insufficient. Cite the source title when making a claim.\n\n"
            f"User question:\n{query}\n\n"
            f"Retrieved context:\n{context_text}"
        )
        return generator(prompt)

    def generate_answer(self, query: str, top_k: Optional[int] = None) -> str:
        if self.generator is not None:
            return self.answer_with_generator(query, self.generator, top_k)

        context_text = self.build_context(query, top_k)
        if not context_text:
            return (
                "No relevant content found in the indexed text files. "
                "Try a different question or add more source documents."
            )

        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        answer = (
            f"RAG Time Model response generated at {now}\n\n"
            f"User query: {query}\n\n"
            "Retrieved context:\n"
            f"{context_text}\n\n"
            "Use this retrieved context to answer the user question. "
            "For a production setup, wire this output into a generative model."
        )
        return answer

    def ask(self, query: str, top_k: Optional[int] = None) -> str:
        return self.generate_answer(query, top_k)

    def save_answer(
        self,
        query: str,
        output_dir: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> str:
        """Save a retrieved answer as a Markdown file and return its path."""
        if output_dir is None:
            output_dir = os.path.join(self.text_dir, "answers")

        os.makedirs(output_dir, exist_ok=True)
        filename = re.sub(r"[^a-zA-Z0-9]+", "-", query).strip("-").lower()
        filename = f"{filename[:80] or 'answer'}.md"
        output_path = os.path.join(output_dir, filename)
        answer = self.ask(query, top_k)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(f"# RAG Answer\n\n## Question\n\n{query}\n\n")
            file.write(f"## Response\n\n{answer}\n")

        from o_db.storage import save_answer as save_answer_record

        save_answer_record(query, answer, output_path)

        return output_path



# 
if __name__ == "__main__":
    from pathlib import Path

    sample_dir = Path(__file__).resolve().parents[1] / "data"
    model = RAGTimeModel(text_dir=str(sample_dir))

    # what
    try:
        response = model.ask("Generate a LLM given the books from the dataset?", top_k=3)
        print(response)
    except FileNotFoundError as error:
        print(error)
