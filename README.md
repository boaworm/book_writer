# book-writer

Turn a story outline into a full book using a local or cloud LLM.

## How it works

1. Write a `outline.yaml` for your book in `books/<your_book>/`
2. Run the tool — it writes each chapter as a separate Markdown file
3. A stitched `book.md` is produced when all chapters are done

## Setup

```bash
pip install -e .
cp .env.example .env
# edit .env with your model settings
```

### Local LLM (Ollama)

```bash
ollama pull llama3
```

In `.env`:
```
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
MODEL_NAME=llama3
```

### OpenAI

In `.env`:
```
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o
```

## Writing your book

Create a directory for your book and add an outline:

```
books/
└── my_story/
    └── outline.yaml
```

See `books/example_book/outline.yaml` for the full outline format. The outline defines:

- **title**, **author**, **genre**, **premise** — global book context
- **characters** — name, role, and description for each character
- **chapters** — each with a summary and a list of scenes to cover

## Running

```bash
python main.py books/my_story
```

Options:

```
python main.py books/my_story --model mistral
python main.py books/my_story --base-url http://localhost:11434/v1
```

## Output

Generated files land in `books/my_story/output/`:

```
output/
├── 01_the_weight_of_ash.md
├── 02_first_lessons.md
└── book.md                   ← full book
```

Each chapter file is standalone Markdown. `book.md` stitches them all together with dividers.
