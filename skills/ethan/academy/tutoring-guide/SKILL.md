---
name: tutoring-guide
description: >
  Generate step-by-step tutoring guide PDFs for math problems Ethan can't solve.
  Use when asked to create a "tutoring guide", "解题指南", or "touring guide" for
  specific homework/exam questions. Input: problem numbers + source (exam PDF or
  textbook photos). Output: print-ready PDF with KaTeX math, color-coded steps,
  practice problems, and answer key. Targets IM 2 Honors level but adaptable to
  any math course.
---

# Tutoring Guide Skill

Generate print-ready tutoring guide PDFs that walk through problems step-by-step.

## Workflow

1. **Identify the problems** — Extract the exact problem text from the referenced exam/homework (PDF or photos).
2. **Analyze each problem** — Determine the concept, method, and common mistakes.
3. **Build the HTML** — Use the template structure below. One HTML file → convert to PDF.
4. **Generate PDF** — Chrome headless with `--print-to-pdf-no-header`.
5. **Send** — Deliver PDF via message tool.

## HTML Structure

Use `assets/template.html` as a working reference. Key sections in order:

```
course-tag          → Red bold: Course | Module — Topic | Date
header              → Title + subtitle
concept-box         → Prerequisites the student already knows
─── per problem: ───
  problem-box       → Yellow box stating the problem
  tip/warn          → Context or approach hint
  step cards        → Numbered, color-coded solution steps
  tip/warn          → Common mistakes or key insights
  try-it            → Practice: rewrite proof / solve similar
─── end ────────────
summary             → Bullet-point recap of key takeaways
try-it (×2-3)       → Practice problems with work areas
summary (red)       → Practice answers
```

## Key Rules

- **Math rendering**: KaTeX via CDN. Inline `$...$`, display `$$...$$`.
- **Font size**: 9pt body, compact margins — optimized for printing.
- **Course tag**: Always include at top-left in red bold: `Course | Module — Topic | Date`.
- **No file paths in output**: No footer with file:// URLs. Use `@page margin` (not 0) so Chrome doesn't clip content, and always pass `--print-to-pdf-no-header`.
- **Step colors**: Rotate through purple → blue → green → amber → teal → rose for visual variety.
- **Multiple methods**: When a problem has multiple solution approaches, show all (label which is fastest/most intuitive).
- **Practice problems**: 2-3 similar problems with work areas + answers at the end.
- **Page breaks**: Use `<div class="page-break"></div>` between major sections.

## Component Reference

For CSS classes, HTML snippets, and color codes → read `references/css-reference.md`.

## PDF Generation

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --print-to-pdf="/path/output.pdf" --print-to-pdf-no-header \
  --no-sandbox --disable-gpu "file:///path/to/guide.html"
```
