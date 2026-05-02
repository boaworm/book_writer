# book-writer

Turn a story outline into a full book using a local or cloud LLM.

You create a book directory with two files — `outline.yaml` (the story) and `book.yaml` (how
to generate it) — and the tool does the rest, including picking up all LLM parameters,
writing style, and world context automatically.

## Setup

```bash
pip install -e .
cp .env.example .env
# edit .env with your backend URL and model name
```

`.env` holds your connection settings:

```
OPENAI_BASE_URL=http://localhost:11434/v1   # Ollama, llama.cpp, or any OpenAI-compatible endpoint
OPENAI_API_KEY=not-needed                   # use your real key for OpenAI
MODEL_NAME=llama3                           # model name as your backend expects it
```

---

## Book directory structure

Every book lives in `books/<name>/` and needs two files:

```
books/my_story/
├── book.yaml       ← generation config: category, style, universe, LLM overrides
└── outline.yaml    ← story content: title, premise, characters, chapters
```

Output lands in `books/my_story/output/` and snapshots are saved to
`books/my_story/versions/` before each regeneration.

---

## book.yaml — generation config

Controls everything about *how* the book is written. Only `category` is required.

### Full reference

```yaml
# ── Identity ──────────────────────────────────────────────────────────────────

category: fantasy
# Required. Loads a template from templates/<category>.yaml which sets LLM
# defaults and injects a style prompt into every chapter.
# Values: fantasy | novel | scifi | childrens | factual
# Default: novel

writing_style: "JRR Tolkien"
# Optional. Emulate a named author's prose style. Well-known authors get a
# curated style description; unknown names are passed to the model as-is.
# Examples: "Ernest Hemingway", "Cormac McCarthy", "Ursula K Le Guin"

universe: "Middle Earth"
# Optional (simple form). Ground the story in a known world. The tool injects
# world context (geography, tone, canon rules) into every chapter prompt.

universe:
  name: "The Shattered Realm"
  description: "A world fractured into floating islands after a magical war."
# Optional (custom form). Provide your own world description.

# ── Backend ───────────────────────────────────────────────────────────────────

model: llama3
# Optional. Overrides MODEL_NAME from .env for this book only.

base_url: http://localhost:11434/v1
# Optional. Overrides OPENAI_BASE_URL from .env for this book only.

# ── LLM parameter overrides ───────────────────────────────────────────────────
# All optional. Each overrides the corresponding value from the category template.

llm:
  temperature: 0.85
  # Controls randomness. Higher = more creative/unpredictable.
  # Typical range: 0.4 (factual) – 1.2 (creative). Default: from template.

  max_tokens: 4000
  # Maximum tokens the model may generate per chapter.
  # Higher = longer chapters but slower. Default: from template (often 2500–4000).

  top_p: 0.95
  # Nucleus sampling. Only the top_p probability mass of tokens is considered.
  # Lower = more focused. Range: 0.0–1.0. Default: from template.

  frequency_penalty: 0.1
  # Penalises tokens that have already appeared, reducing repetition.
  # Range: -2.0–2.0. Positive values reduce repetition. Default: from template.

  presence_penalty: 0.1
  # Penalises all tokens that have appeared at all, encouraging new topics.
  # Range: -2.0–2.0. Positive values broaden vocabulary. Default: from template.

  top_k: 100
  # (llama.cpp / Ollama only) Limits sampling to the top K most likely tokens.
  # Lower = more conservative. Not supported by OpenAI. Default: unset.

  min_p: 0.09
  # (llama.cpp / Ollama only) Minimum probability threshold relative to the top
  # token. Filters out very unlikely tokens. Default: unset.
```

### How parameters are resolved

Parameters flow through a layered stack — each layer overrides the one below:

```
.env                         model name, backend URL
  └── category template      temperature, max_tokens, top_p, penalties, style prompt
        └── book.yaml llm:   per-book overrides on any of the above
              └── CLI flags  --model, --base-url (highest priority)
```

