import difflib
from pathlib import Path

from rich.console import Console

from utils.versioning import get_version_dir, list_versions


def _read(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text().splitlines(keepends=True)


def _render_diff(diff_lines: list[str], console: Console, label: str) -> None:
    console.print(f"\n[bold cyan]{label}[/bold cyan]")
    if not diff_lines:
        console.print("[dim]  No changes.[/dim]")
        return
    for line in diff_lines:
        stripped = line.rstrip()
        if line.startswith("+++") or line.startswith("---"):
            console.print(f"[bold]{stripped}[/bold]")
        elif line.startswith("+"):
            console.print(f"[green]{stripped}[/green]")
        elif line.startswith("-"):
            console.print(f"[red]{stripped}[/red]")
        elif line.startswith("@@"):
            console.print(f"[yellow]{stripped}[/yellow]")
        else:
            console.print(f"[dim]{stripped}[/dim]")


def _resolve_paths(book_dir: Path, label: str) -> tuple[Path, Path]:
    """Return (outline_path, book_path) for a label like 'v1' or 'current'."""
    if label == "current":
        return book_dir / "outline.yaml", book_dir / "output" / "book.md"
    version_dir = get_version_dir(book_dir, int(label.lstrip("v")))
    return version_dir / "outline.yaml", version_dir / "book.md"


def show_diff(
    book_dir: Path,
    from_label: str | None,
    to_label: str | None,
    console: Console,
) -> None:
    versions = list_versions(book_dir)

    if not versions:
        console.print(
            "[yellow]No versions yet — generate the book at least once to create a baseline.[/yellow]"
        )
        return

    resolved_from = from_label or f"v{versions[-1]}"
    resolved_to = to_label or "current"

    console.print(f"\nDiff: [bold]{resolved_from}[/bold] → [bold]{resolved_to}[/bold]")

    from_outline, from_book = _resolve_paths(book_dir, resolved_from)
    to_outline, to_book = _resolve_paths(book_dir, resolved_to)

    outline_diff = list(difflib.unified_diff(
        _read(from_outline), _read(to_outline),
        fromfile=f"{resolved_from}/outline.yaml",
        tofile=f"{resolved_to}/outline.yaml",
    ))
    book_diff = list(difflib.unified_diff(
        _read(from_book), _read(to_book),
        fromfile=f"{resolved_from}/book.md",
        tofile=f"{resolved_to}/book.md",
    ))

    _render_diff(outline_diff, console, "Outline")
    _render_diff(book_diff, console, "Book")
