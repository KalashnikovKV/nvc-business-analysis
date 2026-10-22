# Бизнес-анализ: NVC Maps

**Продукт:** система создания игровых 3D-карт по видеозаписи
**English:** A System for Creating 3D Game Maps from Video

Документ отвечает на два вопроса: зачем нужен продукт и что должен уметь пользователь. Его читают владелец продукта и команда. Как это устроено внутри — пороги, тестовые случаи, контракт API и поставка — описано в ТЗ.

Пакет согласован с [ТЗ](../diplom-docs-2026-09-27/explain/tz-sistema-igrovyh-3d-kart.md), разделы 9–10, и с [Blueprint](../diplom-docs-2026-09-27/explain/blueprint-pipeline-3d-kart.md). При расхождении главным считается ТЗ.

| Раздел | Файл |
|--------|------|
| Введение: проблема, цель и задачи, объект и предмет, методы | [00-introduction.md](00-introduction.md) |
| Глава 1. Аналитическая часть: AS-IS и TO-BE, источники, аналоги, выводы | [01-analytical-part.md](01-analytical-part.md) |
| Глава 2. Требования: видение и KPI, стейкхолдеры, границы, концепция, истории, сценарии, NFR, право, риски | [02-system-requirements.md](02-system-requirements.md) |
| Список источников и литературы (Chicago, генерируется из `references.json`) | [03-references.md](03-references.md) |
| Приложение 1. Бэклог (генерируется из 2.5) | [04-appendix-a-backlog.md](04-appendix-a-backlog.md) |
| Приложение 2. Диаграммы | [05-appendix-b-diagrams.md](05-appendix-b-diagrams.md) |
| Заявления: ИИ, вклад, согласие организации | [06-statements.md](06-statements.md) |
| Сайт с разделами и экранами | [wireframes/index.html](wireframes/index.html) · [на сайте](https://kalashnikovkv.github.io/nvc-business-analysis/) |
| Презентация для защиты: титул и 8 слайдов | [wireframes/deck.html](wireframes/deck.html) · [PowerPoint](wireframes/NVC-Maps-защита.pptx) |
| Подготовка к защите: ответы на вопросы комиссии, материалы после доклада | [wireframes/prep.html](wireframes/prep.html) |
| Весь анализ одним файлом | [NVC-Maps-бизнес-анализ.md](NVC-Maps-бизнес-анализ.md) · [PDF](wireframes/NVC-Maps-бизнес-анализ.pdf) · [DOCX для эксперта](wireframes/BA_Kalashnikov_Kirill.docx) |

## Сборка

```bash
python3 scripts/build-ba.py          # приложение 1, сводный файл, сайт, DOCX и PDF
python3 scripts/build-ba.py shots    # скриншоты макетов (после правки экранов)
```

Нужны Python с пакетами `markdown` и `Pillow`, Node.js (`npm install`, mermaid-cli через npx), Google Chrome, LibreOffice и poppler.

**Репозитории:** [`nvc-capture`](../nvc-capture) — съёмка; [`neuralVideoCartography`](../neuralVideoCartography) — сборка карты; сервис и веб-клиент — загрузка, статус, ходьба по карте.
