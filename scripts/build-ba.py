#!/usr/bin/env python3
"""Собрать пакет бизнес-анализа из исходных разделов.

Шаги:
  backlog  — приложение 1 из историй раздела 2.5
  summary  — сводный Markdown из всех разделов
  shots    — скриншоты макетов для раздела 2.5
  site     — страницы разделов на сайте
  docx     — DOCX на двух языках: английский для эксперта, русский — копия

Русские разделы лежат в корне, английские — в en/ с теми же именами файлов.
Сайт и сводный файл собираются из русских разделов.
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

SOURCES = [src for src, _, _ in SECTIONS]

# Титульный лист по образцу ЕГУ (Правила оформления письменных работ, прил. 1, П. 1.3 и П. 1.4).
# Пропуски «____» заполняются перед сдачей. Строки: текст, полужирный, выравнивание, отступ после.
TITLE_RU = [
    ("ЕВРОПЕЙСКИЙ ГУМАНИТАРНЫЙ УНИВЕРСИТЕТ", True, "center", 0),
    ("Академический департамент ____________________", False, "center", 0),
    ("(название программы) ____________________", False, "center", 1200),
    ("КИРИЛЛ КАЛАШНИКОВ", True, "center", 0),
    ("Студент ___ курса", False, "center", 2000),
    ("СИСТЕМА СОЗДАНИЯ ИГРОВЫХ 3D-КАРТ ПО ВИДЕОЗАПИСИ", True, "center", 0),
    ("A SYSTEM FOR CREATING 3D GAME MAPS FROM VIDEO", False, "center", 600),
    ("БАКАЛАВРСКИЙ ПРОЕКТ", True, "center", 0),
    ("Блок бизнес-анализа: введение, глава 1, глава 2", False, "center", 0),
    ("Тип проекта: индивидуальный", False, "center", 2000),
    ("Руководитель: доц., канд. техн. наук С. В. Авдейчик", False, "right", 2400),
    ("Вильнюс, 2026", False, "center", 0),
]
TITLE_EN = [
    ("EUROPEAN HUMANITIES UNIVERSITY", True, "center", 0),
    ("Academic Department of ____________________", False, "center", 0),
    ("Study programme ____________________", False, "center", 1200),
    ("KIRILL KALASHNIKOV", True, "center", 0),
    ("___ year student", False, "center", 2000),
    ("A SYSTEM FOR CREATING 3D GAME MAPS FROM VIDEO", True, "center", 600),
    ("BACHELOR PROJECT", True, "center", 0),
    ("Business analysis block: Introduction, Chapter 1, Chapter 2", False, "center", 0),
    ("Project type: individual", False, "center", 2000),
    ("Supervisor: Assoc. Prof., Cand. Sc. (Eng.) S. V. Avdeychik", False, "right", 2400),
    ("Vilnius, 2026", False, "center", 0),
]

# Всё, что зависит от языка документа.
LANGS = {
    "en": {
        "dir": ROOT / "en",
        "docx": SITE / "BA_Kalashnikov_Kirill.docx",
        "pdf": SITE / "BA_Kalashnikov_Kirill.pdf",
        "title": TITLE_EN,
        "labels": {"toc": "TABLE OF CONTENTS", "table": "Table", "figure": "Image",
                   "appendix": "Appendix", "appendixUpper": "APPENDIX", "lang": "en-GB"},
        "references": "List of References",
        "backlog": ["# Appendix 1. Backlog", "",
                    "The full table of epics and stories is given in Table A.1.1.", "",
                    "Table A.1.1. Backlog: epics and stories", "",
                    "| ID | Epic | Story | Acceptance criteria | MoSCoW |",
                    "|----|------|-------|---------------------|--------|"],
    },
    "ru": {
        "dir": ROOT,
        "docx": SITE / "BA_Kalashnikov_Kirill_RU.docx",
        "pdf": SITE / "NVC-Maps-бизнес-анализ.pdf",
        "title": TITLE_RU,
        "labels": {"toc": "СОДЕРЖАНИЕ", "table": "Табл.", "figure": "Рис.",
                   "appendix": "Приложение", "appendixUpper": "ПРИЛОЖЕНИЕ", "lang": "ru-RU"},
        "references": "Список источников и литературы",
        "backlog": ["# Приложение 1. Бэклог", "",
                    "Полная таблица эпиков и историй приведена в табл. П.1.1.", "",
                    "Табл. П.1.1. Бэклог: эпики и истории", "",
                    "| ID | Эпик | История | Критерии приёмки | MoSCoW |",
                    "|----|------|---------|------------------|--------|"],
    },
}

SHOT_PAGES = {
    "m2-preflight": (1280, 820),
    "b2-jobs": (1280, 900),
    "b3-report": (1280, 820),
    "b4-viewer": (1280, 900),
}


# --- Источники и ссылки (IEEE) -------------------------------------------------
# В тексте источник указывается ключом: [@key] или [@a; @b]. Сборка нумерует источники
# по порядку первого упоминания и подставляет номера в квадратных скобках: [3], [3], [5], [2]–[4].

CITE = re.compile(r"\[@([^\]]+)\]")


def load_refs() -> dict:
    return {r["key"]: r for r in json.loads((ROOT / "references.json").read_text())}


def cite_keys(match: re.Match) -> list[str]:
    return [k.strip().lstrip("@") for k in match.group(1).split(";")]


def citation_order(lang: str = "ru") -> dict[str, int]:
    """Номер каждого источника — по первому упоминанию в разделах по порядку."""
    refs = load_refs()
    order: dict[str, int] = {}
    for src in SOURCES:
        path = LANGS[lang]["dir"] / src
        if not path.is_file():  # 03 и 04 генерируются и ссылок не содержат
            continue
        for m in CITE.finditer(path.read_text()):
            for key in cite_keys(m):
                if key not in refs:
                    raise SystemExit(f"Нет источника {key} в references.json")
                order.setdefault(key, len(order) + 1)
    missing = set(refs) - set(order)
    if missing:
        raise SystemExit(f"Источники ни разу не процитированы: {sorted(missing)}")
    return order


def cite_label(nums: list[int]) -> str:
    """[1], [3] для отдельных номеров, [2]–[5] для трёх и больше подряд."""
    nums = sorted(set(nums))
    groups, start = [], 0
    for i in range(1, len(nums) + 1):
        if i == len(nums) or nums[i] != nums[i - 1] + 1:
            run = nums[start:i]
            groups.append(f"[{run[0]}]–[{run[-1]}]" if len(run) >= 3 else ", ".join(f"[{n}]" for n in run))
            start = i
    return ", ".join(groups)


def cite_markdown(text: str, order: dict[str, int], escape: bool = False) -> str:
    """Заменить [@key] на номера IEEE. escape — для Markdown, где [n] надо экранировать."""
    def repl(m: re.Match) -> str:
        label = cite_label([order[k] for k in cite_keys(m)])
        return label.replace("[", "\\[").replace("]", "\\]") if escape else label
    return CITE.sub(repl, text)


def build_references() -> None:
    refs = load_refs()
    for lang, cfg in LANGS.items():
        order = citation_order(lang)
        out = [f"# {cfg['references']}", ""]
        for key, n in sorted(order.items(), key=lambda kv: kv[1]):
            out += [f"\\[{n}\\] {refs[key]['ieee']}", ""]
        (cfg["dir"] / "03-references.md").write_text("\n".join(out))
        print(f"references ({lang}):", len(order))


# --- Приложение 1 -----------------------------------------------------------

STORY_ROW = re.compile(r"^\| (US-\d+\.\d+) \| (.+) \| (.+) \| (Must|Should|Could) \|$")
EPIC = re.compile(r"^### (E\d+)\. (.+)$")


def build_backlog() -> None:
    for lang, cfg in LANGS.items():
        lines = (cfg["dir"] / "02-system-requirements.md").read_text().splitlines()
        rows, epic = [], None
        for line in lines:
            if m := EPIC.match(line):
                epic = m.group(1)
            elif m := STORY_ROW.match(line):
                rows.append({"id": m.group(1), "epic": epic, "story": m.group(2),
                             "ac": m.group(3), "priority": m.group(4)})
        out = list(cfg["backlog"])
        for s in rows:
            out.append(f"| {s['id']} | {s['epic']} | {s['story']} | {s['ac']} | {s['priority']} |")
        out.append("")
        (cfg["dir"] / "04-appendix-a-backlog.md").write_text("\n".join(out))
        print(f"backlog ({lang}):", len(rows), "stories")


# --- Сводный Markdown -------------------------------------------------------

SUMMARY_HEADER = """# Бизнес-анализ: система создания игровых 3D-карт по видеозаписи

