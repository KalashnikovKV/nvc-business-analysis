// Собрать DOCX блока бизнес-анализа из Markdown-разделов.
// Вызывается из scripts/build-ba.py: node scripts/build-docx.mjs <input.json>
// input.json: { root, out, sections: [...], title: {...}, toc: [{text, level, page}] | null }

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { marked } from "marked";
import {
  AlignmentType, BorderStyle, Document, ExternalHyperlink, Header, HeadingLevel, ImageRun,
  LevelFormat, Packer, PageNumber, PageOrientation, Paragraph, ShadingType, Table, TableCell, TableLayoutType,
  TableOfContents, TableRow, TabStopType, TextRun, WidthType,
} from "docx";

const input = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const ROOT = input.root;

// A4, поля по правилам ЕГУ: слева 25 мм, справа 10 мм, сверху и снизу 20 мм.
const PAGE = { width: 11906, height: 16838 };
const MARGIN = { top: 1134, right: 567, bottom: 1134, left: 1417 };
const TEXT_WIDTH = PAGE.width - MARGIN.left - MARGIN.right; // 9922 DXA
const LAND_TEXT_WIDTH = PAGE.height - MARGIN.left - MARGIN.right; // 14854 DXA на альбомной странице
const INDENT = 709; // абзацный отступ 1,25 см
const CAPTION_SIZE = 22; // подписи к таблицам и рисункам — 11 pt
const FONT = "Times New Roman";
const BODY_SIZE = 24; // 12 pt
const TABLE_SIZE = 20; // 10 pt
const MAX_IMG_W = 640; // ≈ 17 см при 96 dpi
const MAX_IMG_H = 800; // ≈ 21 см

const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'");

// --- Ссылки на источники (IEEE) ---------------------------------------------
// [@key; @key] в тексте → номера по порядку первого упоминания: [3], [5] или [2]–[4].

const CITATIONS = input.citations;

function citeLabel(nums) {
  nums = [...new Set(nums)].sort((a, b) => a - b);
  const groups = [];
  let start = 0;
  for (let i = 1; i <= nums.length; i++) {
    if (i === nums.length || nums[i] !== nums[i - 1] + 1) {
      const run = nums.slice(start, i);
      groups.push(run.length >= 3 ? `[${run[0]}]–[${run.at(-1)}]` : run.map((n) => `[${n}]`).join(", "));
      start = i;
    }
  }
  return groups.join(", ");
}

function withCitations(markdown) {
  return markdown.replace(/\[@([^\]]+)\]/g, (_, list) => {
    const keys = list.split(";").map((k) => k.trim().replace(/^@/, ""));
    const nums = keys.map((k) => {
      if (!CITATIONS[k]) throw new Error(`Нет номера для источника ${k}`);
      return CITATIONS[k];
    });
    // Квадратные скобки экранируются, чтобы marked не принял номер за ссылку.
    return citeLabel(nums).replace(/\[/g, "\\[").replace(/\]/g, "\\]");
  });
}

// --- Inline ------------------------------------------------------------------

function inline(tokens, style = {}) {
  const runs = [];
  for (const t of tokens || []) {
    switch (t.type) {
      case "strong":
        runs.push(...inline(t.tokens, { ...style, bold: true }));
        break;
      case "em":
        runs.push(...inline(t.tokens, { ...style, italics: true }));
        break;
      case "codespan":
        runs.push(new TextRun({ ...style, text: decode(t.text), font: "Courier New", size: (style.size || BODY_SIZE) - 2 }));
        break;
      case "link":
        runs.push(new ExternalHyperlink({
          link: t.href,
          children: inline(t.tokens, { ...style, color: "0F5C55" }).map((r) => r),
        }));
        break;
      case "br":
        runs.push(new TextRun({ ...style, break: 1 }));
        break;
      case "text":
        if (t.tokens && t.tokens.length) runs.push(...inline(t.tokens, style));
        else runs.push(new TextRun({ ...style, text: decode(t.text) }));
        break;
      case "escape":
        runs.push(new TextRun({ ...style, text: decode(t.text) }));
        break;
      case "image":
        break;
      default:
        if (t.text) runs.push(new TextRun({ ...style, text: decode(t.text) }));
    }
  }
  return runs;
}

