#!/usr/bin/env python3
"""Собрать PDF бизнес-анализа для скачивания с главной страницы."""

import html
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "NVC-Maps-бизнес-анализ.md"
OUTPUT = ROOT / "wireframes" / "NVC-Maps-бизнес-анализ.pdf"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.min.js"

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>NVC Maps — бизнес-анализ</title>
  <style>
    @page {{ size: A4; margin: 16mm 14mm 18mm; }}
    html {{ font-size: 11pt; }}
    body {{
      margin: 0;
      color: #111827;
      font-family: -apple-system, "Helvetica Neue", "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    h1 {{ font-size: 20pt; line-height: 1.2; margin: 0 0 12pt; }}
    h2 {{ font-size: 15pt; margin: 22pt 0 8pt; page-break-after: avoid; }}
    h3 {{ font-size: 12.5pt; margin: 16pt 0 6pt; page-break-after: avoid; }}
    h4 {{ font-size: 11.5pt; margin: 12pt 0 4pt; page-break-after: avoid; }}
    p {{ margin: 0 0 8pt; }}
    a {{ color: #0f766e; text-decoration: none; }}
    hr {{ border: 0; border-top: 1px solid #d1d5db; margin: 16pt 0; }}
    ul, ol {{ margin: 0 0 8pt; padding-left: 18pt; }}
    li {{ margin: 0 0 3pt; }}
    table {{ width: 100%; border-collapse: collapse; margin: 0 0 12pt; }}
    tr {{ page-break-inside: avoid; }}
    th, td {{ border: 1px solid #d1d5db; padding: 4pt 6pt; vertical-align: top; text-align: left; }}
    th {{ background: #f3f4f6; }}
    pre {{
      white-space: pre-wrap;
      font-family: "SF Mono", Menlo, monospace;
      font-size: 8pt;
      line-height: 1.35;
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 6pt;
      padding: 8pt;
      page-break-inside: avoid;
    }}
    .mermaid {{ margin: 8pt 0 12pt; text-align: center; }}
    .mermaid svg {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
{body}
<script src="mermaid.min.js"></script>
<script>
  mermaid.initialize({{ startOnLoad: false, theme: "neutral", securityLevel: "loose" }});
  mermaid.run().then(function () {{
    document.querySelectorAll(".mermaid svg").forEach(function (svg) {{
      var box = svg.viewBox && svg.viewBox.baseVal;
      var w = (box && box.width) || 800;
      var h = (box && box.height) || 400;
      var width = 680;
      var height = Math.min(Math.round(h * (width / w)), 280);
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      svg.setAttribute("width", String(width));
      svg.setAttribute("height", String(height));
      svg.style.maxWidth = "100%";
      svg.style.height = "auto";
    }});
  }});
</script>
</body>
</html>
"""


def mermaid_blocks(match: re.Match) -> str:
    code = html.unescape(match.group(1))
    return f'<div class="mermaid">{html.escape(code)}</div>'


def build_html(source: str) -> str:
    body = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    body = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        mermaid_blocks,
        body,
        flags=re.DOTALL,
    )
    return PAGE.format(body=body)


def main() -> None:
    if not CHROME.is_file():
        raise SystemExit(f"Не найден Chrome: {CHROME}")
    source = SOURCE.read_text()
    with tempfile.TemporaryDirectory(prefix="nvc-ba-pdf-") as tmp:
        folder = Path(tmp)
        mermaid_js = folder / "mermaid.min.js"
        urllib.request.urlretrieve(MERMAID_URL, mermaid_js)
        page = folder / "index.html"
        page.write_text(build_html(source))
        pdf = folder / "analysis.pdf"
        subprocess.run(
            [
                str(CHROME),
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--virtual-time-budget=20000",
                f"--print-to-pdf={pdf}",
                page.as_uri(),
            ],
            check=True,
        )
        if not pdf.is_file() or pdf.stat().st_size < 1000:
            raise SystemExit("Chrome не записал PDF")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, OUTPUT)
    print(OUTPUT, OUTPUT.stat().st_size)


if __name__ == "__main__":
    main()