**Продукт:** NVC Maps
**English:** A System for Creating 3D Game Maps from Video

Сайт с разделами и экранами: [kalashnikovkv.github.io/nvc-business-analysis](https://kalashnikovkv.github.io/nvc-business-analysis/)

Файл собирается скриптом `scripts/build-ba.py` из разделов `00`–`06`. Правки вносятся в разделы, не сюда.

"""


def build_summary() -> None:
    parts = []
    order = citation_order()
    for src, _, _ in SECTIONS:
        text = cite_markdown((ROOT / src).read_text(), order, escape=True)
        parts.append(re.sub(r"(?m)^(#+) ", r"#\1 ", text).rstrip() + "\n")
    body = "\n---\n\n".join(parts)
    SUMMARY.write_text(SUMMARY_HEADER + "---\n\n" + body)
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
    combine_shots(KEY_SHOTS, "", "key-stories.png")
    build_shots_en()


KEY_SHOTS = [
    ("m2-preflight", "US-1.2 · Проверка записи"),
    ("b2-jobs", "US-2.3 · Мои задания"),
    ("b3-report", "US-3.1 · Отчёт"),
    ("b4-viewer", "US-4.1 · Ходьба по карте"),
]
KEY_SHOTS_EN = [
    ("m2-preflight", "US-1.2 · Recording check"),
    ("b2-jobs", "US-2.3 · My jobs"),
    ("b3-report", "US-3.1 · Report"),
    ("b4-viewer", "US-4.1 · Walking the map"),
]

# Тексты макетов ключевых историй для английского документа.
MOCKUP_EN = {
    "Съёмка прошла проверку. Съёмка уходит на сервер, карты открываются в браузере.":
        "The capture passed the check. It goes to the server; maps open in the browser.",
    "Карта готова": "Map ready", "Тёмная": "Dark", "Светлая": "Light",
    "Длительность": "Duration", "22 с": "22 s", "Кадры позы": "Pose frames", "Глубина": "Depth",
    "Пол": "Floor", "найден": "found", "Отправить съёмку": "Send capture",
    "Открыть в браузере": "Open in browser",
    "Загрузка": "Upload", "Задания": "Jobs", "Мои задания": "My jobs",
    "То же видео с теми же параметрами сборки даёт ту же карту.":
        "The same video with the same build settings gives the same map.",
    "Все": "All", "В очереди": "Queued", "Собирается": "Building", "Готово": "Ready", "Отказ": "Rejected",
    "Создано": "Created", "Статус": "Status", "Способ построения": "Reconstruction method",
    "готово": "ready", "слияние глубины LiDAR": "LiDAR depth fusion", "Отчёт": "Report", "Карта": "Map",
    "собирается": "building", "отказ": "rejected", "Причина": "Reason", "в очереди": "queued",
    "Отчёт · job_8f2a": "Report · job_8f2a",
    "Зона по умолчанию 80×80 см · размеры датчика, масштаб не менялся":
        "Default zone 80×80 cm · sensor scale, not rescaled",
    "Карта собрана · способ построения: слияние глубины LiDAR":
        "Map built · reconstruction method: LiDAR depth fusion",
    "Видимая модель": "Visual mesh", "до 50 000 треугольников": "up to 50,000 triangles",
    "Опора": "Collision mesh", "до 25% от видимой модели": "up to 25% of the visual mesh",
    "Файл видимой модели": "Visual mesh file", "4,2 МБ": "4.2 MB", "до 25 МБ": "up to 25 MB",
    "Файл опоры": "Collision mesh file", "0,9 МБ": "0.9 MB", "до 8 МБ": "up to 8 MB",
    "Зона": "Zone", "0,80 м": "0.80 m", "как снял датчик": "as measured by the sensor",
    "Открыть карту": "Open map", "Скачать пакет (5 файлов)": "Download package (5 files)",
    "К списку": "Back to list",
    "Карта · проверка опоры": "Map · collision check",
    "Управление — WASD или стрелки. Персонаж должен простоять на поверхности не меньше 5 секунд и пройти карту от края до края.":
        "Controls: WASD or arrow keys. The character must stand on the surface for at least 5 seconds and cross the map from edge to edge.",
    "опора": "collision", "на поверхности · 0:07": "on surface · 0:07",
    "размер только для показа": "size for display only",
    "Исходный кадр · та же камера": "Source frame · same camera",
    "Хорошая карта похожа на кадр съёмки. Масштаб под игру выбирает разработчик, который импортирует пакет.":
        "A good map looks like the capture frame. The game scale is chosen by the developer who imports the package.",
    "Размер персонажа (показ)": "Character size (display)", "Назад к отчёту": "Back to report",
}


def build_shots_en() -> None:
    """Те же макеты с английскими надписями — для рисунка 2.1 английского документа."""
    with tempfile.TemporaryDirectory(prefix="nvc-mock-en-") as tmp:
        folder = Path(tmp)
        shutil.copyfile(SITE / "wireframes.css", folder / "wireframes.css")
        for name, (w, h) in SHOT_PAGES.items():
            text = (SITE / f"{name}.html").read_text()
            text = re.sub(r">([^<>]+)<", lambda m: ">" + MOCKUP_EN.get(" ".join(m.group(1).split()), m.group(1)) + "<", text)
            page = folder / f"{name}.html"
            page.write_text(text)
            out = SHOTS / f"{name}-en.png"
            subprocess.run(
                [str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                 f"--window-size={w},{h}", "--force-device-scale-factor=1",
                 "--virtual-time-budget=5000", f"--screenshot={out}", page.as_uri()],
                check=True, capture_output=True,
            )
            crop_shot(out)
            print("shot:", out.name)
    combine_shots(KEY_SHOTS_EN, "-en", "key-stories-en.png")


def combine_shots(items: list, suffix: str, name: str) -> None:
    """Собрать макеты ключевых историй в один рисунок 2 × 2."""
    from PIL import Image, ImageDraw, ImageFont

    cell_w, cell_h, label_h, gap = 900, 760, 44, 24
    sheet = Image.new("RGB", (cell_w * 2 + gap * 3, (cell_h + label_h) * 2 + gap * 3), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    for i, (shot, label) in enumerate(items):
        im = Image.open(SHOTS / f"{shot}{suffix}.png").convert("RGB")
        im.thumbnail((cell_w, cell_h))
        x = gap + (i % 2) * (cell_w + gap)
        y = gap + (i // 2) * (cell_h + label_h + gap)
        draw.text((x, y), label, fill="#111827", font=font)
        sheet.paste(im, (x + (cell_w - im.width) // 2, y + label_h))
    sheet.save(SHOTS / name)
    print("shot:", name)


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
  <link rel="stylesheet" href="wireframes.css?v=12" />
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


# Якоря для запасных слайдов (s09-backup.html).
ANCHORS = {
    "1.3. Анализ аналогов": "analogs",
    "2.6. Сценарии использования": "use-cases",
    "2.9. Риски": "risks",
}


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
    order = citation_order()
    for src, page, title in SECTIONS:
        active = ' class="active"'
        nav = "\n".join(
            f'      <a{active if p == page else ""} href="{p}">{t}</a>'
            for _, p, t in SECTIONS
        )
        text = cite_markdown((ROOT / src).read_text(), order, escape=True)
        body = md_to_html(text)
        body = body.replace('src="wireframes/', 'src="')
        for heading, anchor in ANCHORS.items():
            body = body.replace(f"<h2>{heading}</h2>", f'<h2 id="{anchor}">{heading}</h2>')
            body = body.replace(f"<h3>{heading}</h3>", f'<h3 id="{anchor}">{heading}</h3>')
        (SITE / page).write_text(PAGE.format(
            title=html.escape(title), nav=nav, body=body,
            tag=page[1:3], mermaid=MERMAID_JS,
        ))
        print("site:", page)


# --- Слайды для защиты ---------------------------------------------------------

def build_slides() -> None:
    import slides

    for page in slides.render(SITE):
        print("slide:", page)
    # Тот же набор слайдов — в PowerPoint для скачивания.
    CACHE.mkdir(exist_ok=True)
    slides.export_json(CACHE / "slides.json")
    subprocess.run(["node", str(ROOT / "scripts" / "build-pptx.mjs"), str(CACHE / "slides.json"),
                    str(SITE / "NVC-Maps-защита.pptx")], check=True)


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


def docx_headings(lang: str) -> list[tuple[int, str, str]]:
    """Заголовки 1–2 уровня в порядке документа — для оглавления."""
    cfg = LANGS[lang]
    label = cfg["labels"]
    out = []
    for src in SOURCES:
        in_code = False
        for line in (cfg["dir"] / src).read_text().splitlines():
            if line.startswith("```"):
                in_code = not in_code
            m = re.match(r"^(#{1,2}) (.+)$", line)
            if m and not in_code:
                text = re.sub(r"\\(.)", r"\1", m.group(2)).replace("**", "")
                level = len(m.group(1))
                appendix = re.match(rf"^{label['appendix']} (\d+)\. (.+)$", text)
                if appendix:
                    # В тексте: «ПРИЛОЖЕНИЕ N» справа и заголовок ниже; в оглавлении — одной строкой.
                    upper = f"{label['appendixUpper']} {appendix.group(1)}"
                    out.append((1, f"{upper}. {appendix.group(2)}", upper))
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


def heading_pages(pdf: Path, headings: list[tuple[int, str, str]], toc: str) -> list[int]:
    pages = pdf_pages(pdf)
    # Страницы титула и оглавления пропускаем: оглавление тоже содержит заголовки.
    start = max(i for i, p in enumerate(pages) if toc in p) + 1
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
    for lang, cfg in LANGS.items():
        build_docx_lang(lang, cfg)


def build_docx_lang(lang: str, cfg: dict) -> None:
    out = cfg["docx"]
    for src in SOURCES:
        for code in re.findall(r"```mermaid\n(.*?)```\n", (cfg["dir"] / src).read_text(), flags=re.DOTALL):
            render_mermaid(code)
    CACHE.mkdir(exist_ok=True)
    spec = CACHE / f"docx-input-{lang}.json"
    spec.write_text(json.dumps({
        "root": str(ROOT), "dir": str(cfg["dir"]), "out": str(out), "sections": SOURCES,
        "titleLines": cfg["title"], "labels": cfg["labels"], "author": "Kirill Kalashnikov",
        "docTitle": "A System for Creating 3D Game Maps from Video",
        "citations": citation_order(lang),
    }, ensure_ascii=False))
    subprocess.run(["node", str(ROOT / "scripts" / "build-docx.mjs"), str(spec)], check=True)

    toc = cfg["labels"]["toc"]
    headings = docx_headings(lang)
    with tempfile.TemporaryDirectory(prefix="nvc-ba-docx-") as tmp:
        folder = Path(tmp)
        # Проход 1: строки с условными номерами, чтобы оглавление заняло своё место.
        fill_toc(out, headings, ["00"] * len(headings))
        pages = heading_pages(docx_to_pdf(out, folder), headings, toc)
        # Проход 2: настоящие номера страниц.
        fill_toc(out, headings, pages)
        check = heading_pages(docx_to_pdf(out, folder), headings, toc)
        if check != pages:
            fill_toc(out, headings, check)
        preview = docx_to_pdf(out, folder)
        shutil.copyfile(preview, CACHE / f"docx-preview-{lang}.pdf")
        shutil.copyfile(preview, cfg["pdf"])
    print(f"docx ({lang}):", out.name, out.stat().st_size, "· превью:", CACHE / f"docx-preview-{lang}.pdf")


STEPS = {
    "references": build_references,
    "backlog": build_backlog,
    "summary": build_summary,
    "shots": build_shots,
    "site": build_site,
    "slides": build_slides,
    "docx": build_docx,
}

if __name__ == "__main__":
    steps = sys.argv[1:] or ["references", "backlog", "summary", "site", "slides", "docx"]
    for step in steps:
        STEPS[step]()