const plain = (tokens) =>
  (tokens || []).map((t) => (t.tokens ? plain(t.tokens) : decode(t.text || ""))).join("");

// --- Изображения -----------------------------------------------------------

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function imageParagraphs(file, caption, maxW = MAX_IMG_W, maxH = MAX_IMG_H) {
  const { w, h } = pngSize(file);
  let width = maxW;
  let height = Math.round((h * width) / w);
  if (height > maxH) {
    height = maxH;
    width = Math.round((w * height) / h);
  }
  const out = [new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: Boolean(caption),
    spacing: { before: 120, after: caption ? 60 : 160, line: 240 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width, height } })],
  })];
  if (caption) {
    out.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 240, line: 240 },
      children: [new TextRun({ text: caption, size: CAPTION_SIZE })],
    }));
  }
  return out;
}

function diagramFile(code) {
  const hash = crypto.createHash("sha1").update(code + "\n", "utf8").digest("hex").slice(0, 12);
  const file = path.join(ROOT, ".build", `diagram-${hash}.png`);
  if (!fs.existsSync(file)) throw new Error(`Нет отрисованной диаграммы ${file}`);
  return file;
}

// --- Таблицы -----------------------------------------------------------------

function columnWidths(header, rows, textWidth = TEXT_WIDTH) {
  const n = header.length;
  const CHAR = 125; // ширина символа 10 pt (полужирный в заголовке) в DXA с запасом
  const cols = [...Array(n)].map((_, i) => {
    const texts = [header[i], ...rows.map((r) => r[i])].map((c) => plain(c.tokens));
    const lens = texts.map((s) => s.length);
    const word = Math.max(...texts.flatMap((s) => s.split(/\s+/).map((w) => w.length)));
    return {
      max: Math.max(...lens),
      mean: lens.reduce((a, b) => a + b, 0) / lens.length,
      min: Math.min(2600, Math.round((word + 3) * CHAR)),
    };
  });
  // Короткие столбцы (ID, оценки, приоритет) — по самому длинному значению.
  const base = cols.map((c) => (c.max <= 14 ? Math.max(c.min, (c.max + 3) * CHAR) : c.min));
  const free = Math.max(0, textWidth - base.reduce((a, b) => a + b, 0));
  const weights = cols.map((c) => (c.max <= 14 ? 0 : Math.pow(Math.max(c.mean, 8), 0.75)));
  const wsum = weights.reduce((a, b) => a + b, 0) || 1;
  let widths = base.map((b, i) => b + Math.round((free * weights[i]) / wsum));
  const total = widths.reduce((a, b) => a + b, 0);
  if (total !== textWidth) widths = widths.map((w) => Math.floor((w * textWidth) / total));
  widths[widths.length - 1] += textWidth - widths.reduce((a, b) => a + b, 0);
  return widths;
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(tokens, width, headerRow) {
  const keepNext = headerRow;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    shading: headerRow ? { type: ShadingType.CLEAR, color: "auto", fill: "EDEDED" } : undefined,
    children: [new Paragraph({
      keepNext,
      spacing: { before: 0, after: 0, line: 240 },
      children: inline(tokens, { size: TABLE_SIZE, bold: headerRow || undefined }),
    })],
  });
}

function table(t, textWidth = TEXT_WIDTH) {
  const widths = columnWidths(t.header, t.rows);
  const rows = [
    new TableRow({ tableHeader: true, cantSplit: true, children: t.header.map((c, i) => cell(c.tokens, widths[i], true)) }),
    ...t.rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c.tokens, widths[i], false)) })),
  ];
  return [
    new Table({ width: { size: textWidth, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows }),
    new Paragraph({ spacing: { before: 0, after: 120, line: 240 }, children: [] }),
  ];
}

