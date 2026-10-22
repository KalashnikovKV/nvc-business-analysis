// Собрать презентацию для защиты в PowerPoint из того же описания слайдов, что и deck.html.
// Вызывается из scripts/build-ba.py: node scripts/build-pptx.mjs <slides.json> <out.pptx>

import fs from "node:fs";
import pptxgen from "pptxgenjs";

const [, , input, output] = process.argv;
const data = JSON.parse(fs.readFileSync(input, "utf8"));

// Холст 16:9 — 10 × 5,625 дюйма.
const W = 10;
const X = 0.5;
const CW = W - 2 * X;
const TOP = 1.9; // начало содержимого под заголовком
const BOTTOM = 5.15; // граница над подписью раздела (она стоит на 5,2)

const COLOR = {
  ink: "111827", muted: "6B7280", line: "E5E7EB", white: "FFFFFF",
  teal: "0F766E", tealTint: "ECFDF5", tealSoft: "F3F8F7", tealLine: "A7F3D0",
  navy: "0F172A", slate: "94A3B8", gray: "F3F4F6",
  red: "B42318", redTint: "FDE8E7", amber: "B54708", amberTint: "FFF4E5",
};
const FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Система создания игровых 3D-карт по видеозаписи";
pres.author = "Кирилл Калашников";
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

pres.defineSlideMaster({
  title: "TITLE",
  background: { color: COLOR.navy },
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: COLOR.white },
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 10, color: COLOR.muted, align: "right" },
  objects: [{
    placeholder: {
      options: { name: "title", type: "title", x: X, y: 0.72, w: CW, h: 1.0, fontFace: FONT, fontSize: 26, bold: true, color: COLOR.ink, align: "left", valign: "top", margin: 0 },
      text: "",
    },
  }],
});

// --- Помощники ---------------------------------------------------------------

const box = (slide, x, y, w, h, fill, opts = {}) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08, fill: { color: fill },
    line: opts.line ? { color: opts.line, width: opts.lineWidth || 1 } : { type: "none" },
    objectName: opts.name,
  });

const text = (slide, value, x, y, w, h, o = {}) =>
  slide.addText(value, {
    x, y, w, h, isTextBox: true, margin: o.margin ?? 0.08, fontFace: FONT,
    fontSize: o.size || 14, color: o.color || COLOR.ink, bold: o.bold, italic: o.italic,
    align: o.align || "left", valign: o.valign || "top", fit: "none", objectName: o.name,
    paraSpaceAfter: o.paraSpaceAfter, hyperlink: o.link ? { url: o.link } : undefined,
  });

// Подпись сверху и текст снизу внутри карточки.
const labelled = (slide, label, value, x, y, w, h, o = {}) =>
  text(slide, [
    { text: label, options: { fontSize: 10, color: o.labelColor || COLOR.muted, breakLine: true } },
    { text: value, options: { fontSize: o.size || 15, bold: o.bold ?? true, color: o.color || COLOR.ink } },
  ], x + 0.08, y + 0.06, w - 0.16, h - 0.12, { name: o.name, paraSpaceAfter: 3 });

function chain(slide, active) {
  if (active === undefined || active === null) return;
  let x = X;
  data.chain.forEach((step, i) => {
    const w = 0.22 + step.length * 0.085;
    const on = i === active;
    box(slide, x, 0.3, w, 0.28, on ? COLOR.teal : COLOR.white, { line: on ? COLOR.teal : COLOR.line, name: `chain-${i}` });
    text(slide, step, x, 0.3, w, 0.28, { size: 10, color: on ? COLOR.white : COLOR.muted, align: "center", valign: "middle", margin: 0 });
    x += w;
    if (i < data.chain.length - 1) {
      text(slide, "→", x, 0.3, 0.25, 0.28, { size: 10, color: COLOR.muted, align: "center", valign: "middle", margin: 0 });
      x += 0.25;
    }
  });
}

// --- Блоки: каждый рисует себя с позиции y и возвращает занятую высоту --------

