import argparse
import os
import sys
import textwrap
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.table import Table

from chains.chapter_writer import build_chapter_chain
from chains.critique import CATEGORY_CHECKS, build_critique_chain
from models.config import LLMConfig
from utils.config_loader import load_config
from utils.differ import show_diff
from utils.file_handler import (
    format_characters,
    format_previous_summaries,
    format_scenes,
    load_outline,
    stitch_book,
    write_chapter,
)
from utils.outline_cleaner import clean_outline
from utils.universes import resolve_universe
from utils.versioning import list_versions, snapshot_current
from utils.writing_styles import resolve_writing_style

console = Console()


def _build_llm(
    model: str,
    base_url: str | None,
    llm_cfg: LLMConfig | None = None,
    temperature_override: float | None = None,
) -> ChatOpenAI:
    cfg = llm_cfg or LLMConfig()
    temperature = temperature_override if temperature_override is not None else cfg.temperature

    # top_k and min_p are llama.cpp-specific — the OpenAI client rejects unknown
    # fields, so we route them through extra_body which bypasses schema validation.
    extra_body: dict = {}
    if cfg.top_k is not None:
        extra_body["top_k"] = cfg.top_k
    if cfg.min_p is not None:
        extra_body["min_p"] = cfg.min_p

    return ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
        temperature=temperature,
        max_tokens=cfg.max_tokens,
        top_p=cfg.top_p,
        frequency_penalty=cfg.frequency_penalty,
        presence_penalty=cfg.presence_penalty,
        **({"extra_body": extra_body} if extra_body else {}),
    )


def _resolve_book_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_dir():
        console.print(f"[red]Directory not found:[/red] {path}")
        sys.exit(1)
    return path


