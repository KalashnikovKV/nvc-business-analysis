"""Слайды для защиты по «Defense and Presentation Requirements 2026/27».

Восемь слайдов и титульный: одна мысль на слайд, до 30 слов текста, крупный визуальный
элемент, внизу — ссылка на раздел работы. Сквозная линия: проблема → цель → KPI → эпик.
Плюс запасные слайды и ответы на типовые вопросы комиссии.

Цифры и формулировки берутся из разделов 00–02; при их правке слайды правятся здесь.
"""

from __future__ import annotations

from pathlib import Path

TOTAL = 8

# Сквозная линия: на каждом слайде подсвечено звено, о котором он.
CHAIN = ["Проблема", "Цель", "KPI", "Эпик"]

SLIDES = [
    {
        "file": "s00-title.html",
        "nav": "Титул",
        "title": "Система создания игровых 3D-карт по видеозаписи",
        "body": """
        <div class="slide-title">
          <p class="slide-kicker">NVC Maps · бакалаврский проект</p>
          <h1>Система создания игровых 3D-карт по видеозаписи</h1>
          <p class="slide-sub">A System for Creating 3D Game Maps from Video</p>
          <div class="slide-people">
            <span>Кирилл Калашников</span>
            <span>Руководитель: доц., канд. техн. наук С. В. Авдейчик</span>
          </div>
        </div>""",
        "ref": "Титульный лист",
        "no_head": True,
    },
    {
        "file": "s01-problem.html",
        "nav": "1 · Проблема",
        "chain": 0,
        "title": "Телефон снимает место, но не делает из него уровень",
        "body": """
        <div class="slide-grid two">
          <div class="big-number">
            <strong>70&nbsp;000</strong>
            <span>авторов карт в Fortnite в 2024 году — почти втрое больше, чем годом раньше</span>
          </div>
          <p class="slide-text">Опору для персонажа, упрощение и размеры делают вручную. Брак съёмки виден только в игровом движке.</p>
        </div>""",
        "ref": "Введение · Актуальность и проблема",
    },
    {
        "file": "s02-goal.html",
        "nav": "2 · Цель",
        "chain": 1,
        "title": "Один обход телефоном — и проходимый уровень без ручной доводки",
        "body": """
        <ol class="task-row">
          <li><b>1.1</b>Как сейчас</li>
          <li><b>1.2–1.3</b>Источники и аналоги</li>
          <li><b>2.1</b>Видение и KPI</li>
          <li><b>2.5–2.7</b>Требования</li>
          <li><b>2.8–2.10</b>Право, риски, оценка</li>
        </ol>
        <div class="slide-grid two">
          <div class="pill-card"><span>Объект</span>Создание уровня по реальному месту</div>
          <div class="pill-card"><span>Предмет</span>Проверка съёмки, сборка карты, ходьба в браузере</div>
        </div>""",
        "ref": "Введение · Цель и задачи, объект и предмет",
    },
    {
        "file": "s03-process.html",
        "nav": "3 · Процесс",
        "chain": 0,
        "title": "Время теряется на ручной доводке, данные — при экспорте",
        "body": """
        <ol class="flow">
          <li>Снять</li>
          <li>Выгрузить</li>
          <li class="lost">Почистить<small>вручную</small></li>
          <li class="lost">Опора<small>вручную</small></li>
          <li class="lost">Размеры<small>теряются</small></li>
          <li class="late">Проверка<small>только в движке</small></li>
        </ol>
        <div class="matrix-2x2">
          <div><span>Влияние ↑ · интерес ↑</span>Пользователи · Владелец продукта</div>
          <div><span>Влияние ↑ · интерес ↓</span>Apple · glTF · GDPR</div>
          <div><span>Влияние ~</span>Хостинг · Конкуренты</div>
          <div><span>Влияние ↓ · интерес ↑</span>Игрок · Владелец места · Человек в кадре</div>
        </div>""",
        "ref": "Разделы 1.1 и 2.2",
    },
    {
        "file": "s04-analogs.html",
        "nav": "4 · Аналоги",
        "chain": 0,
        "title": "Сканеры делают модель для просмотра, а не уровень",
        "body": """
        <table class="check-table">
          <tr><th></th><th>Polycam, Scaniverse, KIRI</th><th>World Labs Marble</th><th>Video2Game</th><th class="us">NVC Maps</th></tr>
          <tr><td>Размеры в метрах</td><td class="yes">✓</td><td class="no">✕</td><td class="no">✕</td><td class="us yes">✓</td></tr>
          <tr><td>Лёгкая опора</td><td class="no">✕</td><td class="part">~</td><td class="yes">✓</td><td class="us yes">✓</td></tr>
          <tr><td>Проверка ходьбой</td><td class="no">✕</td><td class="part">~</td><td class="yes">✓</td><td class="us yes">✓</td></tr>
          <tr><td>Отказ с причиной</td><td class="no">✕</td><td class="no">✕</td><td class="no">✕</td><td class="us yes">✓</td></tr>
        </table>
        <p class="slide-text">Никто не отдаёт сразу опору в метрах, проверку ходьбой и честный отказ.</p>""",
        "ref": "Разделы 1.3–1.4",
    },
    {
        "file": "s05-vision.html",
        "nav": "5 · Видение и KPI",
        "chain": 2,
        "title": "Снял — прошёл по уровню в браузере — забрал в движок",
        "body": """
        <div class="kpi-row">
          <div><span>KPI-1 · уровень без доводки</span><b>0% → 100%</b></div>
          <div><span>KPI-2 · до проверки ходьбой</span><b>2–4 ч → ≤15 мин</b></div>
          <div><span>KPI-3 · отказ на браке</span><b>0% → 100%</b></div>
          <div><span>KPI-4 · треугольников</span><b>сотни тыс. → ≤50 000</b></div>
        </div>
        <div class="slide-grid two scope">
          <div class="in"><span>Входит</span>iPhone с LiDAR · сборка на сервере · ходьба в браузере · пакет GLB</div>
          <div class="out"><span>Не входит</span>Игра · Android · текстуры · админка</div>
        </div>""",
        "ref": "Разделы 2.1, 2.3",
    },
    {
        "file": "s06-epics.html",
        "nav": "6 · Эпики",
        "chain": 3,
        "title": "Шесть эпиков ведут к KPI; ключевая история — ходьба по карте",
        "body": """
        <div class="trace">
          <span>BG-1 Без доводки</span><i>→</i><span>KPI-1</span><i>→</i><span>E3 · E4 · E5</span><i>→</i><span class="hot">US-4.1 Ходьба по карте</span>
        </div>
        <div class="epic-row">
          <span>E1 Съёмка</span><span>E2 Задания</span><span>E3 Сборка и отчёт</span>
          <span class="hot">E4 Ходьба</span><span>E5 Пакет</span><span>E6 Тестовая ссылка</span>
        </div>
        <ol class="flow small">
          <li>Рамка зоны</li><li>Обход 10–30 с</li><li>Проверка</li><li>Отправить</li><li>Задание в очереди</li>
        </ol>
        <p class="slide-note">UC-1. Если проверка не прошла — причина и «Переснять»; при обрыве повтор не запускает вторую сборку.</p>""",
        "ref": "Разделы 2.5–2.6",
    },
    {
        "file": "s07-nfr.html",
        "nav": "7 · NFR и право",
        "chain": 2,
        "title": "Быстро, только своим и по закону",
        "body": """
        <div class="kpi-row">
          <div><span>NFR-1 · сборка</span><b>≤ 10 мин</b></div>
          <div><span>NFR-2 · открыть карту</span><b>≤ 10 с</b></div>
          <div><span>NFR-8 · доступность</span><b>≥ 99%</b></div>
          <div><span>NFR-9 · веб-клиент</span><b>WCAG 2.1 AA</b></div>
        </div>
        <div class="legal-row">
          <div><span>GDPR ст. 6(1)(b)</span>своя съёмка</div>
          <div><span>GDPR ст. 6(1)(f)</span>случайные люди в кадре</div>
          <div><span>Хранение</span>≤ 90 дней, удаление ≤ 30 дней</div>
          <div><span>Лицензии</span>MIT · BSD · Apache-2.0</div>
        </div>""",
        "ref": "Разделы 2.7–2.8",
    },
    {
        "file": "s08-concept.html",
        "nav": "8 · Концепция и риски",
        "chain": 3,
        "title": "Телефон снимает, сервер собирает, браузер проверяет",
        "body": """
        <div class="slide-grid concept">
          <div class="ctx">
            <div class="ctx-node"><span>Оператор</span><b>Телефон</b><small>съёмка · ARKit · LiDAR</small></div>
            <i>съёмка →</i>
            <div class="ctx-node main"><span>Система</span><b>Сервер</b><small>приём · очередь · сборка карты</small></div>
            <i>← карта, отчёт</i>
            <div class="ctx-node"><span>Сборщик</span><b>Браузер</b><small>отчёт · ходьба · скачать</small></div>
            <div class="ctx-ext">Хостинг: база и файлы</div>
            <div class="ctx-ext">Движки: Godot · Unity · Unreal</div>
          </div>
          <ol class="risks">
            <li><b>R1 · Карта неузнаваема</b>Маленькая зона, обязательные позы, отказ</li>
            <li><b>R2 · Опора не держит</b>Проверка ходьбой до выдачи пакета</li>
            <li><b>R6 · Персона не подтверждена</b>5 интервью до следующего релиза</li>
          </ol>
        </div>""",
        "ref": "Разделы 2.4, 2.9",
    },
]

