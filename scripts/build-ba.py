#!/usr/bin/env python3
"""Собрать пакет бизнес-анализа из исходных разделов.

Шаги:
  backlog  — приложение 1 из историй раздела 2.5
  summary  — сводный Markdown из всех разделов
  shots    — скриншоты макетов для раздела 2.5
  site     — страницы разделов на сайте
  docx     — DOCX для эксперта (титул, оглавление, диаграммы картинками)

Без аргументов выполняются backlog, summary, site и docx.
DOCX рисует scripts/build-docx.mjs (npm install), PDF для сайта — его рендер в LibreOffice.
"""

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "wireframes"
SHOTS = SITE / "shots"
CACHE = ROOT / ".build"
SUMMARY = ROOT / "NVC-Maps-бизнес-анализ.md"
DOCX = SITE / "BA_Kalashnikov_Kirill.docx"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.12.0"
MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.min.js"

SECTIONS = [
    ("00-introduction.md", "d00-introduction.html", "Введение"),
    ("01-analytical-part.md", "d01-analysis.html", "1. Аналитическая часть"),
    ("02-system-requirements.md", "d02-requirements.html", "2. Требования к системе"),
    ("03-references.md", "d03-references.html", "Список источников и литературы"),
    ("04-appendix-a-backlog.md", "d04-backlog.html", "Приложение 1. Бэклог"),
    ("05-appendix-b-diagrams.md", "d05-diagrams.html", "Приложение 2. Диаграммы"),
    ("06-statements.md", "d06-statements.html", "Заявления"),
]

# Титульный лист по образцу ЕГУ (Правила оформления письменных работ, прил. 1).
# Пропуски «____» заполняются перед сдачей.
TITLE = {
    "topic_ru": "Система создания игровых 3D-карт по видеозаписи",
    "topic_en": "A System for Creating 3D Game Maps from Video",
    "department": "____________________",
    "program": "(название программы) ____________________",
    "author_caps": "КИРИЛЛ КАЛАШНИКОВ",
    "course": "___",
    "supervisor": "доц., канд. техн. наук С. В. Авдейчик",
    "type": "индивидуальный",
    "block": "Блок бизнес-анализа: введение, глава 1, глава 2",
    "year": "2026",
}

SHOT_PAGES = {
    "m2-preflight": (1280, 820),
    "b2-jobs": (1280, 900),
    "b3-report": (1280, 820),
    "b4-viewer": (1280, 900),
}


# --- Источники и сноски (Чикагский стиль, 16-е изд.) -------------------------

CITE = re.compile(r"[ \u00a0]*\[@([^\]]+)\]")


def load_refs() -> dict:
    return {r["key"]: r for r in json.loads((ROOT / "references.json").read_text())}


def bib_sort_key(entry: str) -> tuple:
    text = entry.lstrip("“\"*").lower()
    # Сначала кириллица, затем латиница (правила ЕГУ, п. 2.5).
    return (0 if re.match(r"[а-яё]", text) else 1, text)


def build_references() -> None:
    refs = load_refs()
    entries = sorted((r["bib"] for r in refs.values()), key=bib_sort_key)
    linked = [re.sub(r"(https?://\S+?)(\.?)$", r"<\1>\2", e) for e in entries]
    out = [
        "# Список источников и литературы",
        "",
        "Источники расположены в алфавитном порядке и оформлены по Чикагскому стилю (метод сносок и библиографии, 16-е изд.). Источников на кириллице нет. Ссылки в тексте даны постраничными сносками.",
        "",
        *[f"{i}. {e}" for i, e in enumerate(linked, 1)],
        "",
    ]
    (ROOT / "03-references.md").write_text("\n".join(out))
    print("references:", len(entries))


def chicago_join(parts: list[str]) -> str:
    """Склеить несколько ссылок в одну сноску: «A; B.» — точка внутри кавычек."""
    clean = []
    for p in parts:
        p = p.rstrip(".")
        if p.endswith(".”"):
            p = p[:-2] + "”"
        clean.append(p)
    text = "; ".join(clean)
    return text[:-1] + ".”" if text.endswith("”") else text + "."


