// Декларация подлинности и самостоятельности — отдельный документ без номеров страниц
// (Правила оформления письменных работ ЕГУ, прил. 5). Текст — дословно по шаблону.
// node scripts/build-declaration.mjs <ru|en> <out.docx>

import fs from "node:fs";
import { AlignmentType, Document, Packer, Paragraph, TextRun } from "docx";

const [, , lang, out] = process.argv;

const TEXT = {
  ru: {
    heading: ["Декларация подлинности и самостоятельности выполнения", "бакалаврского проекта"],
    author: "Кирилл Калашников",
    titles: ["Система создания игровых 3D-карт по видеозаписи", "A System for Creating 3D Game Maps from Video"],
    body: "Подтверждаю, что бакалаврский проект является результатом моей собственной, оригинальной деятельности. "
      + "Проект не содержит нарушений, перечисленных в Положении “О самостоятельности выполнения письменных и творческих "
      + "работ в Европейском гуманитарном университете”. Удостоверяю, что я ознакомлен с данным Положением, в том числе "
      + "с последствиями, которые может повлечь обнаружение нарушений мною академической этики. Кроме того, ни весь "
      + "проект, ни какая-либо его часть не были ранее представлены в какое-либо другое высшее учебное заведение в "
      + "качестве письменной / творческой отчетной или итоговой работы.",
    sign: "(подпись автора)",
  },
  en: {
    heading: ["Declaration of authenticity of the bachelor project"],
    author: "Kirill Kalashnikov",
    titles: ["A System for Creating 3D Game Maps from Video"],
    body: "I confirm that this bachelor project is the result of my own original work. The project does not contain any "
      + "violations listed in the “Regulation on the Independence of Written and Creative Work at the European Humanities "
      + "University”. I certify that I have read this Regulation, including the consequences that may result from the "
      + "discovery of violations of academic ethics by me. Also, neither the entire project nor any part of it has been "
      + "submitted to any other higher education institution as a thesis, academic paper, or final project.",
    sign: "(author’s signature)",
  },
}[lang];

const p = (text, opts = {}) => new Paragraph({
  alignment: opts.align || AlignmentType.CENTER,
  spacing: { before: opts.before || 0, after: opts.after ?? 120, line: 360 },
  indent: opts.indent ? { firstLine: 709 } : undefined,
  children: [new TextRun({ text, bold: opts.bold })],
});

const children = [
  ...TEXT.heading.map((h, i) => p(h, { bold: true, before: i ? 0 : 1200, after: i === TEXT.heading.length - 1 ? 600 : 0 })),
  p(TEXT.author, { after: 360 }),
  ...TEXT.titles.map((h, i) => p(h, { after: i === TEXT.titles.length - 1 ? 600 : 120 })),
  p(TEXT.body, { align: AlignmentType.JUSTIFIED, indent: true, after: 1200 }),
  p("____________________", { align: AlignmentType.RIGHT, after: 0 }),
  p(TEXT.sign, { align: AlignmentType.RIGHT }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: "Times New Roman", size: 24 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 567, bottom: 1134, left: 1417 } } },
    children,
  }],
});
fs.writeFileSync(out, await Packer.toBuffer(doc));