const GAP = 0.25;
const blocks = {
  number(slide, b, y) {
    const h = BOTTOM - y;
    text(slide, b.value, X, y + 0.2, 4.4, 1.2, { size: 66, bold: true, color: COLOR.teal, margin: 0, name: "number" });
    text(slide, b.caption, X, y + 1.45, 4.2, 0.9, { size: 15, color: "374151", margin: 0 });
    text(slide, b.text, 5.2, y + 0.6, 4.3, 1.6, { size: 18, color: "374151", valign: "middle", margin: 0 });
    return h;
  },
  tasks(slide, b, y) {
    const n = b.items.length, gap = 0.15, w = (CW - gap * (n - 1)) / n, h = 1.15;
    b.items.forEach(([label, value], i) => {
      const x = X + i * (w + gap);
      box(slide, x, y, w, h, COLOR.tealSoft, { line: "CFE9E4", name: `task-${i}` });
      labelled(slide, label, value, x, y, w, h, { labelColor: COLOR.teal, size: 14 });
    });
    return h;
  },
  cards(slide, b, y) {
    const gap = 0.3, w = (CW - gap) / 2, h = 1.0;
    b.items.forEach(([label, value], i) => {
      const x = X + i * (w + gap);
      box(slide, x, y, w, h, COLOR.white, { line: COLOR.line, name: `card-${i}` });
      labelled(slide, label, value, x, y, w, h, { size: 16 });
    });
    return h;
  },
  flow(slide, b, y) {
    const n = b.items.length, gap = 0.12, w = (CW - gap * (n - 1)) / n, h = b.small ? 0.8 : 0.95;
    const fills = { lost: [COLOR.redTint, COLOR.red], late: [COLOR.amberTint, COLOR.amber], "": [b.small ? COLOR.tealSoft : COLOR.gray, COLOR.ink] };
    b.items.forEach(([value, small, kind], i) => {
      const x = X + i * (w + gap);
      const [fill, color] = fills[kind];
      box(slide, x, y, w, h, fill, { name: `step-${i}` });
      const runs = [{ text: value, options: { fontSize: 14, bold: true, color, breakLine: Boolean(small) } }];
      if (small) runs.push({ text: small, options: { fontSize: 10, color } });
      text(slide, runs, x, y, w, h, { align: "center", valign: "middle" });
    });
    return h;
  },
  matrix(slide, b, y) {
    const gap = 0.15, w = (CW - gap) / 2, h = 0.75;
    b.items.forEach(([label, value, hi], i) => {
      const x = X + (i % 2) * (w + gap), yy = y + Math.floor(i / 2) * (h + gap);
      box(slide, x, yy, w, h, hi ? COLOR.tealTint : COLOR.white, { line: hi ? COLOR.tealLine : COLOR.line, name: `stakeholder-${i}` });
      labelled(slide, label, value, x, yy, w, h, { size: 15 });
    });
    return 2 * h + gap;
  },
  check(slide, b, y) {
    const marks = { yes: ["✓", COLOR.teal, 20], no: ["✕", COLOR.red, 18], part: ["частично", COLOR.amber, 13] };
    const last = b.columns.length;
    const head = [{ text: "", options: {} }, ...b.columns.map((c, i) => ({
      text: c, options: { bold: true, fontSize: 11, color: i + 1 === last ? COLOR.teal : COLOR.muted, align: "center", fill: { color: i + 1 === last ? COLOR.tealTint : COLOR.white } },
    }))];
    const rows = b.rows.map((r) => [
      { text: r[0], options: { bold: true, fontSize: 15, color: COLOR.ink } },
      ...r.slice(1).map((v, i) => {
        const [mark, color, size] = marks[v];
        return { text: mark, options: { color, fontSize: size, bold: v !== "part", align: "center", fill: { color: i + 1 === last ? COLOR.tealTint : COLOR.white } } };
      }),
    ]);
    const rowH = [0.6, ...rows.map(() => 0.42)];
    slide.addTable([head, ...rows], {
      x: X, y, w: CW, colW: [2.7, 2.1, 1.5, 1.2, 1.5], rowH, fontFace: FONT, valign: "middle",
      border: { type: "solid", pt: 0.75, color: COLOR.line }, margin: 0.06, objectName: "analogs",
    });
    // Небольшой запас под таблицей: строки с переносом чуть выше заданной высоты.
    return rowH.reduce((a, b) => a + b, 0) + 0.25;
  },
  text(slide, b, y) {
    text(slide, b.text, X, y, CW, 0.45, { size: 17, color: "374151", margin: 0 });
    return 0.45;
  },
  note(slide, b, y) {
    text(slide, b.text, X, y, CW, 0.4, { size: 12, color: COLOR.muted, margin: 0 });
    return 0.4;
  },
  tiles(slide, b, y) {
    const n = b.items.length, gap = 0.15, w = (CW - gap * (n - 1)) / n, h = 1.1;
    b.items.forEach(([label, value], i) => {
      const x = X + i * (w + gap);
      box(slide, x, y, w, h, COLOR.navy, { name: `tile-${i}` });
      labelled(slide, label, value, x, y, w, h, { labelColor: COLOR.slate, color: COLOR.white, size: 17 });
    });
    return h;
  },
  scope(slide, b, y) {
    const gap = 0.3, w = (CW - gap) / 2, h = 1.15;
    box(slide, X, y, w, h, COLOR.tealTint, { name: "scope-in" });
    labelled(slide, "Входит", b.in, X, y, w, h, { size: 15 });
    box(slide, X + w + gap, y, w, h, COLOR.gray, { name: "scope-out" });
    labelled(slide, "Не входит", b.out, X + w + gap, y, w, h, { size: 15, color: "4B5563" });
    return h;
  },
  trace(slide, b, y) {
    const n = b.items.length, arrow = 0.3, w = (CW - arrow * (n - 1)) / n, h = 0.75;
    b.items.forEach(([value, hot], i) => {
      const x = X + i * (w + arrow);
      box(slide, x, y, w, h, hot ? COLOR.teal : COLOR.gray, { name: `trace-${i}` });
      text(slide, value, x, y, w, h, { size: 14, bold: true, color: hot ? COLOR.white : COLOR.ink, align: "center", valign: "middle" });
      if (i < n - 1) text(slide, "→", x + w, y, arrow, h, { size: 16, color: COLOR.muted, align: "center", valign: "middle", margin: 0 });
    });
    return h;
  },
  chips(slide, b, y) {
    const per = 3, gap = 0.15, w = (CW - gap * (per - 1)) / per, h = 0.45;
    b.items.forEach(([value, hot], i) => {
      const x = X + (i % per) * (w + gap), yy = y + Math.floor(i / per) * (h + 0.1);
      box(slide, x, yy, w, h, hot ? COLOR.teal : COLOR.gray, { name: `epic-${i}` });
      text(slide, value, x, yy, w, h, { size: 14, bold: true, color: hot ? COLOR.white : COLOR.ink, align: "center", valign: "middle" });
    });
    const rowsN = Math.ceil(b.items.length / per);
    return rowsN * h + (rowsN - 1) * 0.1;
  },
  legal(slide, b, y) {
    const n = b.items.length, gap = 0.15, w = (CW - gap * (n - 1)) / n, h = 1.4;
    b.items.forEach(([label, value], i) => {
      const x = X + i * (w + gap);
      box(slide, x, y, w, h, COLOR.white, { line: COLOR.line, name: `legal-${i}` });
      labelled(slide, label, value, x, y, w, h, { size: 14, bold: false });
    });
    return h;
  },
  concept(slide, b, y) {
    const left = 5.9, arrow = 0.55, nw = (left - 2 * arrow) / 3, nh = 1.45;
    b.nodes.forEach(([role, name, desc, main], i) => {
      const x = X + i * (nw + arrow);
      box(slide, x, y + 0.1, nw, nh, main ? COLOR.tealTint : COLOR.white, { line: main ? COLOR.teal : COLOR.line, lineWidth: 1.5, name: `node-${i}` });
      text(slide, [
        { text: role, options: { fontSize: 10, color: COLOR.muted, breakLine: true } },
        { text: name, options: { fontSize: 20, bold: true, color: COLOR.ink, breakLine: true } },
        { text: desc, options: { fontSize: 11, color: "4B5563" } },
      ], x, y + 0.1, nw, nh, { align: "center", valign: "middle" });
      if (i < 2) text(slide, b.arrows[i], x + nw, y + 0.1, arrow, nh, { size: 10, color: COLOR.muted, align: "center", valign: "middle", margin: 0 });
    });
    const ew = (left - 0.2) / 2;
    b.external.forEach((ext, i) => {
      const x = X + i * (ew + 0.2);
      box(slide, x, y + 1.75, ew, 0.5, COLOR.gray, { name: `external-${i}` });
      text(slide, ext, x, y + 1.75, ew, 0.5, { size: 13, bold: true, align: "center", valign: "middle" });
    });
    const rx = X + left + 0.3, rw = CW - left - 0.3, rh = 0.95;
    b.risks.forEach(([title, desc], i) => {
      const yy = y + i * (rh + 0.12);
      box(slide, rx, yy, rw, rh, COLOR.redTint, { name: `risk-${i}` });
      text(slide, [
        { text: title, options: { fontSize: 14, bold: true, color: COLOR.red, breakLine: true } },
        { text: desc, options: { fontSize: 12, color: COLOR.ink } },
      ], rx + 0.05, yy + 0.04, rw - 0.1, rh - 0.08, {});
    });
    return 3 * rh + 2 * 0.12;
  },
  backup(slide, b, y) {
    const gap = 0.25, w = (CW - gap) / 2, h = 1.0;
    b.items.forEach(([label, value, href], i) => {
      const x = X + (i % 2) * (w + gap), yy = y + Math.floor(i / 2) * (h + gap);
      box(slide, x, yy, w, h, COLOR.white, { line: COLOR.line, name: `backup-${i}` });
      text(slide, [
        { text: label, options: { fontSize: 11, color: COLOR.teal, breakLine: true } },
        { text: value, options: { fontSize: 18, bold: true, color: COLOR.ink, hyperlink: { url: data.siteUrl + href } } },
      ], x + 0.1, yy + 0.08, w - 0.2, h - 0.16, {});
    });
    return 2 * h + gap;
  },
  qa(slide, b, y) {
    const rowH = 0.85;
    b.items.forEach(([q, a], i) => {
      const yy = y + i * rowH;
      text(slide, q, X, yy, 3.3, rowH - 0.05, { size: 14, bold: true });
      text(slide, a, X + 3.4, yy, CW - 3.4, rowH - 0.05, { size: 14, color: "374151" });
    });
    return b.items.length * rowH;
  },
};