class Notes:
    """Сноски по Чикагскому стилю: первая ссылка на источник — полная, дальше — краткая."""

    def __init__(self) -> None:
        self.refs = load_refs()
        self.seen: set[str] = set()
        self.defs: list[str] = []

    def note(self, keys: list[str]) -> str:
        parts = []
        for key in keys:
            ref = self.refs[key]
            parts.append(ref["short"] if key in self.seen else ref["note"])
            self.seen.add(key)
        return chicago_join(parts)

    def markdown(self, text: str) -> str:
        """Заменить [@key; @key] на сноски Markdown [^n]."""
        def repl(m: re.Match) -> str:
            keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
            self.defs.append(re.sub(r"(https?://[^\s<>]+?)(?=[.,;]?(?:\s|$))", r"<\1>", self.note(keys)))
            return f"[^{len(self.defs)}]"
        return CITE.sub(repl, text)

    def definitions(self) -> str:
        return "\n".join(f"[^{i}]: {d}" for i, d in enumerate(self.defs, 1))


# --- Приложение 1 -----------------------------------------------------------

STORY_ROW = re.compile(r"^\| (US-\d+\.\d+) \| (.+) \| (.+) \| (Must|Should|Could) \|$")
EPIC = re.compile(r"^### (E\d+)\. (.+)$")


def build_backlog() -> None:
    lines = (ROOT / "02-system-requirements.md").read_text().splitlines()
    rows, epic = [], None
    for line in lines:
        if m := EPIC.match(line):
            epic = m.group(1)
        elif m := STORY_ROW.match(line):
            rows.append({"id": m.group(1), "epic": epic, "story": m.group(2),
                         "ac": m.group(3), "priority": m.group(4)})

    out = [
        "# Приложение 1. Бэклог",
        "",
        "Полная таблица эпиков и историй приведена в табл. П.1.1. Она собирается автоматически из раздела 2.5, поэтому совпадает с ним дословно.",
        "",
        "Табл. П.1.1. Бэклог: эпики и истории",
        "",
        "| ID | Эпик | История | Критерии приёмки | MoSCoW |",
        "|----|------|---------|------------------|--------|",
    ]
    for s in rows:
        out.append(f"| {s['id']} | {s['epic']} | {s['story']} | {s['ac']} | {s['priority']} |")
    out.append("")
    (ROOT / "04-appendix-a-backlog.md").write_text("\n".join(out))
    print("backlog:", len(rows), "stories")


# --- Сводный Markdown -------------------------------------------------------

SUMMARY_HEADER = """# Бизнес-анализ: система создания игровых 3D-карт по видеозаписи

**Продукт:** NVC Maps
**English:** A System for Creating 3D Game Maps from Video

Сайт с разделами и экранами: [kalashnikovkv.github.io/nvc-business-analysis](https://kalashnikovkv.github.io/nvc-business-analysis/)

Файл собирается скриптом `scripts/build-ba.py` из разделов `00`–`06`. Правки вносятся в разделы, не сюда.

"""


def build_summary() -> None:
    parts = []
    notes = Notes()
    for src, _, _ in SECTIONS:
        text = notes.markdown((ROOT / src).read_text())
        parts.append(re.sub(r"(?m)^(#+) ", r"#\1 ", text).rstrip() + "\n")
    body = "\n---\n\n".join(parts)
    SUMMARY.write_text(SUMMARY_HEADER + "---\n\n" + body + "\n---\n\n" + notes.definitions() + "\n")
    print("summary:", SUMMARY.name)


# --- Скриншоты макетов -------------------------------------------------------

def build_shots() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    for name, (w, h) in SHOT_PAGES.items():
        out = SHOTS / f"{name}.png"
        subprocess.run(
            [str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={w},{h}", "--force-device-scale-factor=1",
             "--virtual-time-budget=5000", f"--screenshot={out}",
             (SITE / f"{name}.html").as_uri()],
            check=True, capture_output=True,
        )
        crop_shot(out)
        print("shot:", out.name)
    combine_shots()


KEY_SHOTS = [
    ("m2-preflight", "US-1.2 · Проверка записи"),
    ("b2-jobs", "US-2.4 · Мои задания"),
    ("b3-report", "US-3.1 · Отчёт"),
    ("b4-viewer", "US-4.1 · Ходьба по карте"),
]


