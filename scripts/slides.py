"""Презентация для защиты по «Defense and Presentation Requirements 2026/27».

Восемь слайдов и титульный: одна мысль на слайд, до 30 слов текста, крупный визуальный
элемент, внизу — ссылка на раздел работы. Сквозная линия: проблема → цель → показатель → эпик.
После доклада — запасные слайды и ответы на типовые вопросы комиссии.

На слайдах нет сокращений и идентификаторов (KPI, NFR, US-4.1 и т. п.) — только слова.
Цифры берутся из разделов 00–02; при их правке слайды правятся здесь.

Содержимое описано данными: из него собираются и страница deck.html (render),
и PowerPoint (scripts/build-pptx.mjs читает export_json).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

DECK = "deck.html"
SITE_URL = "https://kalashnikovkv.github.io/nvc-business-analysis/"

# Сквозная линия: на слайде подсвечено звено, о котором он.
CHAIN = ["Проблема", "Цель", "Показатели", "Эпики"]

SLIDES = [
    {
        "nav": "Титульный слайд",
        "kind": "title",
        "ref": "Титульный лист",
        "blocks": [{
            "type": "title",
            "kicker": "NVC Maps · бакалаврский проект",
            "title": "Система создания игровых 3D-карт по видеозаписи",
            "sub": "A System for Creating 3D Game Maps from Video",
            "people": ["Кирилл Калашников", "Руководитель: доцент, кандидат технических наук Сергей Валентинович Авдейчик"],
        }],
    },
    {
        "nav": "Проблема",
        "chain": 0,
        "title": "Телефон снимает место, но не делает из него уровень",
        "ref": "Введение: актуальность и проблема",
        "blocks": [{
            "type": "number",
            "value": "70 000",
            "caption": "авторов карт в Fortnite в 2024 году — почти втрое больше, чем годом раньше",
            "text": "Опору для персонажа, упрощение и размеры делают вручную. Брак съёмки виден только в игровом движке.",
        }],
    },
    {
        "nav": "Цель",
        "chain": 1,
        "title": "Один обход телефоном — и проходимый уровень без ручной доводки",
        "ref": "Введение: цель и задачи, объект и предмет",
        "blocks": [
            {"type": "tasks", "items": [
                ["Раздел 1.1", "Как делают сейчас"],
                ["Разделы 1.2–1.3", "Источники и аналоги"],
                ["Раздел 2.1", "Видение и показатели"],
                ["Разделы 2.5–2.7", "Требования"],
                ["Разделы 2.8–2.10", "Право, риски, оценка"],
            ]},
            {"type": "cards", "items": [
                ["Объект", "Создание игрового уровня по реальному месту"],
                ["Предмет", "Проверка съёмки, сборка карты, проверка ходьбой"],
            ]},
        ],
    },
    {
        "nav": "Текущий процесс",
        "chain": 0,
        "title": "Время теряется на ручной доводке, данные — при экспорте",
        "ref": "Разделы 1.1 и 2.2",
        "blocks": [
            {"type": "flow", "items": [
                ["Снять", "", ""],
                ["Выгрузить", "", ""],
                ["Почистить", "вручную", "lost"],
                ["Построить опору", "вручную", "lost"],
                ["Выставить размеры", "теряются", "lost"],
                ["Проверить", "только в движке", "late"],
            ]},
            {"type": "matrix", "items": [
                ["Сильное влияние, высокий интерес", "Пользователи, владелец продукта", True],
                ["Сильное влияние, низкий интерес", "Apple, игровые движки, закон о данных", False],
                ["Среднее влияние", "Хостинг, конкуренты", False],
                ["Слабое влияние, высокий интерес", "Игрок, владелец места, человек в кадре", False],
            ]},
        ],
    },
    {
        "nav": "Аналоги",
        "chain": 0,
        "title": "Сканеры делают модель для просмотра, а не уровень",
        "ref": "Разделы 1.3–1.4",
        "blocks": [
            {"type": "check",
             "columns": ["Polycam, Scaniverse, KIRI Engine", "World Labs Marble", "Video2Game", "NVC Maps"],
             "rows": [
                 ["Размеры в метрах", "yes", "no", "no", "yes"],
                 ["Лёгкая опора для персонажа", "no", "part", "yes", "yes"],
                 ["Проверка ходьбой", "no", "part", "yes", "yes"],
                 ["Отказ с причиной", "no", "no", "no", "yes"],
             ]},
            {"type": "text", "text": "Никто не отдаёт сразу опору в метрах, проверку ходьбой и честный отказ."},
        ],
    },
    {
        "nav": "Видение и показатели",
        "chain": 2,
        "title": "Снял — прошёл по уровню в браузере — забрал в движок",
        "ref": "Разделы 2.1 и 2.3",
        "blocks": [
            {"type": "tiles", "items": [
                ["Уровень без ручной доводки", "0% → 100%"],
                ["От отправки до проверки ходьбой", "2–4 часа → до 15 минут"],
                ["Брак получает отказ с причиной", "0% → 100%"],
                ["Треугольников в карте", "сотни тысяч → до 50 000"],
            ]},
            {"type": "scope",
             "in": "Съёмка на iPhone с датчиком глубины, сборка на сервере, проверка в браузере, файлы для движков",
             "out": "Игра, Android, текстуры, панель администрирования"},
        ],
    },
    {
        "nav": "Эпики и сценарий",
        "chain": 3,
        "title": "Шесть эпиков ведут к показателям; ключевая история — ходьба по карте",
        "ref": "Разделы 2.5–2.6",
        "blocks": [
            {"type": "trace", "items": [
                ["Цель: без ручной доводки", False],
                ["Показатель: проходимый уровень", False],
                ["Эпики: сборка, ходьба, файлы", False],
                ["История: пройти по карте в браузере", True],
            ]},
            {"type": "chips", "items": [
                ["Съёмка и проверка", False], ["Отправка и задания", False], ["Сборка и отчёт", False],
                ["Ходьба по карте", True], ["Файлы для движка", False], ["Тестовая ссылка", False],
            ]},
            {"type": "flow", "small": True, "items": [
                ["Рамка зоны", "", ""],
                ["Обход 10–30 секунд", "", ""],
                ["Проверка записи", "нет — «Переснять»", "late"],
                ["Отправить", "", ""],
                ["Задание в очереди", "", ""],
            ]},
        ],
    },
    {
        "nav": "Качество и право",
        "chain": 2,
        "title": "Быстро, только своим и по закону",
        "ref": "Разделы 2.7–2.8",
        "blocks": [
            {"type": "tiles", "items": [
                ["Сборка карты", "до 10 минут"],
                ["Открыть карту в браузере", "до 10 секунд"],
                ["Сервис доступен", "не меньше 99% времени"],
                ["Доступность веб-страниц", "уровень AA"],
            ]},
            {"type": "legal", "items": [
                ["Своя съёмка", "Договор с пользователем — регламент Евросоюза о защите данных, статья 6"],
                ["Случайные люди в кадре", "Законный интерес; лица крупным планом не публикуются"],
                ["Хранение", "До 90 дней, удаление по запросу — до 30 дней"],
                ["Библиотеки", "Только открытые лицензии"],
            ]},
        ],
    },
    {
        "nav": "Концепция и риски",
        "chain": 3,
        "title": "Телефон снимает, сервер собирает, браузер проверяет",
        "ref": "Разделы 2.4 и 2.9",
        "blocks": [{
            "type": "concept",
            "nodes": [
                ["Оператор", "Телефон", "съёмка с датчиком глубины", False],
                ["Система", "Сервер", "приём, очередь, сборка карты", True],
                ["Сборщик", "Браузер", "отчёт, ходьба, скачать", False],
            ],
            "arrows": ["съёмка →", "← карта и отчёт"],
            "external": ["Хостинг: база и файлы", "Игровые движки: Godot, Unity, Unreal"],
            "risks": [
                ["Карта неузнаваема", "Маленькая зона, обязательные позы камеры, отказ вместо случайной геометрии"],
                ["Опора не держит персонажа", "Проверка ходьбой до выдачи файлов"],
                ["Портрет пользователя не подтверждён", "Пять интервью до следующего релиза"],
            ],
        }],
    },
    {
        "nav": "Запасные слайды",
        "kind": "backup",
        "title": "Запасные слайды",
        "ref": "Требования к защите: запасные слайды",
        "blocks": [
            {"type": "backup", "items": [
                ["Раздел 1.3", "Полная таблица аналогов", "d01-analysis.html#analogs"],
                ["Приложение 1", "Все эпики и истории", "d04-backlog.html"],
                ["Раздел 2.9", "Таблица рисков", "d02-requirements.html#risks"],
                ["Раздел 2.6", "Полный текст сценариев", "d02-requirements.html#use-cases"],
            ]},
            {"type": "note", "text": "Показываются после доклада, по вопросам комиссии."},
        ],
    },
    {
        "nav": "Вопросы комиссии",
        "kind": "backup",
        "title": "Ответы на типовые вопросы комиссии",
        "ref": "Требования к защите: типовые вопросы комиссии",
        "blocks": [{"type": "qa", "items": [
            ["Как вы убедились, что проблема реальна?",
             "Анализ рынка и девяти аналогов: ни один не отдаёт опору в метрах и проверку ходьбой. Интервью пока не было — это отдельный риск, план: пять интервью с инди-разработчиками."],
            ["Чем решение лучше аналога?",
             "Это не сканер, а сборщик уровня: лёгкая опора, настоящие размеры, ходьба в браузере, честный отказ, повторяемость. Картинка проще — это осознанная граница."],
            ["Почему такие показатели и как их измерить?",
             "Каждый показатель — одна боль: ручная доводка, время, брак, вес карты. Измеряются прогоном четырёх эталонных съёмок по тестовой ссылке."],
            ["Что вне проекта и почему?",
             "Игра, Android, текстуры, своя модель глубины, панель администрирования. Один разработчик и фиксированный срок — в релиз входит только путь «снял — прошёл — забрал»."],
            ["Какие истории обязательны и что уберёте при нехватке времени?",
             "Пятнадцать обязательных историй, без которых не достичь показателей. Первыми уходят желательные: подсказка обхода, фильтр, сравнение сборок, рост персонажа, инструкция для Godot."],
            ["Какие персональные данные и на каком основании?",
             "Ключ устройства, видео участка, сетевые адреса в журналах. Регламент Евросоюза о защите данных, статья 6: договор и законный интерес; хранение до 90 дней, удаление по запросу."],
            ["Что самое рискованное?",
             "Качество карты. Снижаем маленькой зоной, обязательными позами камеры и отказом вместо случайной геометрии; проверяем ходьбой до выдачи."],
        ]}],
    },
]

MAIN = sum(1 for s in SLIDES if s.get("kind") not in ("title", "backup"))


def label(i: int, slide: dict) -> str:
    if slide.get("kind") == "title":
        return "Титул"
    if slide.get("kind") == "backup":
        return "После доклада"
    return f"{i} из {MAIN}"


# --- HTML ---------------------------------------------------------------------

e = html.escape


def cls(name: str) -> str:
    return f' class="{name}"' if name else ""


def block_html(b: dict) -> str:
    t = b["type"]
    if t == "title":
        people = "".join(f"<span>{e(p)}</span>" for p in b["people"])
        return (f'<div class="s-title"><p class="s-kicker">{e(b["kicker"])}</p><h1>{e(b["title"])}</h1>'
                f'<p class="s-sub">{e(b["sub"])}</p><div class="s-people">{people}</div></div>')
    if t == "number":
        return (f'<div class="s-split"><div class="s-number"><strong>{e(b["value"]).replace(" ", "&nbsp;")}</strong>'
                f'<span>{e(b["caption"])}</span></div><p class="s-text">{e(b["text"])}</p></div>')
    if t == "tasks":
        return '<ol class="s-tasks">' + "".join(f"<li><b>{e(a)}</b>{e(x)}</li>" for a, x in b["items"]) + "</ol>"
    if t == "cards":
        return '<div class="s-split">' + "".join(f'<div class="s-card"><span>{e(a)}</span>{e(x)}</div>' for a, x in b["items"]) + "</div>"
    if t == "flow":
        kind = "s-flow small" if b.get("small") else "s-flow"
        items = "".join(
            f'<li{cls(c)}>{e(x)}{f"<small>{e(s)}</small>" if s else ""}</li>'
            for x, s, c in b["items"])
        return f'<ol class="{kind}">{items}</ol>'
    if t == "matrix":
        return '<div class="s-matrix">' + "".join(
            f'<div{cls("hi" if hi else "")}><span>{e(a)}</span>{e(x)}</div>' for a, x, hi in b["items"]) + "</div>"
    if t == "check":
        marks = {"yes": "✓", "no": "✕", "part": "частично"}
        last = len(b["columns"])
        head = "<tr><th></th>" + "".join(f'<th{cls("us" if i == last else "")}>{e(c)}</th>' for i, c in enumerate(b["columns"], 1)) + "</tr>"
        rows = "".join(
            "<tr><td>" + e(r[0]) + "</td>" + "".join(
                f'<td class="{v}{" us" if i == last else ""}">{marks[v]}</td>' for i, v in enumerate(r[1:], 1)) + "</tr>"
            for r in b["rows"])
        return f'<table class="s-check">{head}{rows}</table>'
    if t == "text":
        return f'<p class="s-text">{e(b["text"])}</p>'
    if t == "note":
        return f'<p class="s-note">{e(b["text"])}</p>'
    if t == "tiles":
        return '<div class="s-tiles">' + "".join(f"<div><span>{e(a)}</span><b>{e(x)}</b></div>" for a, x in b["items"]) + "</div>"
    if t == "scope":
        return (f'<div class="s-split scope"><div class="in"><span>Входит</span>{e(b["in"])}</div>'
                f'<div class="out"><span>Не входит</span>{e(b["out"])}</div></div>')
    if t == "trace":
        return '<div class="s-trace">' + "<i>→</i>".join(
            f'<span{cls("hot" if hot else "")}>{e(x)}</span>' for x, hot in b["items"]) + "</div>"
    if t == "chips":
        return '<div class="s-chips">' + "".join(
            f'<span{cls("hot" if hot else "")}>{e(x)}</span>' for x, hot in b["items"]) + "</div>"
    if t == "legal":
        return '<div class="s-legal">' + "".join(f"<div><span>{e(a)}</span>{e(x)}</div>" for a, x in b["items"]) + "</div>"
    if t == "concept":
        n = [f'<div class="node{" main" if main else ""}"><span>{e(r)}</span><b>{e(name)}</b><small>{e(d)}</small></div>'
             for r, name, d, main in b["nodes"]]
        a = [f"<i>{e(x)}</i>" for x in b["arrows"]]
        ext = "".join(f'<div class="ext">{e(x)}</div>' for x in b["external"])
        risks = "".join(f"<li><b>{e(x)}</b>{e(y)}</li>" for x, y in b["risks"])
        return (f'<div class="s-concept"><div class="s-ctx">{n[0]}{a[0]}{n[1]}{a[1]}{n[2]}{ext}</div>'
                f'<ol class="s-risks">{risks}</ol></div>')
    if t == "backup":
        return '<div class="s-backup">' + "".join(f'<a href="{h}"><span>{e(a)}</span>{e(x)}</a>' for a, x, h in b["items"]) + "</div>"
    if t == "qa":
        return '<dl class="s-qa">' + "".join(f"<dt>{e(q)}</dt><dd>{e(a)}</dd>" for q, a in b["items"]) + "</dl>"
    raise ValueError(f"Неизвестный блок {t}")


PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Защита · NVC Maps</title>
  <link rel="stylesheet" href="wireframes.css?v=14" />
</head>
<body class="deck-view">
  <div class="deck-progress"><span></span></div>
  <main class="deck-stage">
{slides}
  </main>
  <nav class="deck-overview" hidden>
{overview}
  </nav>
  <footer class="deck-toolbar">
    <a class="deck-home" href="index.html">← Бизнес-анализ</a>
    <div class="deck-controls">
      <button type="button" data-go="-1" aria-label="Предыдущий слайд">◀</button>
      <span class="deck-pos"></span>
      <button type="button" data-go="1" aria-label="Следующий слайд">▶</button>
    </div>
    <div class="deck-actions">
      <button type="button" data-overview>Все слайды</button>
      <button type="button" data-fullscreen>Во весь экран</button>
      <a class="deck-download" href="NVC-Maps-защита.pptx" download="NVC-Maps-защита.pptx">Скачать презентацию</a>
    </div>
  </footer>
  <script>
{script}
  </script>
</body>
</html>
"""

