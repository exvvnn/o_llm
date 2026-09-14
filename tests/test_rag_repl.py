from o_agent.models.rag import RAGTimeModel
from o_agent.helpers.rag_repl import run_repl


def test_repl_answers_questions_and_handles_commands(tmp_path):
    corpus = tmp_path / "notes.txt"
    corpus.write_text("Python is useful for data engineering pipelines.", encoding="utf-8")
    (tmp_path / "other.txt").write_text("A separate note about cooking.", encoding="utf-8")
    model = RAGTimeModel(str(tmp_path), default_top_k=1)
    questions = iter([":sources", "What is useful for data engineering?", ":quit"])
    output = []

    run_repl(model, input_fn=lambda _: next(questions), output_fn=output.append)

    assert output[0].startswith("RAG REPL ready")
    assert "Indexed 2 text chunks." in output
    assert "What is useful for data engineering?" in output[-2]
    assert "Python is useful" in output[-2]
    assert output[-1] == "Goodbye."


def test_repl_accepts_eof(tmp_path):
    corpus = tmp_path / "notes.txt"
    corpus.write_text("A short note.", encoding="utf-8")
    model = RAGTimeModel(str(tmp_path))

    run_repl(model, input_fn=lambda _: (_ for _ in ()).throw(EOFError()))
