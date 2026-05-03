from pathlib import Path
import yaml
from models.outline import StoryOutline, Character, Scene, Chapter


def load_outline(book_dir: Path) -> StoryOutline:
    outline_path = book_dir / "outline.yaml"
    if not outline_path.exists():
        raise FileNotFoundError(f"No outline.yaml found in {book_dir}")
    with open(outline_path) as f:
        data = yaml.safe_load(f)
    return StoryOutline.model_validate(data)


def write_chapter(book_dir: Path, number: int, title: str, content: str) -> Path:
    output_dir = book_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = title.lower().replace(" ", "_").replace("/", "-")
    filename = f"{number:02d}_{slug}.md"
    path = output_dir / filename
    with open(path, "w") as f:
        f.write(f"# Chapter {number}: {title}\n\n")
        f.write(content.strip())
        f.write("\n")
    return path


def stitch_book(book_dir: Path, outline: StoryOutline) -> Path:
    output_dir = book_dir / "output"
    chapter_files = sorted(output_dir.glob("[0-9][0-9]_*.md"))
    book_path = output_dir / "book.md"
    with open(book_path, "w") as out:
        out.write(f"# {outline.title}\n\n")
        out.write(f"*by {outline.author}*\n\n---\n\n")
        for chapter_file in chapter_files:
            out.write(chapter_file.read_text())
            out.write("\n---\n\n")
    return book_path


def format_characters(characters: list[Character]) -> str:
    lines: list[str] = []
    main = [c for c in characters if c.type.lower() == "main"]
    central = [c for c in characters if c.type.lower() != "main"]

    def _char_line(c: Character) -> str:
        alias = f' (known as "{c.alias}")' if c.alias else ""
        role = f" — {c.role}" if c.role else ""
        return f"  {c.name}{alias}{role}: {c.description}"

    if main:
        lines.append("Main characters (the story revolves around these):")
        lines.extend(_char_line(c) for c in main)
    if central:
        if main:
            lines.append("")
        lines.append("Central characters (significant recurring figures with backstory):")
        lines.extend(_char_line(c) for c in central)

    return "\n".join(lines)


def format_scenes(scenes: list[Scene]) -> str:
    return "\n".join(
        f"{i + 1}. {s.title}: {s.description}" for i, s in enumerate(scenes)
    )


def format_previous_summaries(summaries: list[str]) -> str:
    if not summaries:
        return ""
    joined = "\n".join(summaries)
    return f"Story so far:\n{joined}\n\n"
