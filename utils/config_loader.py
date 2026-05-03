import os
from pathlib import Path

import yaml

from models.book_config import BookConfig, BookLLMOverrides
from models.config import CategoryTemplate, LLMConfig, ResolvedConfig
from utils.llm_defaults import resolve_llm_defaults

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def load_book_config(book_dir: Path) -> BookConfig:
    path = book_dir / "book.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"No book.yaml found in {book_dir}.\n"
            "Create one with at least:\n\n"
            "  category: novel  # childrens | novel | fantasy | factual | scifi\n"
        )
    with open(path) as f:
        return BookConfig.model_validate(yaml.safe_load(f) or {})


def load_template(category: str) -> CategoryTemplate:
    path = TEMPLATES_DIR / f"{category}.yaml"
    if not path.exists():
        available = [p.stem for p in sorted(TEMPLATES_DIR.glob("*.yaml"))]
        raise FileNotFoundError(
            f"No template for category '{category}'. Available: {available}"
        )
    with open(path) as f:
        return CategoryTemplate.model_validate(yaml.safe_load(f))


def _apply_overrides(base: LLMConfig, overrides: BookLLMOverrides) -> LLMConfig:
    data = base.model_dump()
    data.update(overrides.model_dump(exclude_none=True))
    return LLMConfig.model_validate(data)


def load_config(book_dir: Path, model_override: str | None = None) -> tuple[BookConfig, ResolvedConfig]:
    book_cfg = load_book_config(book_dir)
    template = load_template(book_cfg.category)

    # Merge order (low → high priority):
    #   1. category template
    #   2. LLM defaults (llm_defaults.json, keyed by model × category)
    #   3. book.yaml llm: overrides
    model = model_override or book_cfg.model or os.getenv("MODEL_NAME", "")
    base_llm = template.llm
    if model:
        llm_defs = resolve_llm_defaults(model, book_cfg.category)
        if llm_defs:
            base_llm = _apply_overrides(base_llm, llm_defs)

    resolved = ResolvedConfig(
        llm=_apply_overrides(base_llm, book_cfg.llm),
        base_llm=base_llm,
        prompts=template.prompts,
        template=template,
    )
    return book_cfg, resolved
