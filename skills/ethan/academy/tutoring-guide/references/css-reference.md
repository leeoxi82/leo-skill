# CSS Component Reference

## Page & Typography
```css
@page { size: letter; margin: 0.5in; }
body  { font-family: Georgia, serif; font-size: 9pt; line-height: 1.45; }
```

## Course Tag (top-left red label)
```html
<div class="course-tag">IM 2 Honors | Module 9.3 — Topic | 2026-03-22</div>
```
```css
.course-tag { font-size: 8pt; font-weight: 700; color: #dc2626; }
```

## Header
```html
<div class="header">
  <h1>🎓 Tutoring Guide</h1>
  <div class="sub">Topic A • Topic B</div>
</div>
```
```css
.header { text-align: center; border-bottom: 3px solid #4f46e5; }
.header h1 { font-size: 16pt; color: #4f46e5; }
.header .sub { font-size: 9pt; color: #666; }
```

## Concept Box (prerequisite knowledge)
```html
<div class="concept-box">
  <h3>📌 Title</h3>
  <p><b>Label:</b> explanation with $LaTeX$</p>
</div>
```
```css
.concept-box { background: #eef2ff; border-left: 4px solid #4f46e5; padding: 6px 10px; }
```

## Problem Box (yellow, states the question)
```html
<div class="problem-box">
  <h2>Q36 — Problem statement</h2>
  <p><em>Detailed description</em></p>
</div>
```
```css
.problem-box { background: #fefce8; border: 2px solid #eab308; padding: 6px 10px; }
```

## Step Cards (numbered, color-coded)
```html
<div class="step step-purple">
  <div class="step-header"><span class="step-num">1</span> Step Title</div>
  <div class="step-body">
    <p>Explanation</p>
    <div class="math-display">$$formula$$</div>
  </div>
</div>
```
Color classes: `step-purple` (#7c3aed), `step-blue` (#2563eb), `step-green` (#16a34a), `step-amber` (#d97706), `step-teal` (#0d9488), `step-rose` (#e11d48).

## Tip & Warning Callouts
```html
<div class="tip">Text (auto-prefixed with 💡)</div>
<div class="warn">Text (auto-prefixed with ⚠️)</div>
```

## Practice Box (green dashed border)
```html
<div class="try-it">
  <h3>🏋️ Practice Title</h3>
  <p>Problem statement</p>
  <div class="work-area" style="min-height: 70px;"></div>
</div>
```

## Summary Box
```html
<div class="summary">
  <h3>📋 Summary Title</h3>
  <ul><li><b>Key point</b></li></ul>
</div>
```
Answer variant: add `style="background:#fef2f2; border-color:#ef4444;"` and use `<h3 style="color:#dc2626;">`.

## Divider & Page Break
```html
<hr class="divider">           <!-- dashed line -->
<div class="page-break"></div>  <!-- force new page -->
```

## Math (KaTeX)
- Inline: `$x^2 + 1$`
- Display: `$$\frac{-b \pm \sqrt{\Delta}}{2a}$$`
- Centered block: wrap in `<div class="math-display">$$...$$</div>`

## PDF Generation
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --print-to-pdf="output.pdf" --print-to-pdf-no-header \
  --no-sandbox --disable-gpu "file:///path/to/file.html"
```