def combine_shots() -> None:
    """Собрать макеты ключевых историй в один рисунок 2 × 2."""
    from PIL import Image, ImageDraw, ImageFont

    cell_w, cell_h, label_h, gap = 900, 760, 44, 24
    sheet = Image.new("RGB", (cell_w * 2 + gap * 3, (cell_h + label_h) * 2 + gap * 3), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    for i, (name, label) in enumerate(KEY_SHOTS):
        im = Image.open(SHOTS / f"{name}.png").convert("RGB")
        im.thumbnail((cell_w, cell_h))
        x = gap + (i % 2) * (cell_w + gap)
        y = gap + (i // 2) * (cell_h + label_h + gap)
        draw.text((x, y), label, fill="#111827", font=font)
        sheet.paste(im, (x + (cell_w - im.width) // 2, y + label_h))
    sheet.save(SHOTS / "key-stories.png")
    print("shot: key-stories.png")


def crop_shot(path: Path) -> None:
    """Оставить только макет: без боковой панели сайта и пустого фона."""
    from PIL import Image

    im = Image.open(path).convert("RGB")
    w, h = im.size
    gray = im.convert("L")
    # Тёмные рамки телефона и тёмного окна браузера; правее 1200 px — обрезанная светлая копия.
    box = gray.crop((280, 0, min(w, 1200), h)).point(lambda v: 255 if v < 60 else 0).getbbox()
    if not box:
        return
    left, top, right, bottom = box
    im.crop((280 + left - 8, max(0, top - 60), 280 + right + 8, min(h, bottom + 8))).save(path)


# --- Сайт --------------------------------------------------------------------

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} · NVC Maps</title>
  <link rel="stylesheet" href="wireframes.css?v=11" />
</head>
<body class="page">
  <aside class="side">
    <a class="back" href="index.html">← Бизнес-анализ</a>
    <h1>{title}</h1>
    <nav>
{nav}
    </nav>
  </aside>
  <main class="stage">
    <article class="doc-board prose">
      <div class="bar"><span>{tag}</span><span>NVC Maps</span></div>
      <div class="body">
{body}
      </div>
    </article>
  </main>
  <script src="{mermaid}"></script>
  <script>mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});</script>
</body>
</html>
"""


def md_to_html(text: str) -> str:
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "footnotes"])
    body = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        lambda m: f'<pre class="mermaid">{m.group(1)}</pre>',
        body,
        flags=re.DOTALL,
    )
    return body


def build_site() -> None:
    for old in ["d01-summary", "d02-stakeholders", "d03-personas", "d04-stories", "d05-screens", "d06-nfr"]:
        (SITE / f"{old}.html").unlink(missing_ok=True)
    for src, page, title in SECTIONS:
        active = ' class="active"'
        nav = "\n".join(
            f'      <a{active if p == page else ""} href="{p}">{t}</a>'
            for _, p, t in SECTIONS
        )
        notes = Notes()
        text = notes.markdown((ROOT / src).read_text())
        if notes.defs:
            text += "\n\n" + notes.definitions() + "\n"
        body = md_to_html(text)
        body = body.replace('src="wireframes/', 'src="')
        (SITE / page).write_text(PAGE.format(
            title=html.escape(title), nav=nav, body=body,
            tag=page[1:3], mermaid=MERMAID_JS,
        ))
        print("site:", page)


# --- DOCX --------------------------------------------------------------------

def render_mermaid(code: str) -> Path:
    CACHE.mkdir(exist_ok=True)
    digest = hashlib.sha1(code.encode()).hexdigest()[:12]
    png = CACHE / f"diagram-{digest}.png"
    if png.is_file():
        return png
    src = CACHE / f"diagram-{digest}.mmd"
    src.write_text(code)
    conf = CACHE / "puppeteer.json"
    conf.write_text(json.dumps({"executablePath": str(CHROME), "args": ["--no-sandbox"]}))
    env = dict(os.environ, PUPPETEER_SKIP_DOWNLOAD="1")
    subprocess.run(
        ["npx", "-y", MERMAID_CLI, "-p", str(conf), "-i", str(src), "-o", str(png),
         "-s", "2", "-b", "white", "-w", "1100"],
        check=True, env=env, capture_output=True,
    )
    return png


SOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def docx_headings() -> list[tuple[int, str, str]]:
    """Заголовки 1–2 уровня в порядке документа — для оглавления."""
    out = []
    for src, _, _ in SECTIONS:
        in_code = False
        for line in (ROOT / src).read_text().splitlines():
            if line.startswith("```"):
                in_code = not in_code
            m = re.match(r"^(#{1,2}) (.+)$", line)
            if m and not in_code:
                text = re.sub(r"\\(.)", r"\1", m.group(2)).replace("**", "")
                level = len(m.group(1))
                appendix = re.match(r"^Приложение (\d+)\. (.+)$", text)
                if appendix:
                    # В тексте: «ПРИЛОЖЕНИЕ N» справа и заголовок ниже; в оглавлении — одной строкой.
                    out.append((1, f"ПРИЛОЖЕНИЕ {appendix.group(1)}. {appendix.group(2)}", f"ПРИЛОЖЕНИЕ {appendix.group(1)}"))
                else:
                    shown = text.upper() if level == 1 else text
                    out.append((level, shown, shown))
    return out


def docx_to_pdf(docx: Path, folder: Path) -> Path:
    subprocess.run(
        [str(SOFFICE), "--headless", "--convert-to", "pdf", "--outdir", str(folder), str(docx)],
        check=True, capture_output=True,
    )
    return folder / (docx.stem + ".pdf")


def pdf_pages(pdf: Path) -> list[str]:
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True,
                          capture_output=True, text=True).stdout
    return [re.sub(r"\s+", " ", p) for p in text.split("\f")]


def heading_pages(pdf: Path, headings: list[tuple[int, str, str]]) -> list[int]:
    pages = pdf_pages(pdf)
    # Страницы титула и оглавления пропускаем: оглавление тоже содержит заголовки.
    start = max(i for i, p in enumerate(pages) if "СОДЕРЖАНИЕ" in p) + 1
    result, i = [], start
    for _, _, text in headings:
        key = re.sub(r"\s+", " ", text)[:40]
        while i < len(pages) and key not in pages[i]:
            i += 1
        if i == len(pages):
            raise SystemExit(f"Заголовок не найден в PDF: {text}")
        result.append(i + 1)
    return result


def fill_toc(docx: Path, headings: list[tuple[int, str, str]], pages: list[int]) -> None:
    """Записать готовые строки в поле оглавления; поле остаётся обновляемым (F9)."""
    with zipfile.ZipFile(docx) as z:
        files = {n: z.read(n) for n in z.namelist()}
    doc = files["word/document.xml"].decode()
    entries = "".join(
        f'<w:p><w:pPr><w:pStyle w:val="TOC{level}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{html.escape(text, quote=False)}</w:t></w:r>'
        f"<w:r><w:tab/></w:r><w:r><w:t>{page}</w:t></w:r></w:p>"
        for (level, text, _), page in zip(headings, pages)
    )
    # Убрать прежние строки и вставить новые перед абзацем с концом поля.
    doc = re.sub(r'<!--toc-->.*?<!--/toc-->', "", doc, flags=re.DOTALL)
    end = re.search(r'<w:p>(?:(?!<w:p>).)*?<w:fldChar w:fldCharType="end"/>', doc, flags=re.DOTALL)
    if not end:
        raise SystemExit("Не найдено поле оглавления")
    doc = doc[: end.start()] + "<!--toc-->" + entries + "<!--/toc-->" + doc[end.start():]
    files["word/document.xml"] = doc.encode()
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    tmp.replace(docx)


def build_docx() -> None:
    if not SOFFICE.is_file():
        raise SystemExit("Нужен LibreOffice: brew install --cask libreoffice")
    sources = [src for src, _, _ in SECTIONS]
    for src in sources:
        for code in re.findall(r"```mermaid\n(.*?)```\n", (ROOT / src).read_text(), flags=re.DOTALL):
            render_mermaid(code)
    CACHE.mkdir(exist_ok=True)
    spec = CACHE / "docx-input.json"
    spec.write_text(json.dumps({
        "root": str(ROOT), "out": str(DOCX), "sections": sources,
        "title": {**TITLE, "author_en": "Kirill Kalashnikov"},
    }, ensure_ascii=False))
    subprocess.run(["node", str(ROOT / "scripts" / "build-docx.mjs"), str(spec)], check=True)

    headings = docx_headings()
    with tempfile.TemporaryDirectory(prefix="nvc-ba-docx-") as tmp:
        folder = Path(tmp)
        # Проход 1: строки с условными номерами, чтобы оглавление заняло своё место.
        fill_toc(DOCX, headings, ["00"] * len(headings))
        pages = heading_pages(docx_to_pdf(DOCX, folder), headings)
        # Проход 2: настоящие номера страниц.
        fill_toc(DOCX, headings, pages)
        final = docx_to_pdf(DOCX, folder)
        check = heading_pages(final, headings)
        if check != pages:
            fill_toc(DOCX, headings, check)
        preview = docx_to_pdf(DOCX, folder)
        shutil.copyfile(preview, CACHE / "docx-preview.pdf")
        # PDF на сайте — тот же документ, что и DOCX.
        shutil.copyfile(preview, SITE / "NVC-Maps-бизнес-анализ.pdf")
    print("docx:", DOCX.name, DOCX.stat().st_size, "· превью:", CACHE / "docx-preview.pdf")


STEPS = {
    "references": build_references,
    "backlog": build_backlog,
    "summary": build_summary,
    "shots": build_shots,
    "site": build_site,
    "docx": build_docx,
}

if __name__ == "__main__":
    steps = sys.argv[1:] or ["references", "backlog", "summary", "site", "docx"]
    for step in steps:
        STEPS[step]()
