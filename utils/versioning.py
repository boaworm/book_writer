import shutil
from pathlib import Path


def get_version_dir(book_dir: Path, version: int) -> Path:
    return book_dir / "versions" / f"v{version}"


def get_latest_version_number(book_dir: Path) -> int:
    versions_dir = book_dir / "versions"
    if not versions_dir.exists():
        return 0
    dirs = [d for d in versions_dir.iterdir() if d.is_dir() and d.name.startswith("v")]
    return max((int(d.name[1:]) for d in dirs), default=0)


def list_versions(book_dir: Path) -> list[int]:
    versions_dir = book_dir / "versions"
    if not versions_dir.exists():
        return []
    dirs = [d for d in versions_dir.iterdir() if d.is_dir() and d.name.startswith("v")]
    return sorted(int(d.name[1:]) for d in dirs)


def snapshot_current(book_dir: Path) -> Path | None:
    """Copy outline.yaml + book.yaml + book.md into versions/vN before regeneration."""
    book_md = book_dir / "output" / "book.md"
    if not book_md.exists():
        return None

    version_dir = get_version_dir(book_dir, get_latest_version_number(book_dir) + 1)
    version_dir.mkdir(parents=True, exist_ok=True)

    for filename in ("outline.yaml", "book.yaml"):
        src = book_dir / filename
        if src.exists():
            shutil.copy2(src, version_dir / filename)

    shutil.copy2(book_md, version_dir / "book.md")
    return version_dir