Run `--analyze books/my_story` to see every active value and its source:

```
Generation Parameters
temperature        1.2   book override
max_tokens         4000  template
top_p              0.9   book override
frequency_penalty  0.85  book override
presence_penalty   0.3   book override
top_k              100   book override
min_p              0.09  book override
```

---

## Category templates

The `category` field loads a template from `templates/`. Templates set LLM defaults and
inject a writing style prompt tailored to the genre into every chapter:

| Category    | Temperature | Max tokens | Character |
|-------------|-------------|------------|-----------|
| `fantasy`   | 0.85        | 4000       | Epic world-building, mythic weight, elevated language |
| `novel`     | 0.75        | 3000       | Literary depth, interiority, subtext, varied rhythm |
| `scifi`     | 0.80        | 3500       | Scientific plausibility balanced with human drama |
| `childrens` | 0.65        | 1500       | Simple vocabulary, short chapters, wonder and heart |
| `factual`   | 0.40        | 2500       | Precision, clear argument, no embellishment |

To add a new category, create `templates/<name>.yaml` — no code changes needed.

---

## Writing style

`writing_style` emulates a named author. Well-known authors get a curated description
passed to the model; any other name is passed through and the model infers the style.

Built-in authors with curated descriptions:

| Author | Style |
|--------|-------|
| JRR Tolkien | Epic and mythic, rich lore, archaic cadence, deep world-building |
| Ernest Hemingway | Iceberg theory, short declarative sentences, subtext-heavy dialogue |
| George RR Martin | Morally complex, multiple POV, political intrigue, no plot armour |
| Cormac McCarthy | Sparse punctuation, biblical cadence, brutal and lyrical |
| Terry Pratchett | Satirical wit, humanist warmth, comic timing |
| Ursula K Le Guin | Anthropological depth, philosophical weight, precise prose |
| Stephen King | Colloquial voice, slow-burn dread, strong interiority |
| Jane Austen | Sharp irony, free indirect discourse, social observation |
| Philip K Dick | Paranoid and philosophical, pulpy pacing, identity and reality |
| Neil Gaiman | Mythic storytelling, dark fairy-tale atmosphere, warm narrative voice |
| Dostoevsky | Intense psychological depth, suffering, characters who philosophise |
| Gabriel Garcia Marquez | Magical realism, multi-generational sweep, dense sensory prose |
| Franz Kafka | Bureaucratic surrealism, deadpan alienation, no resolution |
| Virginia Woolf | Stream of consciousness, lyrical and impressionistic, subjective time |

---

## Universe

`universe` grounds the story in an established world. Known universes inject world
context (geography, factions, magic rules, tone, canon) into every chapter prompt.

Built-in universes:

| Universe | Type |
|----------|------|
| Middle Earth | Fantasy (Tolkien) |
| Star Wars | Sci-fi / space opera |
| The Belgariad | Fantasy (Eddings) |
| Westeros | Fantasy (GRRM) |
| Discworld | Comic fantasy (Pratchett) |
| Dune | Sci-fi (Herbert) |
| Wizarding World | Fantasy (Rowling) |
| Forgotten Realms | D&D high fantasy |
| Medieval England | Historical, ~1000–1485 CE |
| Victorian London | Historical, ~1837–1901 |
| Ancient Rome | Historical, ~500 BCE – 500 CE |
| Feudal Japan | Historical, ~1185–1868 |
| Wild West | Historical, ~1865–1900 |
| World War II | Historical, 1939–1945 |
| Golden Age of Piracy | Historical, ~1650–1730 |
| Ancient Greece | Historical, ~800–300 BCE |

Aliases are supported: "Tolkien", "LOTR", "Lord of the Rings" all resolve to Middle Earth;
"WWII", "WW2", "World War 2" all resolve to World War II; "D&D" resolves to Forgotten Realms.

