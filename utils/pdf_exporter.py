from pathlib import Path

import markdown as md_lib
from weasyprint import CSS, HTML

_CSS = """
@page {
    margin: 2.8cm 3cm;
    @bottom-center {
        content: counter(page);
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #888;
    }
}

body {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
}

h1 {
    font-size: 26pt;
    font-weight: normal;
    text-align: center;
    margin-top: 35%;
    margin-bottom: 0.4em;
    letter-spacing: 0.04em;
    page-break-after: avoid;
}

h1 + p em {
    /* subtitle / byline under h1 */
    font-size: 12pt;
    display: block;
    text-align: center;
    margin-bottom: 3em;
}

h2 {
    font-size: 13pt;
    font-weight: normal;
    text-align: center;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: 2.5em;
    break-before: page;
    page-break-after: avoid;
}

p {
    margin: 0 0 0 0;
    text-indent: 1.5em;
}

/* no indent after headings or hr */
h1 + p, h2 + p, hr + p {
    text-indent: 0;
}

hr {
    border: none;
    margin: 2em 0;
    text-align: center;
}
hr::after {
    content: "—";
    color: #aaa;
    font-size: 10pt;
}

em   { font-style: italic; }
strong { font-weight: bold; }
"""


def export_pdf(book_dir: Path) -> Path:
    book_md = book_dir / "output" / "book.md"
    if not book_md.exists():
        raise FileNotFoundError(
            f"No book.md in {book_dir / 'output'} — run --generate first."
        )

    html_body = md_lib.markdown(
        book_md.read_text(),
        extensions=["extra", "smarty"],
    )
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html_body}</body></html>"

    pdf_path = book_dir / "output" / "book.pdf"
    HTML(string=html).write_pdf(pdf_path, stylesheets=[CSS(string=_CSS)])
    return pdf_path
