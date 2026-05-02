# book-writer — Claude Code Reference

## Working rules

- Never pipe command output into `tail`, `head`, or `grep` — it hides what's happening. Using them directly on files is fine.
- If a command produces long output that needs filtering, pipe through `tee tmp/out.txt` first, then read the file.
- Never use `/tmp`. All temporary files go in the local `tmp/` directory.

## Project layout

```
book_writer/
├── main.py                      # CLI entry point
├── models/
│   ├── outline.py               # StoryOutline, Chapter, Scene, Character (pure story)
│   ├── book_config.py           # BookConfig, BookLLMOverrides (per-book generation config)
│   └── config.py                # LLMConfig, CategoryTemplate, ResolvedConfig (internal)
├── chains/chapter_writer.py     # LangChain LCEL chain for prose generation
├── utils/
│   ├── config_loader.py         # loads book.yaml + template, merges into ResolvedConfig
│   ├── file_handler.py          # outline loading, chapter writing, book stitching
│   ├── versioning.py            # snapshot management (versions/vN/)
│   └── differ.py                # outline + book diffing via difflib + rich
├── templates/                   # category templates (fantasy, novel, childrens, factual, scifi)
├── books/
│   └── <book_name>/
│       ├── book.yaml            # generation config: category, model, optional LLM overrides
│       ├── outline.yaml         # story content: title, premise, characters, chapters
│       ├── output/              # generated files (gitignored)
│       │   ├── 01_<title>.md
│       │   └── book.md
│       └── versions/            # snapshots before each regeneration (gitignored)
│           └── vN/
│               ├── book.yaml
│               ├── outline.yaml
│               └── book.md
├── pyproject.toml
└── .env
```

## CLI

```bash
# Generate (or regenerate — snapshots previous output first)
python main.py --generate books/my_story
python main.py --generate books/my_story --model llama3
python main.py --generate books/my_story --base-url http://localhost:11434/v1

# Analyze: show story stats + resolved generation parameters
python main.py --analyze books/my_story

# Diff: latest version vs current (default)
python main.py --diff books/my_story
python main.py --diff books/my_story --from-version v1 --to-version v2

# List saved versions
python main.py --versions books/my_story
```

## Config hierarchy (low → high priority)

1. Category template (`templates/<category>.yaml`) — LLM params + style prompt
2. Book overrides (`books/<name>/book.yaml` → `llm:` block)
3. CLI flags (`--model`, `--base-url`)
4. `.env` / environment variables

## book.yaml fields

| Field      | Default   | Description                              |
|------------|-----------|------------------------------------------|
| `category` | `novel`   | template to use                          |
| `model`    | from .env | model name (e.g. `llama3`, `gpt-4o`)    |
| `base_url` | from .env | LLM endpoint (set for Ollama etc.)       |
| `llm.*`    | template  | optional per-book parameter overrides    |

## outline.yaml fields

Pure story content only — no generation config here.

| Field        | Required | Description                   |
|--------------|----------|-------------------------------|
| `title`      | yes      | book title                    |
| `author`     | yes      | author name                   |
| `genre`      | yes      | genre label (free text)       |
| `premise`    | yes      | one-paragraph story premise   |
| `characters` | yes      | list of name/role/description |
| `chapters`   | yes      | list of number/title/summary/scenes |

## Templates (`templates/<category>.yaml`)

Each template defines `llm` params and `prompts.style_notes` (injected into system prompt).
Available: `childrens`, `novel`, `fantasy`, `factual`, `scifi`.
To add a new category, drop a new `.yaml` into `templates/`.

## Versioning

`snapshot_current()` runs before each `--generate`. It copies `outline.yaml`, `book.yaml`,
and `output/book.md` into `versions/vN/`. The first run produces no snapshot.
`--diff` uses `difflib.unified_diff` rendered with `rich` colors.

## LLM setup

Uses `langchain-openai` which works with both OpenAI and any OpenAI-compatible endpoint
(Ollama, LM Studio, etc.) — just set `base_url` in `book.yaml` or `.env`.

## Dependencies

Python 3.13. Install: `pip install -e .`