// --- Блоки -------------------------------------------------------------------

let listInstance = 0;
const HEADINGS = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3, 4: HeadingLevel.HEADING_4 };

function list(t, level = 0) {
  const out = [];
  const instance = ++listInstance;
  for (const item of t.items) {
    for (const sub of item.tokens) {
      if (sub.type === "list") {
        out.push(...list(sub, level + 1));
        continue;
      }
      const tokens = sub.type === "text" || sub.type === "paragraph" ? sub.tokens || [{ type: "text", text: sub.text }] : [];
      out.push(new Paragraph({
        numbering: { reference: t.ordered ? "numbers" : "bullets", level, instance: t.ordered ? instance : undefined },
        alignment: /https?:\/\//.test(sub.raw || "") ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
        spacing: { after: 60 },
        children: inline(tokens),
      }));
    }
  }
  return out;
}

function blocks(tokens, opts = {}) {
  let firstHeading = true;
  const out = [];
  const nextBlock = (i) => tokens.slice(i + 1).find((x) => x.type !== "space");
  for (const [i, t] of tokens.entries()) {
    switch (t.type) {
      case "heading": {
        // Приложение по правилам ЕГУ: «ПРИЛОЖЕНИЕ N» в правом верхнем углу, под ним содержательный заголовок.
        const appendix = t.depth === 1 && plain(t.tokens).match(/^Приложение (\d+)\. (.+)$/);
        if (appendix) {
          out.push(new Paragraph({
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.RIGHT,
            pageBreakBefore: !(opts.noBreakFirst && firstHeading),
            spacing: { before: 0, after: 120 },
            children: [new TextRun({ text: `ПРИЛОЖЕНИЕ ${appendix[1]}` })],
          }));
          out.push(new Paragraph({
            alignment: AlignmentType.CENTER,
            keepNext: true,
            spacing: { before: 120, after: 360 },
            children: [new TextRun({ text: appendix[2], bold: true })],
          }));
          firstHeading = false;
          break;
        }
        out.push(new Paragraph({
          heading: HEADINGS[t.depth] || HeadingLevel.HEADING_4,
          pageBreakBefore: t.depth === 1 && !(opts.noBreakFirst && firstHeading),
          // Заголовки разделов и структурных частей — прописными (правила ЕГУ).
          children: t.depth === 1 ? [new TextRun({ text: plain(t.tokens).toUpperCase() })] : inline(t.tokens),
        }));
        firstHeading = false;
        break;
      }
      case "paragraph": {
        const img = t.tokens.length === 1 && t.tokens[0].type === "image" ? t.tokens[0] : null;
        if (img) {
          const file = path.join(ROOT, decodeURI(img.href));
          out.push(...imageParagraphs(file, decode(img.text)));
        } else if (/^(Табл\.|Рис\.) /.test(t.text) || (nextBlock(i)?.type === "table" && !/[.:]$/.test(t.text.trim()))) {
          // Подпись: заголовок таблицы — над таблицей, «Рис.» — под рисунком.
          const above = !t.text.startsWith("Рис.");
          out.push(new Paragraph({
            alignment: AlignmentType.CENTER,
            keepNext: above,
            spacing: { before: above ? 120 : 0, after: above ? 60 : 240, line: 240 },
            children: inline(t.tokens, { size: CAPTION_SIZE }),
          }));
        } else {
          // Фраза со ссылкой на таблицу не отрывается от её подписи.
          const beforeCaption = nextBlock(i)?.type === "paragraph" && /^Табл\. /.test(nextBlock(i).text);
          // Записи списка литературы с длинными ссылками — по левому краю, без растянутых пробелов.
          const reference = /^\[\d+\]/.test(plain(t.tokens));
          out.push(new Paragraph({
            alignment: reference ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
            indent: { firstLine: INDENT },
            keepNext: beforeCaption,
            children: inline(t.tokens),
          }));
        }
        break;
      }
      case "list":
        out.push(...list(t));
        break;
      case "table":
        out.push(...table(t, opts.textWidth));
        break;
      case "code":
        if (t.lang === "mermaid") out.push(...imageParagraphs(diagramFile(t.text), null, opts.maxW, opts.maxH));
        else
          for (const line of t.text.split("\n"))
            out.push(new Paragraph({ spacing: { after: 0, line: 240 }, children: [new TextRun({ text: line, font: "Courier New", size: 18 })] }));
        break;
      case "blockquote":
        out.push(new Paragraph({ indent: { left: 567 }, children: inline(t.tokens.flatMap((x) => x.tokens || []), { italics: true }) }));
        break;
      default:
        break;
    }
  }
  return out;
}

