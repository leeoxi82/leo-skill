---
name: math-exam-generator
description: >-
  Generate a print-ready math exam PDF from a list of questions (or auto-generate questions from a topic/curriculum). Output is a professional, color-coded exam sheet with LaTeX-rendered math, per-question answer boxes, adaptive layout (3-column for short answers, full-width for multi-step problems), and a separate answer key. Uses local KaTeX for offline rendering via Playwright.

  Use when Leo asks to: 出模拟题/出考试/生成试卷/生成考题/mock exam/practice test, or when given a list of questions and asked to format them into an exam PDF.

  Key features:
  - 3-section color system: Section A blue (easy), B orange (medium), C red (hard)
  - Per-question card with answer/work box; compact 3-column layout for short-answer sub-parts
  - Local KaTeX math rendering (no CDN needed)
  - Separate answer key PDF generated automatically
  - Output to workspace homework/ directory; configurable course name, date, time limit
---

# Math Exam Generator

Generates a professional exam PDF + answer key from structured question data.

## Workflow

1. **Determine questions** — either accept user-provided list or auto-generate based on topic + difficulty distribution
2. **Scaffold HTML** — use `scripts/gen_exam.py` which handles all KaTeX, layout, and color coding
3. **Render PDF** — script uses Playwright + local KaTeX (downloaded to `~/.openclaw/workspace/homework/katex-local/`)
4. **Validate** — visually confirm math symbols render (no fallback text like "\\Delta")
5. **Send PDFs** — exam PDF + answer key PDF

## Running the generator

```bash
python3 skills/math-exam-generator/scripts/gen_exam.py \
  --course "IM 2 Honors" \
  --title "Module 9 Mock Exam" \
  --topics "Discriminant • Quadratic Formula • Complex Numbers" \
  --date "2026-03-22" \
  --time "120 minutes" \
  --out /path/to/output/dir \
  --questions questions.json
```

The `--questions` flag takes a JSON file (see format below). If omitted, the script generates a sample set based on `--topics`.

## Question JSON format

```json
[
  {
    "section": "A",
    "number": 1,
    "points": 3,
    "prompt": "Simplify each power of \\(i\\).",
    "layout": "3col",
    "parts": [
      {"label": "a", "prompt": "\\(i^{15}\\)", "answer": "\\(-i\\)"},
      {"label": "b", "prompt": "\\(i^{42}\\)", "answer": "\\(-1\\)"},
      {"label": "c", "prompt": "\\(i^{101}\\)", "answer": "\\(i\\)"}
    ]
  },
  {
    "section": "A",
    "number": 5,
    "points": 3,
    "prompt": "Solve by completing the square: \\(x^2 + 8x + 7 = 0\\)",
    "layout": "full",
    "answer": "\\(x = -1\\) or \\(x = -7\\)"
  }
]
```

### Layout values
- `"3col"` — 3-column compact row (for short sub-parts like powers of i, basic simplification)
- `"full"` — full-width card with large Work/Answer box (for multi-step problems)
- `"2col"` — 2-column (for pairs of sub-problems)

### Section colors
- `A` → blue (#EFF6FF border, #1D4ED8 header)
- `B` → orange (#FFF7ED border, #C2410C header)
- `C` → red (#FFF1F2 border, #BE123C header)

## KaTeX local setup

Before first use, ensure local KaTeX files exist:

```bash
python3 skills/math-exam-generator/scripts/setup_katex.py
```

Downloads KaTeX CSS, JS, and fonts to `~/.openclaw/workspace/homework/katex-local/` and patches font paths for offline use. Only needed once per machine.

## Auto-generating questions

When no `--questions` file is provided, describe the exam to the script and it will scaffold a JSON. Alternatively, generate the JSON inline:

```python
# In your agent session:
questions = [...]  # build list per format above
import json, tempfile
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(questions, f)
    qfile = f.name
# Then call gen_exam.py with --questions qfile
```

## Output files

```
<out-dir>/
  exam.pdf          ← student copy
  answer_key.pdf    ← teacher/parent copy
  exam.html         ← source (for debugging)
```
