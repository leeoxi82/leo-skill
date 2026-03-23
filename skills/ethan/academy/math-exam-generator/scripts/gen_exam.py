#!/usr/bin/env python3
"""
gen_exam.py — Generate a professional math exam PDF + answer key.

Usage:
    python3 gen_exam.py \
        --course "IM 2 Honors" \
        --title "Module 9 Mock Exam" \
        --topics "Discriminant • Quadratic Formula • Complex Numbers" \
        --date "2026-03-22" \
        --time "120 minutes" \
        --out /path/to/output \
        --questions questions.json

Without --questions, writes a minimal sample exam (useful for testing layout).
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

# ── KaTeX paths ──────────────────────────────────────────────────────
KATEX_DIR = os.path.expanduser("~/.openclaw/workspace/homework/katex-local")

def katex_paths():
    css = os.path.join(KATEX_DIR, "katex.local.css")
    js  = os.path.join(KATEX_DIR, "katex.min.js")
    ar  = os.path.join(KATEX_DIR, "auto-render.min.js")
    for p in [css, js, ar]:
        if not os.path.exists(p):
            print(f"ERROR: KaTeX file missing: {p}")
            print("Run: python3 setup_katex.py")
            sys.exit(1)
    return f"file://{css}", f"file://{js}", f"file://{ar}"


# ── Section colour system ─────────────────────────────────────────────
SECTION_COLORS = {
    "A": {
        "card_bg":    "#EFF6FF",
        "card_border":"#BFDBFE",
        "header_bg":  "#1D4ED8",
        "label_bg":   "#DBEAFE",
        "label_text": "#1E40AF",
        "ans_border": "#93C5FD",
    },
    "B": {
        "card_bg":    "#FFF7ED",
        "card_border":"#FED7AA",
        "header_bg":  "#C2410C",
        "label_bg":   "#FFEDD5",
        "label_text": "#9A3412",
        "ans_border": "#FDBA74",
    },
    "C": {
        "card_bg":    "#FFF1F2",
        "card_border":"#FECDD3",
        "header_bg":  "#BE123C",
        "label_bg":   "#FFE4E6",
        "label_text": "#9F1239",
        "ans_border": "#FDA4AF",
    },
}

SECTION_NAMES = {
    "A": "Section A — Fundamentals",
    "B": "Section B — Application",
    "C": "Section C — Advanced",
}

SECTION_PTS = {
    "A": 3,
    "B": 5,
    "C": 8,
}


# ── HTML builders ─────────────────────────────────────────────────────

def build_css(css_path, js_path, ar_path):
    return f"""
