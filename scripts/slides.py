"""Презентация для защиты по «Defense and Presentation Requirements 2026/27».

Доклад и слайды — на английском. Восемь слайдов и титульный: одна мысль на слайд, до 30 слов
текста, крупный визуальный элемент, внизу — ссылка на раздел работы. Цепочка
«проблема → цель → показатель → эпик → история» показана на слайде 6.
У каждого слайда в ``notes`` — текст доклада простым английским (уровень A2); он попадает
в заметки докладчика PowerPoint. Ответы на вопросы комиссии — в отдельном документе, не здесь.

На слайдах нет идентификаторов (KPI, NFR, US-4.1 и т. п.) — только слова.
Цифры берутся из английских разделов en/00–02; при их правке слайды правятся здесь.

Содержимое описано данными: из него собираются и страница deck.html (render),
и PowerPoint (scripts/build-pptx.mjs читает export_json).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

DECK = "deck.html"
PPTX = "NVC-Maps-defense.pptx"

SLIDES = [
    {
        "nav": "Opening",
        "kind": "title",
        "ref": "Title page",
        "blocks": [{
            "type": "title",
            "kicker": "NVC Maps · Bachelor project · European Humanities University, Informatics",
            "title": "A System for Creating 3D Game Maps from Video",
            "sub": "Kirill Kalashnikov",
            "people": ["Supervisor: Associate Professor Sergey Avdeychik, Candidate of Technical Sciences"],
        }],
        "notes": "Good morning. My name is Kirill Kalashnikov. My project is called NVC Maps. "
                 "It is a system for creating 3D game maps from video.",
    },
    {
        "nav": "Problem",
        "title": "A phone scan is not a game level",
        "ref": "Introduction: relevance and problem",
        "blocks": [{
            "type": "number",
            "value": "70,000",
            "caption": "Fortnite map makers in 2024. A year before: 24,000.",
            "text": "Scans are heavy, have no character floor and lose the real size.",
        }],
        "notes": "Many people make small games today. In 2024, the number of Fortnite map makers grew "
                 "from 24,000 to 70,000. Many of them want a level from a real place, for example a desk "
                 "or a small room. A phone can scan a place. But a scan is not a game level. It is too heavy. "
                 "It has no floor for the character. The size is often wrong. People fix it by hand, "
                 "and this takes hours.",
    },
    {
        "nav": "Goal",
        "title": "One walk with a phone → a walkable level",
        "ref": "Introduction: goal, objectives, object and subject",
        "blocks": [
            {"type": "tasks", "items": [
                ["Objective 1", "Losses"],
                ["Objective 2", "Analogs"],
                ["Objective 3", "Targets"],
                ["Objective 4", "Requirements"],
                ["Objective 5", "Law and risks"],
            ]},
            {"type": "cards", "items": [
                ["Object", "A game level from a real place"],
                ["Subject", "Capture check, build, walk check"],
            ]},
        ],
        "notes": "The goal of my project is simple. One walk around a place with a phone must give "
                 "a game level. The character can walk on it, and nobody fixes it by hand. I had five tasks. "
                 "I studied the current process. I compared similar products. I set targets with numbers. "
                 "I wrote the requirements. And I described the tests, the law and the risks.",
    },
    {
        "nav": "Current process",
        "title": "Time is lost on fixing, data on export",
        "ref": "Sections 1.1 and 2.2",
        "blocks": [
            {"type": "flow", "items": [
                ["Capture", "", ""],
                ["Export", "size lost", "lost"],
                ["Clean up", "by hand", "lost"],
                ["Build floor", "by hand", "lost"],
                ["Engine test", "too late", "late"],
                ["Redo", "", "late"],
            ]},
            {"type": "text", "text": "Key: users, product owner. Rules: Apple, game engines, data law."},
        ],
        "notes": "This is how people work today. They scan a place with an app, for example Polycam. "
                 "They export the model. Then they clean it by hand in Blender. They also build a simple "
                 "hidden floor for the character. This takes the most time. Often the real size gets lost here. "
                 "Only in the game engine do they see the problems. If the scan was bad, they start again. "
                 "The key people are the users and the product owner. Apple, the game engines and the data "
                 "protection law give us rules.",
    },
    {
        "nav": "Analogs",
        "title": "Nobody gives all four together",
        "ref": "Sections 1.3–1.4",
        "blocks": [
            {"type": "check",
             "columns": ["Polycam", "World Labs Marble", "Video2Game", "NVC Maps"],
             "rows": [
                 ["Real size", "yes", "no", "none", "yes"],
                 ["Character floor", "no", "yes", "yes", "yes"],
                 ["Walk check", "none", "part", "yes", "yes"],
                 ["Honest rejection", "none", "none", "none", "yes"],
             ]},
            {"type": "note", "text": "— not claimed. Analogs have better pictures: not our goal."},
        ],
        "notes": "I compared seven similar products. Here you see four criteria. Scanners like Polycam keep "
                 "the real size. But they do not make a floor for the character. World Labs Marble has this "
                 "floor, but its world is not a real place. Video2Game can check walking, but it is a research "
                 "project. And no product says: \"This capture is bad, and here is why.\" So nobody gives all "
                 "four things together. The other products have better pictures. But my goal is different: "
                 "a level that works in a game.",
    },
    {
        "nav": "Vision and targets",
        "title": "Capture → walk → take to the engine",
        "ref": "Sections 2.1 and 2.3",
        "blocks": [
            {"type": "tiles", "items": [
                ["No manual fixing", "0% → 100%"],
                ["Time to check", "2–4 hours → 15 minutes"],
                ["Honest rejection", "0% → 100%"],
                ["Map triangles", "≤ 50,000"],
            ]},
            {"type": "scope",
             "in": "iPhone app, server, browser",
             "out": "Game, Android, textures"},
        ],
        "notes": "My idea in one line: capture the place, walk on it in the browser, take it to the game "
                 "engine. I have four goals, and each goal has a number. First, no manual fixing: from zero "
                 "to one hundred percent. Second, time: from two to four hours down to fifteen minutes. "
                 "Third, every bad capture gets a reason. Fourth, the map is light: no more than fifty thousand "
                 "triangles. The project has an iPhone app, a server and a website. A full game, Android and "
                 "textures are not part of it.",
    },
    {
        "nav": "Epics and scenario",
        "title": "From problem to story",
        "ref": "Sections 2.5–2.6",
        "blocks": [
            {"type": "trace", "items": [
                ["Problem: manual fixing", False],
                ["Goal: no fixing", False],
                ["Target: 100% walkable", False],
                ["Epic: walk check", False],
                ["Story: walk the map in a browser", True],
            ]},
            {"type": "chips", "items": [
                ["Capture", False], ["Upload", False], ["Build", False],
                ["Walk check", True], ["Files", False], ["Operation", False],
            ]},
            {"type": "flow", "small": True, "items": [
                ["Open link", "", ""],
                ["Open job", "", ""],
                ["Walk across", "", ""],
                ["Download", "", ""],
            ]},
        ],
        "notes": "Now, how the problem leads to the work. The problem is manual fixing. The goal is no manual "
                 "fixing. The target is one hundred percent of good captures. The epic is \"Walk check in the "
                 "browser\". The key user story is: \"As a map builder, I want to walk a character on the map in "
                 "the browser, so that I can check it without a game engine.\" There are six epics and fourteen "
                 "\"Must\" stories. The key scenario has four steps: open the link from the phone, open the job, "
                 "walk from one side to the other, and download the files.",
    },
    {
        "nav": "Quality and law",
        "title": "Fast, private and legal",
        "ref": "Sections 2.7–2.8",
        "blocks": [
            {"type": "tiles", "items": [
                ["Build", "≤ 10 minutes"],
                ["Map opens", "≤ 10 seconds"],
                ["Access", "Owner only"],
                ["Uptime", "≥ 99%"],
            ]},
            {"type": "legal", "items": [
                ["Data", "User key, video, network address"],
                ["Basis", "EU data law, article 6"],
                ["Kept", "90 days, deleted on request"],
            ]},
        ],
        "notes": "Here are the main quality rules. A build takes no more than ten minutes. The map opens in "
                 "ten seconds. Only the owner can see their jobs. The service works ninety-nine percent of the "
                 "time. Now the law. We follow the GDPR. The personal data are the user key, the video and IP "
                 "addresses. The legal basis is the contract and legitimate interest. We keep the data for "
                 "ninety days. On request, we delete it within thirty days.",
    },
    {
        "nav": "Concept and risks",
        "title": "Phone captures, server builds, browser checks",
        "ref": "Sections 2.4 and 2.9",
        "blocks": [{
            "type": "concept",
            "nodes": [
                ["User", "Phone", "video, depth", False],
                ["System", "Server", "builds the map", True],
                ["Builder", "Browser", "report, walk, files", False],
            ],
            "arrows": ["capture →", "← map"],
            "external": ["Hosting", "Godot, Unity, Unreal"],
            "risks": [
                ["Map holes", "Small area, rejection"],
                ["Character falls", "Walk check first"],
                ["No interviews yet", "Five interviews planned"],
            ],
        }],
        "notes": "This is the solution. The phone records the video and the depth. The server builds the map. "
                 "The browser shows the report, and you can walk on the map. Then the files go to Godot, Unity "
                 "or Unreal. There are three main risks. One: the map can have holes. So we use a small area and "
                 "we reject bad captures. Two: the character can fall through the floor. So we check walking "
                 "before the download. Three: I have not talked to real users yet. I plan five interviews before "
                 "the next release. Thank you for your attention.",
    },
]

MAIN = sum(1 for s in SLIDES if s.get("kind") != "title")


def label(i: int, slide: dict) -> str:
    if slide.get("kind") == "title":
        return "Title"
    return f"{i} of {MAIN}"


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
        marks = {"yes": "✓", "no": "✕", "part": "partly", "none": "—"}
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
        return (f'<div class="s-split scope"><div class="in"><span>In</span>{e(b["in"])}</div>'
                f'<div class="out"><span>Out</span>{e(b["out"])}</div></div>')
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
    raise ValueError(f"Неизвестный блок {t}")


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Defense · NVC Maps</title>
  <link rel="stylesheet" href="wireframes.css?v=15" />
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
    <a class="deck-home" href="index.html">← Business analysis</a>
    <div class="deck-controls">
      <button type="button" data-go="-1" aria-label="Previous slide">◀</button>
      <span class="deck-pos"></span>
      <button type="button" data-go="1" aria-label="Next slide">▶</button>
    </div>
    <div class="deck-actions">
      <button type="button" data-overview>All slides</button>
      <button type="button" data-fullscreen>Full screen</button>
      <a class="deck-download" href="{pptx}" download="{pptx}">Download PowerPoint</a>
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


def render(site: Path) -> list[str]:
    sections, items = [], []
    for i, s in enumerate(SLIDES):
        head = "" if s.get("kind") == "title" else f'      <h2 class="s-head">{e(s["title"])}</h2>\n'
        body = "\n".join("      " + block_html(b) for b in s["blocks"])
        sections.append(
            f'    <section class="s-slide" id="s{i}" data-nav="{e(s["nav"])}" data-label="{label(i, s)}">\n'
            f'{head}{body}\n'
            f'      <footer class="s-ref">{e(s["ref"])}</footer>\n'
            f"    </section>"
        )
        items.append(f'    <a href="#{i}"><span>{label(i, s)}</span>{e(s["nav"])}</a>')
    (site / DECK).write_text(PAGE.format(slides="\n".join(sections), overview="\n".join(items), script=SCRIPT, pptx=PPTX))
    # Прежние отдельные страницы слайдов заменены одной презентацией.
    for old in site.glob("s[0-9][0-9]-*.html"):
        old.unlink()
    return [DECK]


def export_json(path: Path) -> None:
    """Данные для PowerPoint (scripts/build-pptx.mjs)."""
    data = {
        "slides": [{**s, "label": label(i, s)} for i, s in enumerate(SLIDES)],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1))