SCRIPT = """    var slides = Array.prototype.slice.call(document.querySelectorAll(".s-slide"));
    var pos = document.querySelector(".deck-pos");
    var bar = document.querySelector(".deck-progress span");
    var overview = document.querySelector(".deck-overview");
    var current = 0;

    function show(i) {
      current = Math.max(0, Math.min(slides.length - 1, i));
      slides.forEach(function (s, k) { s.classList.toggle("on", k === current); });
      var s = slides[current];
      pos.textContent = s.dataset.label + " · " + s.dataset.nav;
      bar.style.width = ((current + 1) / slides.length * 100) + "%";
      if (location.hash !== "#" + current) history.replaceState(null, "", "#" + current);
    }
    function fromHash() {
      var n = parseInt(location.hash.slice(1), 10);
      show(isNaN(n) ? 0 : n);
    }
    function toggleOverview(force) {
      var open = typeof force === "boolean" ? force : overview.hidden;
      overview.hidden = !open;
    }
    function fullscreen() {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
    }

    document.querySelectorAll("[data-go]").forEach(function (b) {
      b.addEventListener("click", function () { show(current + Number(b.dataset.go)); });
    });
    document.querySelector("[data-overview]").addEventListener("click", function () { toggleOverview(); });
    document.querySelector("[data-fullscreen]").addEventListener("click", fullscreen);
    overview.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { toggleOverview(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      var k = e.key;
      if (k === "ArrowRight" || k === "PageDown" || k === " ") { e.preventDefault(); show(current + 1); }
      else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); show(current - 1); }
      else if (k === "Home") show(0);
      else if (k === "End") show(slides.length - 1);
      else if (k === "f" || k === "F" || k === "а" || k === "А") fullscreen();
      else if (k === "o" || k === "O" || k === "щ" || k === "Щ") toggleOverview();
      else if (k === "Escape") toggleOverview(false);
    });
    var touchX = null;
    document.addEventListener("touchstart", function (e) { touchX = e.touches[0].clientX; }, { passive: true });
    document.addEventListener("touchend", function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 60) show(current + (dx < 0 ? 1 : -1));
      touchX = null;
    });
    window.addEventListener("hashchange", fromHash);
    fromHash();"""


