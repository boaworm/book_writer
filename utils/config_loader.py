from pathlib import Path

import yaml

from models.book_config import BookConfig
from models.config import CategoryTemplate, LLMConfig, ResolvedConfig

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


def _merge_llm(base: LLMConfig, overrides: BookConfig) -> LLMConfig:
    data = base.model_dump()
    data.update(overrides.llm.model_dump(exclude_none=True))
    return LLMConfig.model_validate(data)


def load_config(book_dir: Path) -> tuple[BookConfig, ResolvedConfig]:
    book_cfg = load_book_config(book_dir)
    template = load_template(book_cfg.category)
    resolved = ResolvedConfig(
        llm=_merge_llm(template.llm, book_cfg),
        prompts=template.prompts,
        template=template,
    )
    return book_cfg, resolved
