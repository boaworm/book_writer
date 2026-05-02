from pathlib import Path

import yaml

from models.outline import StoryOutline

# ── YAML helpers ─────────────────────────────────────────────────────────────

class _Literal(str):
    """Marker that makes PyYAML emit block-literal style (|) for this string."""


def _literal_representer(dumper: yaml.Dumper, data: "_Literal") -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class _CleanDumper(yaml.Dumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow=flow, indentless=False)

_CleanDumper.add_representer(_Literal, _literal_representer)

_BLOCK_THRESHOLD = 60  # chars — prose longer than this gets block-literal style


def _prose(s: str) -> "str | _Literal":
    """Use block-literal for multi-line or long prose; plain string for short identifiers."""
    s = s.strip()
    return _Literal(s) if (len(s) > _BLOCK_THRESHOLD or "\n" in s) else s


# ── Canonical dict builder ────────────────────────────────────────────────────

def _to_dict(outline: StoryOutline) -> dict:
    """Rebuild outline as an ordered dict with canonical field ordering."""
    return {
        "title": outline.title,
        "author": outline.author,
        "genre": outline.genre,
        "premise": _Literal(outline.premise.strip()),  # always block
        "characters": [
            {
                "name": c.name,
                "role": c.role,
                "description": _prose(c.description),
            }
            for c in outline.characters
        ],
        "chapters": [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": _prose(ch.summary),
                **({
                    "scenes": [
                        {
                            "title": s.title,
                            "description": _prose(s.description),
                        }
                        for s in ch.scenes
                    ]
                } if ch.scenes else {}),
            }
            for ch in outline.chapters
        ],
    }


def canonical_yaml(outline: StoryOutline) -> str:
    return yaml.dump(
        _to_dict(outline),
        Dumper=_CleanDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=4096,   # don't wrap prose lines — preserve content exactly
        indent=2,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def clean_outline(book_dir: Path) -> tuple[str, str, StoryOutline | None]:
    """
    Returns (original_text, canonical_text, outline_or_None).
    outline_or_None is None if the file failed to parse.
    """
    path = book_dir / "outline.yaml"
    original = path.read_text()
    try:
        outline = StoryOutline.model_validate(yaml.safe_load(original))
    except Exception as exc:
        return original, "", None
    return original, canonical_yaml(outline), outline
