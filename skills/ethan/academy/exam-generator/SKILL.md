---
name: exam-generator
description: >
  Generate professional printable exam/test/quiz PDFs from any subject and topic.
  Use when asked to create a test, exam, quiz, practice problems, mock exam,
  worksheet, or problem set for any academic subject (math, science, history, etc.).
  Triggers: "make a test", "create an exam", "generate a quiz", "practice problems",
  "mock exam", "problem set", "worksheet", "出题", "模拟考试", "练习题".
  Supports multi-section difficulty tiers, KaTeX math rendering, answer keys,
  and professional card-based layout with color-coded sections.
---

# Exam Generator

Generate professional, printable exam PDFs using HTML + KaTeX + Chrome headless PDF.

## Workflow

1. **Gather requirements** — subject, topic, difficulty range, number of questions, time limit, point values, any student weak areas to target.
2. **Build the HTML** — use the card-based template system described below.
3. **Render to PDF** — use Chrome headless `--print-to-pdf`.
4. **Deliver** — send the PDF to the user.

## HTML Template System

Use `assets/exam-template.html` as the reference implementation. Key design patterns:

### Page Setup
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'$',right:'$',display:false}
  ]});"></script>
```
- Page size: `@page { size: letter; margin: 0.55in 0.6in 0.5in 0.6in; }`

### Header Structure
- Exam title (`<h1>`) + subtitle with topic bullets
- Name / Date / Period fields with underlines
- Score summary table with section breakdown
- Instructions box (time limit, calculator policy, answer format)

### Section Color System
Each difficulty tier gets a distinct color for visual separation:
- **Section A** (Easy/Fundamentals): Blue `#3b82f6` — card backgrounds alternate `#f0f5ff` / `#fff`
- **Section B** (Medium/Application): Amber `#f59e0b` — card backgrounds alternate `#fffbeb` / `#fff`
- **Section C** (Hard/Advanced): Red `#ef4444` — card backgrounds alternate `#fef2f2` / `#fff`

Section headers are colored banner bars. Score table rows match section colors.

### Question Card Layout

Every question is a `.q-card` with:
1. **Top bar** (`.q-top`): Bold question number + question text + point value right-aligned
2. **Body** (`.q-body`): Sub-questions if any
3. **Work area** (`.work-area`): White box with border, labeled "Work / Answer"

```html
<div class="q-card">
  <div class="q-top">
    <span class="q-num">5.</span>
    <span class="q-text">Solve by completing the square: $x^2+8x+7=0$</span>
    <span class="q-pts">[3]</span>
  </div>
  <div class="work-area wa-md"></div>
</div>
```

Work area sizes: `wa-sm` (50px), `wa-md` (75px), `wa-lg` (105px), `wa-xl` (140px).

### Sub-question Patterns

**Simple sub-questions** (short answers like simplify $i^{15}$) → use 3-column grid:
```html
<div class="grid-3">
  <div class="grid-cell"><span class="gc-label">(a)</span> <span class="gc-q">$i^{15}$</span></div>
  <div class="grid-cell"><span class="gc-label">(b)</span> <span class="gc-q">$i^{42}$</span></div>
  <div class="grid-cell"><span class="gc-label">(c)</span> <span class="gc-q">$i^{101}$</span></div>
</div>
```

**Complex sub-questions** (multi-step work needed) → stacked with individual work areas:
```html
<div class="q-body"><div class="sub-q">(a) $x^2+6x+9=0$</div></div>
<div class="sub-work wa-sm"></div>
<div class="q-body"><div class="sub-q">(b) $2x^2-5x+1=0$</div></div>
<div class="sub-work wa-md"></div>
```

### Answer Key
- Placed after all exam pages with `page-break-before: always`
- Uses matching section color headers (`.ak-sec-a`, `.ak-sec-b`, `.ak-sec-c`)
- Compact format: one line per answer (`.ak-item`)

### Page Breaks
- Use `<div class="page-break"></div>` between major sections
- Cards have `page-break-inside: avoid` to prevent splitting

## Rendering to PDF

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --print-to-pdf="/path/output.pdf" \
  --print-to-pdf-no-header --no-sandbox --disable-gpu \
  "file:///path/to/exam.html"
```

## Design Guidelines

1. **Work area sizing** — match to expected solution length:
   - Simple computation / single answer → `wa-sm`
   - 2-3 step solution → `wa-md`
   - Multi-step with substitution → `wa-lg`
   - Proof / multi-part derivation → `wa-xl`

2. **Difficulty distribution** — evenly spread across tiers. Target weak areas with "trap" questions that test common mistakes.

3. **Point allocation** — scale with difficulty:
   - Easy: 2-3 pts each
   - Medium: 4-5 pts each
   - Hard: 6-8 pts each

4. **Time budget** — roughly 2-3 min per easy, 4-5 min per medium, 6-8 min per hard question.

5. **Math formatting** — use KaTeX `$...$` for inline, `$$...$$` for display. Use `\dfrac` for fractions, `\sqrt{}` for radicals, `^{}` for exponents.

6. **Non-math subjects** — the card system works for any subject. Replace math notation with regular text. Use the grid layout for matching, multiple choice, or short-answer sets.

## Customization

- To add more sections, define new CSS color classes following the pattern
- To change fonts, update the `font-family` in `body`
- For subjects without math, omit the KaTeX scripts
- Adjust `@page` margins and `size` for different paper sizes (A4: `size: A4`)