EXTRA = [
    {
        "file": "s09-backup.html",
        "nav": "Запасные слайды",
        "title": "Запасные слайды",
        "body": """
        <div class="backup-grid">
          <a href="d01-analysis.html#analogs"><span>1.3</span>Полная таблица аналогов</a>
          <a href="d04-backlog.html"><span>Прил. 1</span>Полный бэклог</a>
          <a href="d02-requirements.html#risks"><span>2.9</span>Таблица рисков</a>
          <a href="d02-requirements.html#use-cases"><span>2.6</span>Полный текст сценариев</a>
        </div>
        <p class="slide-note">Показываются после доклада по вопросам комиссии.</p>""",
        "ref": "Требования к защите · Backup slides",
    },
    {
        "file": "s10-questions.html",
        "nav": "Вопросы комиссии",
        "title": "Ответы на типовые вопросы комиссии",
        "body": """
        <dl class="qa">
          <dt>Как вы убедились, что проблема реальна?</dt>
          <dd>Анализ рынка и девяти аналогов: ни один не отдаёт опору в метрах и проверку ходьбой. Интервью не было — это риск R6, план: 5 интервью с инди-разработчиками.</dd>
          <dt>Чем решение лучше аналога?</dt>
          <dd>Это не сканер, а сборщик уровня: лёгкая опора, размеры датчика, ходьба в браузере, честный отказ, повторяемость. Картинка проще — это осознанная граница.</dd>
          <dt>Почему такие KPI и как их измерить?</dt>
          <dd>Каждый KPI — одна боль: доводка, время, брак, вес карты. Измеряются прогоном четырёх эталонных съёмок по тестовой ссылке.</dd>
          <dt>Что вне проекта и почему?</dt>
          <dd>Игра, Android, текстуры, своя модель глубины, админка. Один разработчик и фиксированный срок — в релиз входит только путь «снял — прошёл — забрал».</dd>
          <dt>Какие истории Must и что уберёте при нехватке времени?</dt>
          <dd>Must — 15 историй без которых не достичь KPI. Первыми уходят Should: подсказка обхода, фильтр, сравнение сборок, рост персонажа, инструкция для Godot.</dd>
          <dt>Какие персональные данные и на каком основании?</dt>
          <dd>Ключ устройства, видео участка, IP в журналах. GDPR ст. 6(1)(b) и 6(1)(f), минимизация, хранение до 90 дней, удаление по запросу.</dd>
          <dt>Что самое рискованное?</dt>
          <dd>Качество карты (R1). Снижаем маленькой зоной, обязательными позами и отказом вместо произвольной геометрии; проверяем ходьбой до выдачи.</dd>
        </dl>""",
        "ref": "Требования к защите · Typical committee questions",
    },
]

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{nav} · Защита · NVC Maps</title>
  <link rel="stylesheet" href="wireframes.css?v=12" />
