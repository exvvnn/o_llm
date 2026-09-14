"""Local Hugging Face text generation for grounded RAG answers."""

from __future__ import annotations

from typing import Any, Optional


class LocalTextGenerator:
    """Lazily load a local or Hugging Face seq2seq generation model."""

    def __init__(
        self,
        model_name: str = "google/flan-t5-base",
        device: str = "cpu",
        max_new_tokens: int = 256,
        temperature: float = 0.2,
    ) -> None:
        if max_new_tokens < 1:
            raise ValueError("max_new_tokens must be at least 1")
        if temperature < 0:
            raise ValueError("temperature must be non-negative")

        self.model_name = model_name
        self.device_name = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.tokenizer: Any = None
        self.model: Any = None

    def _load_model(self) -> None:
        if self.model is not None:
            return

        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            local_files_only=False,
        ).to(torch.device(self.device_name))
        self.model.eval()

    def __call__(self, prompt: str) -> str:
        import torch

        self._load_model()
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
        ).to(self.device_name)
        generation_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "num_beams": 4,
            "early_stopping": True,
        }
        if self.temperature > 0:
            generation_kwargs.update({"do_sample": True, "temperature": self.temperature})

        with torch.no_grad():
            output_ids = self.model.generate(**inputs, **generation_kwargs)
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
