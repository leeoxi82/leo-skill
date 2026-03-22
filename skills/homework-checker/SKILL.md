---
name: homework-checker
description: >-
  Check student homework from photos/screenshots and produce a standardized review for Ethan. Use when Leo asks to 查作业/检查作业/批改作业/讲错题/分析原因/给学习建议. Required deliverables per run: (1) detailed wrong-problem explainer PDF, (2) concept tutoring PDF, (3) targeted home extension practice PDF (count follows error-type rules: 5 questions per wrong item, capped at 10 per error type; each 5-question set = 2 guided + 3 unguided). All three PDFs must be English and LaTeX-rendered, and results must be published to Ethan’sPG Notion homework database with attachments and structured fields.
---

# Homework Checker

## Standard workflow (do this in order)

1) **Collect inputs**
- Homework photos/screenshots (all pages)
- Course + module/lesson/topic (infer from worksheet header when possible)
- Homework date (default to Leo’s indicated date)
- If needed, school assignment link (for `扩展练习条目链接`)

2) **Quick verdict first (to Leo)**
- Overall: `All correct` / `Minor mistakes` / `Needs redo`
- Wrong count (estimate)
- Top 1–2 fixes

3) **Core diagnosis (English)**
For each incorrect/questionable item, capture:
- What Ethan wrote
- Correct answer
- Why it is wrong
- Step-by-step fix
- Mistake type: `Careless` vs `Concept gap`

4) **Mandatory 3 PDF outputs (English + LaTeX-rendered)**
Every homework check must output these PDFs.

For **every PDF page** in this run, enforce the same visual header/footer:
- Top area must show **Module number + homework date** in **red bold** text
- Bottom-right must show page number (`Page X of Y`)

### PDF 1 — Detailed Wrong-Problem Explainer
- Focus only on wrong/questionable items
- Step-by-step correction for each item
- Match school-style solution format
- Keep this per-problem structure (stable default):
  1) What Ethan wrote
  2) Correct answer
  3) Why it is wrong
  4) Step-by-step fix
  5) Mistake type (`Careless` / `Concept gap`)

### PDF 2 — Tutoring Explanation (Concept + Method)
- Explain *why* errors happened (formula/method/concept gaps)
- Use plain, student-friendly language
- Keep logic clear and add light fun/engagement when natural

### PDF 3 — Targeted Home Extension Practice
- Use **adaptive count by error type** (do not force fixed 30 unless Leo explicitly asks).
- Generation rule:
  - For each wrong item: assign a 5-question practice set.
  - Each 5-question set must be: **2 guided** (step-by-step prompts) + **3 unguided** (independent).
  - If the **same error type** appears 2+ times, cap that type at **2 sets** total (i.e., **10 questions** = 4 guided + 6 unguided for that type).
- Error-type grouping default (recommended): same **core concept + formula/equation structure + solving pattern** counts as one type.
  - Example: two problems both require the same linear-equation transformation pattern and formula skeleton → same type.
- **Novelty rule (strict):** extension questions must be materially different from the original wrong items (change context, numbers, phrasing, and structure); no near-duplicates or template clones.
- Must target this homework’s actual weak points.
- Recommended: generate a separate answer-key PDF for parent/teacher use.

5) **LaTeX render validation (mandatory before sending)**
- Run strict render validation for every generated PDF batch.
- Rule: deliver only when `katexRenderIssueCount = 0` (or equivalent strict check passes).
- If any issue exists, fix escaping/LaTeX source and regenerate before sending.
- Visual sanity rule: no red KaTeX error text in final PDF.

6) **Publish to Notion (required)**
- Ensure homework DB schema exists/up-to-date
- Create/update page
- Attach source photos + generated PDFs
- Fill properties including:
  - `错题讲解` (PDF field)
  - `补习讲解及扩展练习` (PDF field; can store multiple PDFs)
  - `扩展练习条目链接` (URL)
  - `作业类型` (`学校作业` or `家庭扩展练习`)
  - Existing grading/status fields (`得分`/`评分`/`错题数`/etc.)
- Write standardized English review in page body

7) **Send back to Leo**
- Send the 3 PDFs (and answer key if generated)
- Include short status summary + Notion link

## Notion tooling (scripts)

### 1) Ensure database + schema exists
Use:
- `skills/homework-checker/scripts/notion_homework_setup.py`

Example:
```bash
python3 skills/homework-checker/scripts/notion_homework_setup.py \
  --path "Haber/Ethan'sPG/College Prep/Homework/Math" \
  --db-title "🧮 Math Homework" \
  --out notion/homework_math.json
```

### 2) Create/update record + attach photos/PDFs + write review
Use:
- `skills/homework-checker/scripts/notion_homework_publish_review.py`

Create/update example:
```bash
python3 skills/homework-checker/scripts/notion_homework_publish_review.py \
  --ids notion/homework_math.json \
  --name "YYYY-MM-DD — IM 2 Honors Module X" \
  --hw-date YYYY-MM-DD \
  --course "IM 2 Honors" --module "Module X" --topic "..." \
  --status Checked --result "Needs redo" --wrong 9 --score 65 --grade D \
  --short-note "Top error patterns..." \
  --wrong-pdf /path/to/wrong_explainer.pdf \
  --tutoring-pdf /path/to/tutoring.pdf \
  --tutoring-pdf /path/to/targeted_practice.pdf \
  --practice-link "https://..." \
  --homework-type "学校作业" \
  /path/to/photo1.jpg /path/to/photo2.jpg \
  < review.md
```

## Scoring fields (Notion)

- `得分` (0–100)
- `评分` (letter grade with +/-)

Default +/- scale:
- A+ 97–100
- A 93–96
- A- 90–92
- B+ 87–89
- B 83–86
- B- 80–82
- C+ 77–79
- C 73–76
- C- 70–72
- D+ 67–69
- D 63–66
- D- 60–62
- F <60

## Output rules

- Student-facing teaching content: **English only**
- PDF equations: **LaTeX-rendered** (not plain-text formulas)
- Render gate: must pass strict KaTeX validation (`katexRenderIssueCount=0`) before delivery
- Page size: **Letter (8.5×11)** unless Leo requests otherwise
- Each PDF must include: red bold `Module <number> | Date <YYYY-MM-DD>` header text + bottom-right page numbering (`Page X of Y`)
- Notion page body: plain markdown-ish text (do not rely on LaTeX rendering in body)

## KaTeX PDF rendering checklist
- Inline the entire `katex.min.css` into the HTML passed to Playwright, and rewrite every `url(fonts/...)` reference to an absolute `file://` path so the KaTeX fonts load while Chromium renders PDFs offline.
- Call `katex.renderToString(…, { output: 'html' })` to suppress MathML output; this prevents duplicate plain-text math from leaking into the PDF layer.
- Run every inline explanation (Focus lines, Step prompts, bullet notes) through `k()` as well—no raw `(x-h)^2` or `5/2` text is allowed.
- Keep the KaTeX render gate enforced (`katexRenderIssueCount` must stay 0) before sending any PDF.
- Visual spot-check: convert at least one fresh PDF page to PNG (e.g., `pdftoppm ... -png`) to confirm superscripts/fractions actually render. Drop the screenshot into Notion when debugging so Leo can see the fix.