<link rel="stylesheet" href="{css_path}">
<script src="{js_path}"></script>
<script src="{ar_path}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    color: #1a1a1a;
    background: white;
    padding: 0.5in 0.7in;
    line-height: 1.5;
  }}

  /* ── Cover / header ── */
  .exam-header {{
    text-align: center;
    border: 2px solid #1a1a6e;
    border-radius: 8px;
    padding: 16px 20px 12px;
    margin-bottom: 16px;
    background: #f8f9ff;
  }}
  .exam-title {{ font-size: 18pt; font-weight: bold; color: #1a1a6e; }}
  .exam-topics {{ font-size: 10pt; color: #444; margin-top: 2px; }}
  .exam-meta {{
    display: flex; justify-content: space-between;
    margin-top: 10px; gap: 12px;
  }}
  .meta-field {{
    flex: 1; border-bottom: 1.5px solid #555;
    font-size: 10pt; color: #333;
    padding-bottom: 2px;
  }}
  .meta-field span {{ color: #999; font-size: 9pt; }}

  /* ── Score table ── */
  .score-table {{
    width: 100%; border-collapse: collapse;
    margin-bottom: 10px; font-size: 10pt;
  }}
  .score-table th {{
    background: #1a1a6e; color: white;
    padding: 5px 10px; text-align: left;
  }}
  .score-table td {{
    border: 1px solid #ccc; padding: 5px 10px;
  }}
  .score-table tr:nth-child(even) td {{ background: #f5f7ff; }}

  .instructions {{
    font-size: 9.5pt; color: #333;
    border-left: 3px solid #aaa;
    padding: 6px 12px;
    margin-bottom: 16px;
    background: #fafafa;
  }}

  /* ── Section header ── */
  .section-header {{
    color: white; font-size: 13pt; font-weight: bold;
    padding: 8px 14px; border-radius: 6px;
    margin: 20px 0 10px;
  }}
  .section-sub {{ font-size: 9pt; font-weight: normal; opacity: 0.85; }}

  /* ── Question card ── */
  .q-card {{
    border-radius: 7px;
    border: 1.5px solid;
    margin-bottom: 12px;
    page-break-inside: avoid;
    overflow: hidden;
  }}
  .q-card-header {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 12px;
    font-size: 10.5pt;
    font-weight: bold;
  }}
  .q-num {{ font-size: 11pt; }}
  .q-pts {{
    font-size: 9pt; font-weight: normal;
    background: rgba(255,255,255,0.3);
    border-radius: 12px; padding: 1px 8px;
    color: white;
  }}
  .q-body {{
    padding: 10px 14px 0;
    font-size: 10.5pt;
  }}
  .q-prompt {{ margin-bottom: 8px; }}

  /* ── Answer box ── */
  .ans-box {{
    margin: 8px 0 10px;
    border-radius: 5px;
    border: 1.5px solid;
    padding: 8px 12px;
    font-size: 9pt;
    color: #666;
    min-height: 52px;
  }}
  .ans-label {{
    font-size: 8.5pt; font-weight: bold;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 4px;
    opacity: 0.7;
  }}

  /* ── 3-column layout ── */
  .col-grid {{
    display: grid;
    gap: 8px;
    margin: 4px 0 10px;
  }}
  .col-grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
  .col-grid-2 {{ grid-template-columns: repeat(2, 1fr); }}

  .part-card {{
    border-radius: 5px;
    border: 1px solid;
    padding: 8px 10px;
  }}
  .part-label {{
    font-size: 9pt; font-weight: bold;
    margin-bottom: 4px;
  }}
  .part-prompt {{ font-size: 10.5pt; margin-bottom: 6px; }}
  .part-ans {{
    border-top: 1px solid;
    margin-top: 4px;
    padding-top: 4px;
    min-height: 30px;
    font-size: 8.5pt; color: #777;
  }}

  /* ── Answer key ── */
  .ak-card {{
    border-radius: 7px; border: 1px solid #ddd;
    margin-bottom: 8px; padding: 8px 14px;
    background: #fafafa;
    page-break-inside: avoid;
  }}
  .ak-q {{ font-weight: bold; color: #1a1a6e; font-size: 10pt; }}
  .ak-ans {{ color: #155724; font-size: 10.5pt; margin-top: 2px; }}
  .ak-parts {{ margin-top: 4px; display: flex; gap: 20px; flex-wrap: wrap; }}
  .ak-part {{ font-size: 10pt; }}
  .ak-part b {{ color: #1a1a6e; }}

  /* ── Page break ── */
  .page-break {{ page-break-after: always; }}
  @media print {{
    body {{ padding: 0.4in 0.6in; }}
    .page-break {{ page-break-after: always; }}
  }}
</style>
"""


def q_card_html(q, section, answer_key=False):
    c = SECTION_COLORS[section]
    pts = q.get("points", SECTION_PTS.get(section, 3))
    layout = q.get("layout", "full")
    num = q["number"]
    prompt = q.get("prompt", "")

    header_style = (
        f'style="background:{c["header_bg"]}; color:white;"'
    )
    card_style = (
        f'style="background:{c["card_bg"]}; border-color:{c["card_border"]};"'
    )

    header = f"""
    <div class="q-card-header" {header_style}>
      <span class="q-num">Q{num}.</span>
      <span style="flex:1; padding:0 10px;">{prompt}</span>
      <span class="q-pts">[{pts} pts]</span>
    </div>"""

    body = ""

    if answer_key:
        # Answer key mode — show answers, no blank boxes
        if "parts" in q:
            parts_html = ""
            for p in q["parts"]:
                ans = p.get("answer", "")
                parts_html += f'<span class="ak-part"><b>({p["label"]})</b> {ans}</span>'
            body = f'<div class="q-body"><div class="ak-parts">{parts_html}</div></div>'
        else:
            ans = q.get("answer", "—")
            body = f'<div class="q-body" style="padding-bottom:8px;"><div class="ak-ans">{ans}</div></div>'
        return f'<div class="q-card" {card_style}>{header}{body}</div>'

    # Student copy
    if layout in ("3col", "2col") and "parts" in q:
        grid_cls = "col-grid-3" if layout == "3col" else "col-grid-2"
        parts_html = ""
        for p in q["parts"]:
            part_style = (
                f'style="background:white; border-color:{c["ans_border"]};"'
            )
            parts_html += f"""
            <div class="part-card" {part_style}>
              <div class="part-label" style="color:{c['label_text']};">({p['label']})</div>
              <div class="part-prompt">{p['prompt']}</div>
              <div class="part-ans" style="border-color:{c['ans_border']};">Answer</div>
            </div>"""
        body = f'<div class="q-body"><div class="col-grid {grid_cls}">{parts_html}</div></div>'

    elif layout == "2col" and "parts" in q:
        # same as 3col but 2 columns
        parts_html = ""
        for p in q["parts"]:
            part_style = f'style="background:white; border-color:{c["ans_border"]};"'
            parts_html += f"""
            <div class="part-card" {part_style}>
              <div class="part-label" style="color:{c['label_text']};">({p['label']})</div>
              <div class="part-prompt">{p['prompt']}</div>
              <div class="part-ans" style="border-color:{c['ans_border']};">Answer</div>
            </div>"""
        body = f'<div class="q-body"><div class="col-grid col-grid-2">{parts_html}</div></div>'

    else:
        # Full-width with work box
        ans_style = f'style="background:white; border-color:{c["ans_border"]}; min-height:70px;"'
        if "parts" in q:
            # Full-width sub-parts (for 2-part questions that need space)
            parts_html = ""
            for p in q["parts"]:
                parts_html += f"""
                <div style="margin-bottom:8px;">
                  <div style="font-weight:bold; color:{c['label_text']}; margin-bottom:4px;">({p['label']}) {p['prompt']}</div>
                  <div class="ans-box" {ans_style}>
                    <div class="ans-label">Work / Answer</div>
                  </div>
                </div>"""
            body = f'<div class="q-body">{parts_html}</div>'
        else:
            body = f"""
            <div class="q-body">
              <div class="ans-box" {ans_style}>
                <div class="ans-label">Work / Answer</div>
              </div>
            </div>"""

    return f'<div class="q-card" {card_style}>{header}{body}</div>'


def build_exam_html(meta, questions, css_js, answer_key=False):
    css_path, js_path, ar_path = css_js
    head = build_css(css_path, js_path, ar_path)

    # Score table
    sections = {}
    for q in questions:
        s = q.get("section", "A")
        pts = q.get("points", SECTION_PTS.get(s, 3))
        sections.setdefault(s, 0)
        sections[s] += pts
    total = sum(sections.values())

    score_rows = ""
    for s, pts in sorted(sections.items()):
        score_rows += f"<tr><td>{SECTION_NAMES.get(s, f'Section {s}')}</td><td>{pts}</td><td></td></tr>"
    score_rows += f"<tr><td><b>Total</b></td><td><b>{total}</b></td><td></td></tr>"

    if answer_key:
        page_title = f"{meta['title']} — Answer Key"
        title_suffix = " <span style='color:#c0392b;font-size:14pt;'>(Answer Key)</span>"
    else:
        page_title = meta["title"]
        title_suffix = ""

    # Build body by section
    body_sections = ""
    current_section = None

    for q in questions:
        s = q.get("section", "A")
        c = SECTION_COLORS[s]
        if s != current_section:
            current_section = s
            s_pts = sections.get(s, 0)
            count = sum(1 for qq in questions if qq.get("section", "A") == s)
            per_q = SECTION_PTS.get(s, 3)
            body_sections += f"""
            <div class="section-header" style="background:{c['header_bg']};">
              {SECTION_NAMES.get(s, f'Section {s}')}
              <span class="section-sub">
                &nbsp;({per_q} pts each · {s_pts} pts total)
              </span>
            </div>"""
        body_sections += q_card_html(q, s, answer_key=answer_key)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{page_title}</title>
{head}
</head>
<body>

<div class="exam-header">
  <div class="exam-title">{meta.get('course', '')} — {meta.get('title', 'Exam')}{title_suffix}</div>
  <div class="exam-topics">{meta.get('topics', '')}</div>
  <div class="exam-meta">
    <div class="meta-field">Name: ______________________________ <span>Name</span></div>
    <div class="meta-field">Date: _____________ <span>Date</span></div>
    <div class="meta-field">Period: _____ <span>Period</span></div>
  </div>
</div>

<table class="score-table">
  <tr><th>Section</th><th>Points</th><th>Score</th></tr>
  {score_rows}
</table>

<div class="instructions">
  <strong>Instructions:</strong> Show ALL work for full credit. Simplify all answers completely.
  Express complex number answers in \\(a + bi\\) form. No calculators unless otherwise noted.
  You have <strong>{meta.get('time', '90 minutes')}</strong>.
</div>

{body_sections}

<script>
  document.addEventListener("DOMContentLoaded", function() {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{left: '$$', right: '$$', display: true}},
        {{left: '\\\\(', right: '\\\\)', display: false}}
      ],
      throwOnError: false
    }});
  }});
</script>
</body>
</html>"""
    return html


def render_pdf(html_content, out_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.wait_for_timeout(2500)  # KaTeX render time
        page.pdf(
            path=out_path,
            format="Letter",
            margin={"top": "0.4in", "bottom": "0.4in",
                    "left": "0.4in", "right": "0.4in"},
            print_background=True,
        )
        browser.close()


# ── Sample questions (used when no --questions provided) ──────────────

SAMPLE_QUESTIONS = [
    {
        "section": "A", "number": 1, "points": 3,
        "prompt": "Simplify each power of \\(i\\).",
        "layout": "3col",
        "parts": [
            {"label": "a", "prompt": "\\(i^{15}\\)", "answer": "\\(-i\\)"},
            {"label": "b", "prompt": "\\(i^{42}\\)", "answer": "\\(-1\\)"},
            {"label": "c", "prompt": "\\(i^{101}\\)", "answer": "\\(i\\)"},
        ],
    },
    {
        "section": "A", "number": 2, "points": 3,
        "prompt": "Simplify each expression.",
        "layout": "3col",
        "parts": [
            {"label": "a", "prompt": "\\(\\sqrt{-49}\\)", "answer": "\\(7i\\)"},
            {"label": "b", "prompt": "\\(\\sqrt{-12}\\)", "answer": "\\(2i\\sqrt{3}\\)"},
            {"label": "c", "prompt": "\\(\\sqrt{-75}\\)", "answer": "\\(5i\\sqrt{3}\\)"},
        ],
    },
    {
        "section": "A", "number": 3, "points": 3,
        "prompt": "Find the discriminant and state the number/type of solutions.",
        "layout": "full",
        "parts": [
            {"label": "a", "prompt": "\\(x^2 + 6x + 9 = 0\\)",
             "answer": "\\(\\Delta = 0\\); 1 real (double) root"},
            {"label": "b", "prompt": "\\(2x^2 - 5x + 1 = 0\\)",
             "answer": "\\(\\Delta = 17\\); 2 real solutions"},
        ],
    },
    {
        "section": "A", "number": 4, "points": 3,
        "prompt": "Perform the operation. Write in \\(a+bi\\) form.",
        "layout": "3col",
        "parts": [
            {"label": "a", "prompt": "\\((3+2i)+(7-5i)\\)", "answer": "\\(10-3i\\)"},
            {"label": "b", "prompt": "\\((4-i)-(6+3i)\\)", "answer": "\\(-2-4i\\)"},
            {"label": "c", "prompt": "\\((8+3i)+(-8+3i)\\)", "answer": "\\(6i\\)"},
        ],
    },
    {
        "section": "A", "number": 5, "points": 3,
        "prompt": "Solve by completing the square: \\(x^2 + 8x + 7 = 0\\)",
        "layout": "full",
        "answer": "\\(x = -1\\) or \\(x = -7\\)",
    },
    {
        "section": "B", "number": 6, "points": 5,
        "prompt": "Solve using the quadratic formula: \\(2x^2 + 3x - 4 = 0\\). Simplify the radical completely.",
        "layout": "full",
        "answer": "\\(x = \\dfrac{-3 \\pm \\sqrt{41}}{4}\\)",
    },
    {
        "section": "B", "number": 7, "points": 5,
        "prompt": "Find the discriminant and state the number/type of solutions: \\(-5x^2 + 10x - 5 = 0\\)",
        "layout": "full",
        "answer": "\\(\\Delta = 0\\); 1 real (double) root",
    },
    {
        "section": "B", "number": 8, "points": 5,
        "prompt": "Multiply and write in \\(a+bi\\) form: \\((2+3i)(4-i)\\)",
        "layout": "full",
        "answer": "\\(11 + 10i\\)",
    },
    {
        "section": "C", "number": 9, "points": 8,
        "prompt": "For what value(s) of \\(k\\) does \\(kx^2 - 6x + 3 = 0\\) have exactly one real solution?",
        "layout": "full",
        "answer": "\\(k = 3\\)",
    },
    {
        "section": "C", "number": 10, "points": 8,
        "prompt": "Solve \\(\\dfrac{x^2}{4} - x\\sqrt{7} + 7 = 0\\). How many solutions does it have and why?",
        "layout": "full",
        "answer": "\\(\\Delta = (-\\sqrt{7})^2 - 4\\cdot\\tfrac{1}{4}\\cdot 7 = 7-7=0\\); exactly 1 real solution: \\(x = 2\\sqrt{7}\\)",
    },
]


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate math exam PDF")
    parser.add_argument("--course",    default="IM 2 Honors")
    parser.add_argument("--title",     default="Module 9 Mock Exam")
    parser.add_argument("--topics",    default="Discriminant • Quadratic Formula • Complex Numbers")
    parser.add_argument("--date",      default="")
    parser.add_argument("--time",      default="90 minutes")
    parser.add_argument("--out",       default="/tmp/exam-output")
    parser.add_argument("--questions", default=None,
                        help="Path to JSON file with question list")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    css_js = katex_paths()

    meta = {
        "course": args.course,
        "title":  args.title,
        "topics": args.topics,
        "date":   args.date,
        "time":   args.time,
    }

    if args.questions:
        with open(args.questions) as f:
            questions = json.load(f)
    else:
        print("No --questions provided; using sample questions.")
        questions = SAMPLE_QUESTIONS

    # Student exam
    exam_html = build_exam_html(meta, questions, css_js, answer_key=False)
    exam_html_path = os.path.join(args.out, "exam.html")
    with open(exam_html_path, "w") as f:
        f.write(exam_html)

    exam_pdf = os.path.join(args.out, "exam.pdf")
    print(f"Rendering exam PDF…")
    render_pdf(exam_html, exam_pdf)
    print(f"✅ Exam:       {exam_pdf}")

    # Answer key
    ak_html = build_exam_html(meta, questions, css_js, answer_key=True)
    ak_html_path = os.path.join(args.out, "answer_key.html")
    with open(ak_html_path, "w") as f:
        f.write(ak_html)

    ak_pdf = os.path.join(args.out, "answer_key.pdf")
    print(f"Rendering answer key PDF…")
    render_pdf(ak_html, ak_pdf)
    print(f"✅ Answer key: {ak_pdf}")

    print(f"\n🎉 Done. Output directory: {args.out}")


if __name__ == "__main__":
    main()