// --- Слайды ------------------------------------------------------------------

function titleSlide(s) {
  const slide = pres.addSlide({ masterName: "TITLE", sectionTitle: "Доклад" });
  const b = s.blocks[0];
  text(slide, b.kicker, X, 1.2, CW, 0.35, { size: 13, color: "5EEAD4", margin: 0 });
  text(slide, b.title, X, 1.6, 8.2, 1.5, { size: 38, bold: true, color: COLOR.white, margin: 0, name: "title" });
  text(slide, b.sub, X, 3.1, CW, 0.4, { size: 16, color: COLOR.slate, margin: 0 });
  text(slide, b.people.join("\n"), X, 3.9, CW, 0.8, { size: 14, color: "E2E8F0", margin: 0, paraSpaceAfter: 4 });
}

function contentSlide(s, section, title = s.title, blocksList = s.blocks) {
  const slide = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  chain(slide, s.chain);
  slide.addText(title, { placeholder: "title" });
  let y = s.chain === undefined || s.chain === null ? 1.45 : TOP;
  for (const b of blocksList) {
    const draw = blocks[b.type];
    if (!draw) throw new Error(`Нет отрисовки для блока ${b.type}`);
    y += draw(slide, b, y) + GAP;
  }
  if (y - GAP > BOTTOM + 0.05) console.warn(`Слайд «${title}» выходит за границу: ${y.toFixed(2)}`);
  text(slide, s.ref, X, 5.2, 8.2, 0.3, { size: 10, color: COLOR.muted, margin: 0, name: "section-ref" });
  return slide;
}

pres.addSection({ title: "Доклад" });
let backupStarted = false;
for (const s of data.slides) {
  if (s.kind === "title") { titleSlide(s); continue; }
  if (s.kind === "backup" && !backupStarted) { pres.addSection({ title: "После доклада" }); backupStarted = true; }
  const section = s.kind === "backup" ? "После доклада" : "Доклад";
  const qa = s.blocks.find((b) => b.type === "qa");
  if (qa) {
    // Семь ответов не помещаются крупным шрифтом на один слайд — делим на два.
    const half = Math.ceil(qa.items.length / 2);
    contentSlide(s, section, `${s.title} (1 из 2)`, [{ type: "qa", items: qa.items.slice(0, half) }]);
    contentSlide(s, section, `${s.title} (2 из 2)`, [{ type: "qa", items: qa.items.slice(half) }]);
    continue;
  }
  contentSlide(s, section);
}

await pres.writeFile({ fileName: output });
console.log("pptx:", output);