def cmd_analyze(book_path: Path) -> None:
    try:
        outline = load_outline(book_path)
        book_cfg, resolved = load_config(book_path)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    template = resolved.template
    llm = resolved.llm
    book_llm = book_cfg.llm.model_dump(exclude_none=True)
    model_display = book_cfg.model or os.getenv("MODEL_NAME", "gpt-4o")
    from utils.llm_defaults import matched_model_key, resolve_llm_defaults
    llm_defaults_key = matched_model_key(model_display)
    _llm_defs_entry = resolve_llm_defaults(model_display, book_cfg.category) if llm_defaults_key else None
    _llm_defs_fields = set(_llm_defs_entry.model_dump(exclude_none=True)) if _llm_defs_entry else set()

    def src(field: str) -> str:
        if field in book_llm:
            default_val = getattr(resolved.base_llm, field)
            suffix = f" [dim](default = {default_val})[/dim]" if default_val is not None else ""
            return f"[yellow]book override[/yellow]{suffix}"
        if field in _llm_defs_fields:
            return "[cyan]llm defaults[/cyan]"
        return "[dim]template[/dim]"

    total_scenes = sum(len(ch.scenes) for ch in outline.chapters)

    console.print()
    console.rule(f"[bold]{outline.title}[/bold]")

    # Story table
    story = Table.grid(padding=(0, 2))
    story.add_column(style="bold")
    story.add_column()
    story.add_row("Title", outline.title)
    story.add_row("Author", outline.author)
    story.add_row("Genre", outline.genre)
    story.add_row("Chapters", str(len(outline.chapters)))
    story.add_row("Scenes", str(total_scenes))
    story.add_row("Characters", str(len(outline.characters)))
    book_md = book_path / "output" / "book.md"
    if book_md.exists():
        words = len(book_md.read_text().split())
        pct = words / 90_000 * 100
        story.add_row("Word count", f"{words:,}  [dim]({pct:.0f}% of a typical novel)[/dim]")
    console.print("\n[bold cyan]Story[/bold cyan]")
    console.print(story)

    # Characters list
    TYPE_STYLE = {"main": "bold yellow", "central": "cyan"}
    console.print("\n[bold cyan]Characters[/bold cyan]")
    for c in outline.characters:
        type_lower = c.type.lower()
        type_color = TYPE_STYLE.get(type_lower, "")
        type_tag = f"[{type_color}][{c.type.upper()}][/{type_color}]"
        alias_str = f"  [dim](alias: {c.alias})[/dim]" if c.alias else ""
        role_str = f"  [dim]{c.role}[/dim]" if c.role else ""
        console.print(f"  {type_tag}  [bold]{c.name}[/bold]{alias_str}{role_str}")
        desc_flat = " ".join(c.description.split())
        indent = "        "
        wrapped = textwrap.fill(desc_flat, width=console.width - len(indent),
                                initial_indent=indent, subsequent_indent=indent)
        console.print(wrapped)

    # Config table
    base_url_display = book_cfg.base_url or os.getenv("OPENAI_BASE_URL", "openai")
    cfg_table = Table.grid(padding=(0, 2))
    cfg_table.add_column(style="bold")
    cfg_table.add_column()
    cfg_table.add_column()
    cfg_table.add_row("Category", book_cfg.category, f"[dim]({template.name})[/dim]")
    cfg_table.add_row("Writing style", book_cfg.writing_style or "[dim]none[/dim]", "")
    universe_display = book_cfg.universe.name if book_cfg.universe else "[dim]none[/dim]"
    cfg_table.add_row("Universe", universe_display, "")
    cfg_table.add_row("Model", model_display, "")
    cfg_table.add_row("LLM defaults", llm_defaults_key or "[dim]none[/dim]", "")
    cfg_table.add_row("Backend", base_url_display, "")
    console.print("\n[bold cyan]Configuration[/bold cyan]")
    console.print(cfg_table)

    # LLM params table
    params = Table.grid(padding=(0, 2))
    params.add_column(style="bold")
    params.add_column()
    params.add_column()
    params.add_row("temperature",       str(llm.temperature),                  src("temperature"))
    params.add_row("max_tokens",        str(llm.max_tokens or "default"),      src("max_tokens"))
    params.add_row("top_p",             str(llm.top_p),                        src("top_p"))
    params.add_row("frequency_penalty", str(llm.frequency_penalty),            src("frequency_penalty"))
    params.add_row("presence_penalty",  str(llm.presence_penalty),             src("presence_penalty"))
    if llm.top_k is not None:
        params.add_row("top_k",         str(llm.top_k),                        src("top_k"))
    if llm.min_p is not None:
        params.add_row("min_p",         str(llm.min_p),                        src("min_p"))
    console.print("\n[bold cyan]Generation Parameters[/bold cyan]")
    console.print(params)

    # Versions
    vs = list_versions(book_path)
    has_output = (book_path / "output" / "book.md").exists()
    console.print("\n[bold cyan]Versions[/bold cyan]")
    if vs:
        console.print(f"  Saved: {', '.join(f'v{v}' for v in vs)}")
    else:
        console.print("  [dim]No saved versions yet[/dim]")
    console.print(f"  Current output: {'yes' if has_output else '[dim]none[/dim]'}")
    console.print()


def _print_generation_stats(
    outline,
    chapter_words: list[tuple[int, str, int]],
    total_elapsed: float,
) -> None:
    total_words = sum(w for _, _, w in chapter_words)
    reference_words = 90_000  # ~300-page novel at 250 words/page
    read_minutes = total_words / 250  # average adult reading speed

    table = Table(title="Generation Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Ch", justify="right", style="dim")
    table.add_column("Title")
    table.add_column("Words", justify="right")

    for num, title, words in chapter_words:
        table.add_row(str(num), title, f"{words:,}")
    table.add_section()
    table.add_row("", "[bold]Total[/bold]", f"[bold]{total_words:,}[/bold]")

    console.print()
    console.print(table)

    pct = total_words / reference_words * 100
    read_h, read_m = divmod(int(read_minutes), 60)
    elapsed_h, rem = divmod(int(total_elapsed), 3600)
    elapsed_m, elapsed_s = divmod(rem, 60)

    elapsed_str = (
        f"{elapsed_h}h {elapsed_m}m {elapsed_s}s" if elapsed_h
        else f"{elapsed_m}m {elapsed_s}s" if elapsed_m
        else f"{elapsed_s}s"
    )
    read_str = f"{read_h}h {read_m}m" if read_h else f"{read_m}m"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold")
    grid.add_column()
    grid.add_row("Generation time", elapsed_str)
    grid.add_row("Word count", f"{total_words:,}  [dim]({pct:.0f}% of a typical 300-page novel)[/dim]")
    grid.add_row("Reading time", f"~{read_str}  [dim](at 250 wpm)[/dim]")
    console.print(grid)


