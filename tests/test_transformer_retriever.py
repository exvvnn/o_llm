from o_agent.models.rag import RAGTimeModel
from o_agent.models.transformers import TextChunk, TransformerRetriever


class FakeIndex:
    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


class FakeScores:
    def __init__(self, scores):
        self.scores = scores

    def argsort(self, descending=False):
        indexes = sorted(
            range(len(self.scores)),
            key=self.scores.__getitem__,
            reverse=descending,
        )
        return [FakeIndex(index) for index in indexes]


class FakeEmbeddings:
    def __init__(self, rows):
        self.rows = rows

    def __matmul__(self, query):
        return FakeScores([
            sum(left * right for left, right in zip(row, query))
            for row in self.rows
        ])

    def __getitem__(self, index):
        return self.rows[index]


def test_transformer_retriever_ranks_matching_embedding():
    retriever = TransformerRetriever()
    chunks = [
        TextChunk("attention and tokenization", "llm-book", 1, {}),
        TextChunk("cloud cost management", "finops-book", 1, {}),
    ]

    def encode(texts):
        if texts == [chunks[0].text, chunks[1].text]:
            return FakeEmbeddings([[1.0, 0.0], [0.0, 1.0]])
        return FakeEmbeddings([[1.0, 0.0]])

    retriever._encode = encode
    retriever.fit(chunks)

    results = retriever.retrieve("transformer attention", top_k=1)

    assert results == [chunks[0]]
    assert retriever.model is None


def test_rag_selects_transformer_retriever_without_loading_model():
    model = RAGTimeModel("o_agent/data", retriever_type="transformer")

    assert isinstance(model.retriever, TransformerRetriever)
    assert model.retriever.model is None
