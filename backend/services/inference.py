"""
InferenceService — loads LlamaTron RS1 Nemesis and runs clinical reasoning.
"""
from __future__ import annotations

import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from backend.core.config import get_settings
from backend.core.logger import logger

cfg = get_settings()

SYSTEM_PROMPT = """You are LlamaTron RS1 Nemesis, a clinical decision support AI.
When a clinician or researcher describes patient symptoms, you MUST respond in this
exact structured format:

## 🔍 Clinical Reasoning
<Think through the case step by step: onset, duration, severity, associated
symptoms, red flags, relevant anatomy/physiology.>

## 📋 Differential Diagnosis
List the top 3-5 diagnoses from most to least likely. For each write:
**1. [Diagnosis Name]** — [brief rationale, 1-2 sentences]

## 🩺 Recommended Workup
List the investigations to order (labs, imaging, etc.).

## 💊 Treatment Plan
Describe the initial management approach including medications if appropriate.

## ⚠️ Red Flags / Escalation
State any warning signs that require urgent escalation.

Always end with:
*This output is AI-generated and is for educational/research purposes only.
Not a substitute for professional medical judgement.*
"""


class InferenceService:
    _instance: InferenceService | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        logger.info(f"Loading model: {cfg.model_id}")
        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        dtype = dtype_map.get(cfg.torch_dtype, torch.bfloat16)

        self.tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            cfg.model_id,
            torch_dtype=dtype,
            device_map=cfg.device,
        )
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        self._loaded = True
        logger.info("Model loaded ✓")

    def analyze(
        self,
        symptoms: str,
        patient_age: int | None = None,
        patient_sex: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        """
        Run clinical analysis. Returns dict with:
          - full_response: complete model output
          - reasoning: extracted chain-of-thought section
          - differentials: extracted differential diagnosis section
          - treatment: extracted treatment section
        """
        if not self._loaded:
            self.load()

        # Build patient context string
        context_parts = []
        if patient_age:
            context_parts.append(f"Age: {patient_age}")
        if patient_sex:
            context_parts.append(f"Sex: {patient_sex}")
        context = ", ".join(context_parts)
        user_content = f"{context + chr(10) if context else ''}Symptoms: {symptoms}"

        # Build messages with optional multi-turn history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        output = self.pipe(
            messages,
            max_new_tokens=cfg.max_new_tokens,
            do_sample=True,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
        )
        full_response: str = output[0]["generated_text"][-1]["content"]

        return {
            "full_response": full_response,
            "reasoning": _extract(full_response, "Clinical Reasoning"),
            "differentials": _extract(full_response, "Differential Diagnosis"),
            "workup": _extract(full_response, "Recommended Workup"),
            "treatment": _extract(full_response, "Treatment Plan"),
            "red_flags": _extract(full_response, "Red Flags"),
        }


def _extract(text: str, section: str) -> str:
    """Pull text between a section header and the next ## header."""
    pattern = rf"##[^#]*{re.escape(section)}.*?\n(.*?)(?=\n##|$)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


# Singleton
inference_service = InferenceService()