def cmd_generate(book_path: Path, model_override: str | None, base_url_override: str | None) -> None:
    try:
        outline = load_outline(book_path)
        book_cfg, resolved = load_config(book_path, model_override)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    snapshot = snapshot_current(book_path)
    if snapshot:
        console.print(f"[dim]Snapshot saved → {snapshot.relative_to(book_path)}[/dim]")

    llm_cfg = resolved.llm
    model = model_override or book_cfg.model or os.getenv("MODEL_NAME", "gpt-4o")
    base_url = base_url_override or book_cfg.base_url or os.getenv("OPENAI_BASE_URL")

    console.print(f"\n[bold]Book:[/bold]     {outline.title}")
    console.print(f"[bold]Category:[/bold] {book_cfg.category}")
    console.print(f"[bold]Chapters:[/bold] {len(outline.chapters)}")
    console.print(
        f"[bold]Model:[/bold]    {model}  "
        f"[dim](temp={llm_cfg.temperature}, "
        f"max_tokens={llm_cfg.max_tokens or 'default'})[/dim]\n"
    )

    llm = _build_llm(model, base_url, llm_cfg)
    chain = build_chapter_chain(llm)
    writing_style_note = resolve_writing_style(book_cfg.writing_style) if book_cfg.writing_style else ""
    universe_note = resolve_universe(book_cfg.universe) if book_cfg.universe else ""
    previous_summaries: list[str] = []
    chapter_words: list[tuple[int, str, int]] = []

    gen_start = time.time()
    total = len(outline.chapters)
    for i, chapter in enumerate(outline.chapters, 1):
        label = f"[{i}/{total}] Chapter {chapter.number}: {chapter.title}"
        with console.status(f"{label}…", spinner="dots"):
            t0 = time.time()
            content = chain.invoke({
                "genre": outline.genre,
                "style_notes": resolved.prompts.style_notes,
                "writing_style_note": writing_style_note,
                "universe_note": universe_note,
                "title": outline.title,
                "premise": outline.premise,
                "characters": format_characters(outline.characters),
                "previous_context": format_previous_summaries(previous_summaries),
                "chapter_number": chapter.number,
                "chapter_title": chapter.title,
                "chapter_summary": chapter.summary,
                "scenes": format_scenes(chapter.scenes),
            })
            elapsed = time.time() - t0
        console.print(f"  [green]✓[/green] {label} [dim]({elapsed:.0f}s)[/dim]")
        write_chapter(book_path, chapter.number, chapter.title, content)
        chapter_words.append((chapter.number, chapter.title, len(content.split())))
        previous_summaries.append(
            f"Chapter {chapter.number} ({chapter.title}): {chapter.summary}"
        )

    book_file = stitch_book(book_path, outline)
    console.print(f"\n[green]Done![/green] Full book at: {book_file}")
    _print_generation_stats(outline, chapter_words, time.time() - gen_start)


def cmd_regenerate_chapter(
    book_path: Path, chapter_number: int, model_override: str | None, base_url_override: str | None
) -> None:
    try:
        outline = load_outline(book_path)
        book_cfg, resolved = load_config(book_path, model_override)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    chapter = next((ch for ch in outline.chapters if ch.number == chapter_number), None)
    if chapter is None:
        nums = [ch.number for ch in outline.chapters]
        console.print(f"[red]Chapter {chapter_number} not found.[/red] Available: {nums}")
        sys.exit(1)

    model = model_override or book_cfg.model or os.getenv("MODEL_NAME", "gpt-4o")
    base_url = base_url_override or book_cfg.base_url or os.getenv("OPENAI_BASE_URL")
    llm = _build_llm(model, base_url, resolved.llm)
    chain = build_chapter_chain(llm)

    writing_style_note = resolve_writing_style(book_cfg.writing_style) if book_cfg.writing_style else ""
    universe_note = resolve_universe(book_cfg.universe) if book_cfg.universe else ""

    previous_summaries = [
        f"Chapter {ch.number} ({ch.title}): {ch.summary}"
        for ch in outline.chapters
        if ch.number < chapter_number
    ]

    label = f"Chapter {chapter.number}: {chapter.title}"
    with console.status(f"Regenerating {label}…", spinner="dots"):
        t0 = time.time()
        content = chain.invoke({
            "genre": outline.genre,
            "style_notes": resolved.prompts.style_notes,
            "writing_style_note": writing_style_note,
            "universe_note": universe_note,
            "title": outline.title,
            "premise": outline.premise,
            "characters": format_characters(outline.characters),
            "previous_context": format_previous_summaries(previous_summaries),
            "chapter_number": chapter.number,
            "chapter_title": chapter.title,
            "chapter_summary": chapter.summary,
            "scenes": format_scenes(chapter.scenes),
        })
        elapsed = time.time() - t0

    console.print(f"  [green]✓[/green] {label} [dim]({elapsed:.0f}s)[/dim]")
    write_chapter(book_path, chapter.number, chapter.title, content)
    book_file = stitch_book(book_path, outline)
    console.print(f"Book re-stitched at: {book_file}")


