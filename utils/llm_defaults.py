import json
from pathlib import Path

from models.book_config import BookLLMOverrides

_DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "llm_defaults.json"


def _load() -> dict:
    if not _DEFAULTS_PATH.exists():
        return {}
    return json.loads(_DEFAULTS_PATH.read_text())


def _match_key(raw: dict, model: str) -> str | None:
    model_lower = model.lower()
    # Longest key first so more-specific entries win over shorter prefixes.
    # Match if either string contains the other (handles "qwen3.5" ↔ "qwen3.5-122b").
    for key in sorted(raw, key=len, reverse=True):
        k = key.lower()
        if k == model_lower or k in model_lower or model_lower in k:
            return key
    return None


def resolve_llm_defaults(model: str, category: str) -> BookLLMOverrides | None:
    raw = _load()
    key = _match_key(raw, model)
    if key is None:
        return None
    entry = raw[key].get(category)
    if not entry:
        return None
    return BookLLMOverrides.model_validate(entry)


def matched_model_key(model: str) -> str | None:
    return _match_key(_load(), model)