def chain_html(active: int | None) -> str:
    if active is None:
        return ""
    steps = [f'<span class="on">{s}</span>' if i == active else f"<span>{s}</span>" for i, s in enumerate(CHAIN)]
    return '      <div class="s-chain">' + "<i>→</i>".join(steps) + "</div>\n"


def render(site: Path) -> list[str]:
    sections, items = [], []
    for i, s in enumerate(SLIDES):
        head = "" if s.get("kind") == "title" else f'      <h2 class="s-head">{e(s["title"])}</h2>\n'
        body = "\n".join("      " + block_html(b) for b in s["blocks"])
        sections.append(
            f'    <section class="s-slide" id="s{i}" data-nav="{e(s["nav"])}" data-label="{label(i, s)}">\n'
            f'{chain_html(s.get("chain"))}{head}{body}\n'
            f'      <footer class="s-ref">{e(s["ref"])}</footer>\n'
            f"    </section>"
        )
        items.append(f'    <a href="#{i}"><span>{label(i, s)}</span>{e(s["nav"])}</a>')
    (site / DECK).write_text(PAGE.format(slides="\n".join(sections), overview="\n".join(items), script=SCRIPT))
    # Прежние отдельные страницы слайдов заменены одной презентацией.
    for old in site.glob("s[0-9][0-9]-*.html"):
        old.unlink()
    return [DECK]


def export_json(path: Path) -> None:
    """Данные для PowerPoint (scripts/build-pptx.mjs)."""
    data = {
        "chain": CHAIN,
        "siteUrl": SITE_URL,
        "slides": [{**s, "label": label(i, s)} for i, s in enumerate(SLIDES)],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1))