def cmd_export_pdf(book_path: Path) -> None:
    from utils.pdf_exporter import export_pdf

    try:
        with console.status("Exporting PDF…", spinner="dots"):
            pdf_path = export_pdf(book_path)
        console.print(f"[green]✓[/green] PDF exported: {pdf_path}")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]PDF export failed:[/red] {e}")
        sys.exit(1)


def cmd_critique(book_path: Path, model_override: str | None, base_url_override: str | None) -> None:
    import yaml

    try:
        outline = load_outline(book_path)
        book_cfg, resolved = load_config(book_path, model_override)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    model = model_override or book_cfg.model or os.getenv("MODEL_NAME", "gpt-4o")
    base_url = base_url_override or book_cfg.base_url or os.getenv("OPENAI_BASE_URL")
    category = book_cfg.category

    llm = _build_llm(model, base_url, temperature_override=0.3)
    chain = build_critique_chain(llm)

    outline_yaml = (book_path / "outline.yaml").read_text()
    scenes_per_chapter = ", ".join(
        f"ch{ch.number}:{len(ch.scenes)}" for ch in outline.chapters
    )

    console.print(f"\n[dim]Critiquing outline with {model}...[/dim]")
    result = chain.invoke({
        "category": category,
        "category_description": resolved.template.description,
        "category_specific_checks": CATEGORY_CHECKS.get(category, "Apply general editorial standards."),
        "chapter_count": len(outline.chapters),
        "total_scenes": sum(len(ch.scenes) for ch in outline.chapters),
        "character_count": len(outline.characters),
        "scenes_per_chapter": scenes_per_chapter,
        "outline_yaml": outline_yaml,
    })

    # Header
    console.print()
    console.rule(f"[bold]Critique: {outline.title}[/bold]")

    score_color = "green" if result.score >= 7 else "yellow" if result.score >= 4 else "red"
    console.print(f"\n[bold]Overall score:[/bold] [{score_color}]{result.score}/10[/{score_color}]")
    console.print(f"[italic]{result.overall_assessment}[/italic]\n")

    if not result.issues:
        console.print("[green]No issues found.[/green]")
        return

    SEVERITY_STYLE = {
        "critical":   ("red",    "✗"),
        "warning":    ("yellow", "⚠"),
        "suggestion": ("cyan",   "→"),
    }

    # Group by area
    by_area: dict[str, list] = {}
    for issue in result.issues:
        by_area.setdefault(issue.area, []).append(issue)

    # Sort: critical areas first
    severity_order = {"critical": 0, "warning": 1, "suggestion": 2}
    sorted_areas = sorted(
        by_area.items(),
        key=lambda kv: min(severity_order[i.severity] for i in kv[1]),
    )

    for area, issues in sorted_areas:
        console.print(f"[bold]{area}[/bold]")
        for issue in sorted(issues, key=lambda i: severity_order[i.severity]):
            color, icon = SEVERITY_STYLE[issue.severity]
            console.print(f"  [{color}]{icon}[/{color}] {issue.issue}")
            console.print(f"    [dim]→ {issue.recommendation}[/dim]")
        console.print()