// --- Титул и оглавление ------------------------------------------------------

function titlePage(t) {
  const p = (text, opts = {}) => new Paragraph({
    alignment: opts.align || AlignmentType.CENTER,
    spacing: { before: opts.before || 0, after: opts.after ?? 0, line: 360 },
    children: [new TextRun({ text, bold: opts.bold })],
  });
  return [
    p("ЕВРОПЕЙСКИЙ ГУМАНИТАРНЫЙ УНИВЕРСИТЕТ", { bold: true }),
    p(`Академический департамент ${t.department}`),
    p(t.program, { after: 1200 }),
    p(t.author_caps, { bold: true }),
    p(`Студент ${t.course} курса`, { after: 2000 }),
    p(t.topic_ru.toUpperCase(), { bold: true }),
    p(t.topic_en.toUpperCase(), { after: 600 }),
    p("БАКАЛАВРСКИЙ ПРОЕКТ", { bold: true }),
    p(t.block),
    p(`Тип проекта: ${t.type}`, { after: 2000 }),
    p(`Руководитель: ${t.supervisor}`, { align: AlignmentType.RIGHT, after: 2400 }),
    p(`Вильнюс, ${t.year}`),
  ];
}

function tocBlock() {
  const heading = new Paragraph({
    alignment: AlignmentType.CENTER,
    pageBreakBefore: true,
    spacing: { before: 240, after: 240 },
    children: [new TextRun({ text: "СОДЕРЖАНИЕ", bold: true })],
  });
  return [heading, new TableOfContents("Содержание", { hyperlink: true, headingStyleRange: "1-2" })];
}

// --- Документ ----------------------------------------------------------------

// Альбомная страница: текст 25 × 17 см.
const LAND_W = Math.floor(((PAGE.height - MARGIN.left - MARGIN.right) / 1440) * 96);
const LAND_H = Math.floor(((PAGE.width - MARGIN.top - MARGIN.bottom) / 1440) * 96) - 160;

// Номер страницы — в правом верхнем углу; на титульном листе не ставится.
const headers = {
  first: new Header({ children: [new Paragraph({ children: [] })] }),
  default: new Header({ children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun({ children: [PageNumber.CURRENT] })],
  })] }),
};
const sections = [];
function pushSection(children, landscape = false) {
  if (!children.length) return;
  sections.push({
    properties: {
      titlePage: sections.length === 0,
      page: {
        size: landscape ? { ...PAGE, orientation: PageOrientation.LANDSCAPE } : PAGE,
        margin: { ...MARGIN, header: 567, footer: 567 },
      },
    },
    headers,
    children,
  });
}