</head>
<body class="deck">
  <header class="deck-bar">
    <a href="index.html">← Бизнес-анализ</a>
    <span>{counter}</span>
  </header>
  <main class="slide">
{chain}{head}
{body}
    <footer class="slide-ref">{ref}</footer>
  </main>
  <nav class="deck-nav">
    {prev}
    {next}
  </nav>
  <script>
    document.addEventListener("keydown", function (e) {{
      var link = e.key === "ArrowRight" ? document.querySelector("[data-next]") : e.key === "ArrowLeft" ? document.querySelector("[data-prev]") : null;
      if (link) location.href = link.getAttribute("href");
    }});
  </script>
</body>
</html>
"""


def chain_html(active: int | None) -> str:
    if active is None:
        return ""
    parts = []
    for i, step in enumerate(CHAIN):
        cls = ' class="on"' if i == active else ""
        parts.append(f"<span{cls}>{step}</span>")
    return '    <div class="chain">' + "<i>→</i>".join(parts) + "</div>\n"


def render(site: Path) -> list[str]:
    pages = SLIDES + EXTRA
    written = []
    for i, s in enumerate(pages):
        main_index = i if i <= TOTAL else None
        counter = f"Слайд {i} / {TOTAL}" if main_index and main_index > 0 else ("Титул" if i == 0 else s["nav"])
        prev = f'<a data-prev href="{pages[i - 1]["file"]}">← {pages[i - 1]["nav"]}</a>' if i > 0 else "<span></span>"
        nxt = f'<a data-next href="{pages[i + 1]["file"]}">{pages[i + 1]["nav"]} →</a>' if i + 1 < len(pages) else "<span></span>"
        (site / s["file"]).write_text(PAGE.format(
            nav=s["nav"], counter=counter, chain=chain_html(s.get("chain")),
            head="" if s.get("no_head") else f'    <h2 class="slide-head">{s["title"]}</h2>\n',
            body=s["body"], ref=s["ref"], prev=prev, next=nxt,
        ))
        written.append(s["file"])
    return written