def cmd_cleanup(book_path: Path) -> None:
    import difflib
    import shutil

    outline_path = book_path / "outline.yaml"
    if not outline_path.exists():
        console.print(f"[red]No outline.yaml found in {book_path}[/red]")
        sys.exit(1)

    original, cleaned, outline = clean_outline(book_path)

    if outline is None:
        console.print("[red]outline.yaml failed to parse — fix structural errors before cleaning.[/red]")
        sys.exit(1)

    if original == cleaned:
        console.print("[green]outline.yaml is already clean.[/green]")
        return

    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        cleaned.splitlines(keepends=True),
        fromfile="outline.yaml  (before)",
        tofile="outline.yaml  (after)",
    ))

    console.print("\n[bold cyan]Changes[/bold cyan]")
    for line in diff:
        s = line.rstrip()
        if line.startswith("+++") or line.startswith("---"):
            console.print(f"[bold]{s}[/bold]")
        elif line.startswith("+"):
            console.print(f"[green]{s}[/green]")
        elif line.startswith("-"):
            console.print(f"[red]{s}[/red]")
        elif line.startswith("@@"):
            console.print(f"[yellow]{s}[/yellow]")
        else:
            console.print(f"[dim]{s}[/dim]")

    shutil.copy2(outline_path, outline_path.with_name("outline.yaml.bak"))
    outline_path.write_text(cleaned)
    console.print("\n[green]✓[/green] outline.yaml cleaned  [dim](original → outline.yaml.bak)[/dim]")


def cmd_diff(book_path: Path, from_version: str | None, to_version: str | None) -> None:
    show_diff(book_path, from_version, to_version, console)


def cmd_versions(book_path: Path) -> None:
    vs = list_versions(book_path)
    if not vs:
        console.print("[dim]No versions yet.[/dim]")
        return
    for v in vs:
        console.print(f"  v{v}")
    console.print("  [bold]current[/bold]  (working copy)")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Book writer — generate books from outlines")
    parser.add_argument("--model", help="Override model (e.g. llama3, gpt-4o)")
    parser.add_argument("--base-url", help="Override LLM base URL")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate",            metavar="BOOK_DIR", help="Generate or regenerate the full book")
    group.add_argument("--regenerate-chapter",  metavar="BOOK_DIR", help="Regenerate a single chapter (use with --chapter N)")
    group.add_argument("--export-pdf",          metavar="BOOK_DIR", help="Export output/book.md to output/book.pdf")
    group.add_argument("--analyze",             metavar="BOOK_DIR", help="Show book config and outline stats")
    group.add_argument("--critique",            metavar="BOOK_DIR", help="Critique the outline for structural problems")
    group.add_argument("--clean-up",            metavar="BOOK_DIR", help="Lint and reformat outline.yaml in place")
    group.add_argument("--diff",                metavar="BOOK_DIR", help="Diff outline and book across versions")
    group.add_argument("--versions",            metavar="BOOK_DIR", help="List saved versions")

    parser.add_argument("--chapter",       metavar="N",       type=int, help="Chapter number for --regenerate-chapter")
    parser.add_argument("--from-version", metavar="VERSION", help="Diff: source version (e.g. v1)")
    parser.add_argument("--to-version",   metavar="VERSION", help="Diff: target version (default: current)")

    args = parser.parse_args()

    if args.generate:
        cmd_generate(_resolve_book_path(args.generate), args.model, args.base_url)
    elif args.regenerate_chapter:
        if not args.chapter:
            console.print("[red]--regenerate-chapter requires --chapter N[/red]")
            sys.exit(1)
        cmd_regenerate_chapter(
            _resolve_book_path(args.regenerate_chapter), args.chapter, args.model, args.base_url
        )
    elif args.export_pdf:
        cmd_export_pdf(_resolve_book_path(args.export_pdf))
    elif args.analyze:
        cmd_analyze(_resolve_book_path(args.analyze))
    elif args.critique:
        cmd_critique(_resolve_book_path(args.critique), args.model, args.base_url)
    elif args.clean_up:
        cmd_cleanup(_resolve_book_path(args.clean_up))
    elif args.diff:
        cmd_diff(_resolve_book_path(args.diff), args.from_version, args.to_version)
    elif args.versions:
        cmd_versions(_resolve_book_path(args.versions))


if __name__ == "__main__":
    main()