let current = [...titlePage(input.title), ...tocBlock()];
let startsSection = false;
for (const file of input.sections) {
  const tokens = marked.lexer(withCitations(fs.readFileSync(path.join(ROOT, file), "utf8")));
  const hasDiagrams = tokens.some((x) => x.type === "code" && x.lang === "mermaid");
  if (!hasDiagrams) {
    // Широкие таблицы между <!-- landscape --> и <!-- /landscape --> — на альбомной странице.
    let segment = [];
    let wide = false;
    const flush = () => {
      if (!segment.length) return;
      if (wide) {
        pushSection(current, false);
        pushSection(blocks(segment, { textWidth: LAND_TEXT_WIDTH }), true);
        current = [];
      } else {
        current.push(...blocks(segment, { noBreakFirst: startsSection }));
        startsSection = false;
      }
      segment = [];
    };
    for (const tk of tokens) {
      if (tk.type === "html" && /<!--\s*\/?landscape\s*-->/.test(tk.raw)) {
        flush();
        wide = !/\/landscape/.test(tk.raw);
        continue;
      }
      segment.push(tk);
    }
    flush();
    continue;
  }
  // Приложение с диаграммами: каждая диаграмма на своей странице, широкие — в альбомной ориентации.
  // Группа = текст перед диаграммой, сама диаграмма и подпись под ней.
  const groups = [[]];
  for (const tk of tokens) {
    if (tk.type === "code" && tk.lang === "mermaid" && groups[groups.length - 1].some((x) => x.type === "code")) groups.push([]);
    groups[groups.length - 1].push(tk);
  }
  groups.unshift([]);
  // Заголовок приложения — на одной странице с первой диаграммой.
  if (groups.length > 1) groups[1] = [...groups[0], ...groups[1]];
  else current.push(...blocks(groups[0], { noBreakFirst: startsSection }));
  for (const group of groups.slice(1)) {
    const code = group.find((x) => x.type === "code" && x.lang === "mermaid");
    const size = code ? pngSize(diagramFile(code.text)) : { w: 1, h: 1 };
    const landscape = size.w / size.h > 1.15;
    const box = landscape ? { maxW: LAND_W, maxH: LAND_H } : { maxW: MAX_IMG_W, maxH: MAX_IMG_H };
    if (current.length) {
      pushSection(current, false);
      current = [];
    }
    pushSection(blocks(group, { ...box, noBreakFirst: true }), landscape);
  }
  startsSection = true;
}
pushSection(current, false);

const doc = new Document({
  creator: input.title.author_en,
  title: input.title.topic_en,
  styles: {
    default: { document: { run: { font: FONT, size: BODY_SIZE }, paragraph: { spacing: { after: 120, line: 360 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: BODY_SIZE, bold: true, color: "000000" },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360, line: 360 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: BODY_SIZE, bold: true, color: "000000" },
        paragraph: { indent: { firstLine: INDENT }, spacing: { before: 360, after: 240, line: 360 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: BODY_SIZE, bold: true, color: "000000" },
        paragraph: { indent: { firstLine: INDENT }, spacing: { before: 240, after: 120, line: 360 }, keepNext: true, outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: BODY_SIZE, bold: true, italics: true, color: "000000" },
        paragraph: { indent: { firstLine: INDENT }, spacing: { before: 200, after: 80, line: 360 }, keepNext: true, outlineLevel: 3 } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal",
        run: { font: FONT, size: BODY_SIZE },
        paragraph: { spacing: { before: 60, after: 0, line: 300 }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_WIDTH, leader: "dot" }] } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal",
        run: { font: FONT, size: 24 },
        paragraph: { spacing: { before: 0, after: 0, line: 300 }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_WIDTH, leader: "dot" }] } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [0, 1, 2].map((level) => ({
        level, format: LevelFormat.BULLET, text: level === 1 ? "–" : "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 567 * (level + 1), hanging: 283 } } },
      })) },
      { reference: "numbers", levels: [0, 1, 2].map((level) => ({
        level, format: LevelFormat.DECIMAL, text: `%${level + 1}.`, alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 567 * (level + 1), hanging: 397 } } },
      })) },
    ],
  },
  sections,
});

fs.writeFileSync(input.out, await Packer.toBuffer(doc));
console.log("docx-js:", path.basename(input.out));
