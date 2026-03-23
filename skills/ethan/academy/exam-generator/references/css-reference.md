# Exam Generator — Full CSS Reference

Complete CSS for the exam card system. Copy into `<style>` of each generated exam HTML.

```css
@page { size: letter; margin: 0.55in 0.6in 0.5in 0.6in; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }

/* HEADER */
.header { text-align: center; padding-bottom: 8px; border-bottom: 2.5px solid #1a1a2e; margin-bottom: 8px; }
.header h1 { font-size: 19pt; color: #1a1a2e; margin-bottom: 2px; }
.header .sub { font-size: 10pt; color: #666; }
.info-row { display: flex; justify-content: space-between; margin: 8px 0; font-size: 10pt; }
.uline { border-bottom: 1px solid #444; display: inline-block; min-width: 180px; height: 16px; }
.uline-sm { border-bottom: 1px solid #444; display: inline-block; min-width: 90px; height: 16px; }

/* SCORE TABLE */
.score-table { border-collapse: collapse; margin: 6px auto; font-size: 9.5pt; }
.score-table th, .score-table td { border: 1px solid #aaa; padding: 2px 12px; text-align: center; }
.score-table th { background: #d5dbe8; font-weight: 700; }
.score-table tr:last-child td { background: #eef0f4; font-weight: 700; }

/* INSTRUCTIONS */
.instructions { background: #f5f6f8; border: 1px solid #ccc; border-radius: 3px; padding: 6px 10px; font-size: 9pt; color: #444; margin: 6px 0 10px; }

/* SECTION HEADERS */
.sec-hdr { font-size: 12.5pt; font-weight: 700; color: #fff; padding: 5px 10px; margin: 14px 0 8px; border-radius: 3px; page-break-after: avoid; }
.sec-a .sec-hdr { background: #3b82f6; }
.sec-b .sec-hdr { background: #f59e0b; }
.sec-c .sec-hdr { background: #ef4444; }

/* QUESTION CARDS */
.q-card { border: 1px solid #d0d0d0; border-radius: 4px; margin-bottom: 8px; page-break-inside: avoid; overflow: hidden; }
.sec-a .q-card:nth-child(odd)  { background: #f0f5ff; }
.sec-a .q-card:nth-child(even) { background: #fff; }
.sec-b .q-card:nth-child(odd)  { background: #fffbeb; }
.sec-b .q-card:nth-child(even) { background: #fff; }
.sec-c .q-card:nth-child(odd)  { background: #fef2f2; }
.sec-c .q-card:nth-child(even) { background: #fff; }

.q-top { display: flex; justify-content: space-between; align-items: baseline; padding: 5px 10px 4px; border-bottom: 1px dashed #ccc; }
.q-num { font-weight: 700; font-size: 11pt; color: #1a1a2e; margin-right: 6px; }
.q-text { flex: 1; font-size: 10.5pt; }
.q-pts { font-size: 8.5pt; color: #888; white-space: nowrap; margin-left: 8px; }
.q-body { padding: 4px 10px 2px; }
.sub-q { margin: 2px 0 1px 16px; font-size: 10pt; }

/* WORK AREAS */
.work-area { margin: 4px 10px 6px; border: 1px solid #bbb; border-radius: 3px; background: #fff; position: relative; }
.work-area::before { content: 'Work / Answer'; position: absolute; top: 2px; right: 6px; font-size: 7pt; color: #aaa; font-style: italic; }
.wa-sm { min-height: 50px; }
.wa-md { min-height: 75px; }
.wa-lg { min-height: 105px; }
.wa-xl { min-height: 140px; }

/* SUB-QUESTION WORK AREAS */
.sub-work { margin: 3px 10px 4px 26px; border: 1px solid #bbb; border-radius: 3px; background: #fff; position: relative; }
.sub-work::before { content: 'Work / Answer'; position: absolute; top: 2px; right: 6px; font-size: 7pt; color: #aaa; font-style: italic; }

/* 3-COLUMN GRID (simple sub-questions) */
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; padding: 4px 10px 6px; }
.grid-cell { border: 1px solid #bbb; border-radius: 3px; background: #fff; padding: 4px 8px; min-height: 56px; position: relative; }
.grid-cell .gc-label { font-weight: 600; font-size: 9.5pt; color: #555; }
.grid-cell .gc-q { font-size: 10pt; margin-top: 1px; }
.grid-cell::after { content: 'Answer'; position: absolute; bottom: 3px; right: 6px; font-size: 7pt; color: #aaa; font-style: italic; }

/* PAGE BREAKS */
.page-break { page-break-before: always; }

/* FOOTER */
.exam-footer { text-align: center; font-size: 8pt; color: #999; border-top: 0.5px solid #ccc; padding-top: 4px; margin-top: 10px; }

/* ANSWER KEY */
.ak-page h1 { font-size: 17pt; color: #1a1a2e; text-align: center; border-bottom: 2px solid #1a1a2e; padding-bottom: 4px; margin-bottom: 10px; }
.ak-sec { font-size: 11pt; font-weight: 700; margin: 10px 0 4px; padding: 3px 8px; border-radius: 3px; color: #fff; }
.ak-sec-a { background: #3b82f6; }
.ak-sec-b { background: #f59e0b; }
.ak-sec-c { background: #ef4444; }
.ak-item { font-size: 9pt; margin: 2px 0 2px 8px; line-height: 1.55; }
.ak-item b { color: #1a1a2e; }
```