For a custom world:

```yaml
universe:
  name: "The Shattered Realm"
  description: "A world fractured into floating islands after a catastrophic magical war 300 years ago."
```

---

## outline.yaml — story content

Pure story content — no generation config here.

### Full reference

```yaml
# ── Book metadata ─────────────────────────────────────────────────────────────

title: "The Long Watch"       # required
author: "Your Name"           # required
genre: "Fantasy"              # required — free text, used in the generation prompt
premise: |                    # required — one or more paragraphs describing the core
  A Dúnedain ranger is posted alone to the south-western marches of the Shire
  by order of Aragorn, and must hold a growing darkness at bay.

# ── Characters ────────────────────────────────────────────────────────────────

characters:                   # required — at least one
  - name: "Aldric"            # required
    role: protagonist         # required — free text (protagonist, antagonist, supporting, etc.)
    description: |            # required — personality, background, arc
      A young Dúnedain ranger on his first extended solo posting. Capable but
      still testing the edge of his courage.

  - name: "Aragorn"
    role: mentor
    description: |
      The Chieftain of the Dúnedain, wandering as Strider. Appears briefly
      to assign the watch. Speaks little but carries enormous weight.

# ── Chapters ──────────────────────────────────────────────────────────────────

chapters:                     # required — at least one
  - number: 1                 # required — integer, used for file naming and ordering
    title: "The Chieftain's Word"   # required
    summary: |                # required — what happens in this chapter (feeds the prompt)
      Aragorn assembles rangers at Weathertop. Aldric is assigned the
      south-western Shire patrol, alone, with no explanation given.
    scenes:                   # optional but strongly recommended
      - title: "The Gathering"       # required per scene
        description: |              # required per scene — specific beat to cover
          Rangers arrive at Weathertop at dusk. Aragorn speaks about
          orc movements. The tone is matter-of-fact, stakes enormous.
      - title: "The Assignment"
        description: |
          Aldric expects a partner. He is sent alone. He does not question
          it, but the descent from Weathertop in the dark is a long one.
```

**Tips:**
- `premise` is injected into every chapter prompt as global context — make it specific.
- `characters` are listed in full in every chapter prompt — descriptions shape how the model portrays them throughout the book.
- `summary` tells the model what must happen in the chapter; `scenes` tell it the order and detail of individual beats. Chapters without scenes produce more improvised prose.
- Use block scalars (`|`) for any multi-line text — run `--clean-up` to normalise formatting.

---

## Commands

All commands take the book directory as their argument:

```bash
# Generate (or regenerate) the full book
python main.py --generate books/my_story

# Regenerate a single chapter without rewriting the rest
python main.py --regenerate-chapter books/my_story --chapter 3

# Export the finished book to PDF
python main.py --export-pdf books/my_story

# Show resolved config, active LLM parameters (and their sources), and outline stats
python main.py --analyze books/my_story

# LLM-powered editorial critique of the outline structure
python main.py --critique books/my_story

# Lint and reformat outline.yaml (backs up original to outline.yaml.bak)
python main.py --clean-up books/my_story

# Diff outline and generated book between versions
python main.py --diff books/my_story
python main.py --diff books/my_story --from-version v1 --to-version v2

# List saved version snapshots
python main.py --versions books/my_story
```

`--model` and `--base-url` can be added to any command that calls the LLM
(`--generate`, `--regenerate-chapter`, `--critique`) to override `.env` and `book.yaml`.

---

## Output structure

```
books/my_story/
├── book.yaml
├── outline.yaml
├── output/
│   ├── 01_the_chieftains_word.md    ← one file per chapter
│   ├── 02_the_green_borders.md
│   ├── book.md                      ← full stitched book (Markdown)
│   └── book.pdf                     ← after running --export-pdf
└── versions/
    └── v1/                          ← snapshot taken before each regeneration
        ├── book.yaml
        ├── outline.yaml
        └── book.md
```
