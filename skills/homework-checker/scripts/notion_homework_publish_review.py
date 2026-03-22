#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Create or update a homework record in a Notion homework database, attach photos, and write the review (English).

Workflow:
- Read ids json created by notion_homework_setup.py (contains data_source_id)
- Upload local files with Notion File Upload API (single_part)
- Create a page under the data_source (or update an existing page)
- (Optionally) replace page body with a standardized review written in markdown-ish text (from stdin)

Usage (create new record):
  python3 skills/homework-checker/scripts/notion_homework_publish_review.py \
    --ids notion/homework_math.json \
    --name "2026-02-02 — IM2 Honors Module 7.3" \
    --hw-date 2026-02-02 \
    --course "IM 2 Honors" \
    --module "7.3" \
    --topic "Zero Product Property" \
    --status Checked \
    --result "Minor mistakes" \
    --wrong 1 \
    --short-note "Fix #8: x = -24 (not 24)." \
    --wrong-pdf /path/to/wrong_explainer.pdf \
    --tutoring-pdf /path/to/tutoring.pdf \
    --tutoring-pdf /path/to/targeted_practice.pdf \
    --practice-link "https://school.example/homework/123" \
    --homework-type "学校作业" \
    /path/to/page1.jpg /path/to/page2.jpg \
    < review.md

Usage (update existing record body):
  python3 skills/homework-checker/scripts/notion_homework_publish_review.py \
    --page-url "https://www.notion.so/..." \
    --replace-body \
    < review.md

Requires: ~/.config/notion/api_key
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

NOTION_VERSION = "2025-09-03"
API = "https://api.notion.com/v1"


def notion_key() -> str:
    p = os.path.expanduser("~/.config/notion/api_key")
    with open(p, "r", encoding="utf-8") as f:
        return f.read().strip()


def req(method: str, path: str, token: str, body: dict | None = None, headers_extra: dict | None = None, raw: bytes | None = None) -> dict:
    url = path if path.startswith("http") else API + path
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "User-Agent": "clawdbot/notion",
    }
    if headers_extra:
        headers.update(headers_extra)

    data = None
    if raw is not None:
        data = raw
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            if resp.status == 204:
                return {}
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raw_err = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} {url}: {raw_err}")


def _multipart_form(field_name: str, filename: str, content_type: str, content: bytes, boundary: str) -> bytes:
    b = boundary.encode("utf-8")
    lines: list[bytes] = []
    lines.append(b"--" + b)
    lines.append(
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode("utf-8")
    )
    lines.append(f"Content-Type: {content_type}".encode("utf-8"))
    lines.append(b"")
    lines.append(content)
    lines.append(b"--" + b + b"--")
    lines.append(b"")
    return b"\r\n".join(lines)


def upload_file_to_notion(token: str, file_path: str) -> str:
    fn = os.path.basename(file_path)
    ct, _ = mimetypes.guess_type(fn)
    ct = ct or "application/octet-stream"

    fu = req("POST", "/file_uploads", token, {"filename": fn})
    upload_url = fu.get("upload_url")
    upload_id = fu.get("id")
    if not upload_url or not upload_id:
        raise RuntimeError("Failed to create file upload")

    with open(file_path, "rb") as f:
        content = f.read()

    boundary = "----clawdbot-" + secrets.token_hex(16)
    form = _multipart_form("file", fn, ct, content, boundary)

    req(
        "POST",
        upload_url,
        token,
        headers_extra={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(form)),
        },
        raw=form,
    )

    # The file upload id is what we attach to Notion objects.
    return upload_id


def rt(text: str) -> list[dict]:
    if not text:
        return []
    return [{"type": "text", "text": {"content": text}}]


def score_to_grade(score: float) -> str:
    """Default +/- grading scale (common US HS scale).

    A+ 97–100
    A  93–96
    A- 90–92
    B+ 87–89
    B  83–86
    B- 80–82
    C+ 77–79
    C  73–76
    C- 70–72
    D+ 67–69
    D  63–66
    D- 60–62
    F  <60
    """

    s = float(score)
    if s >= 97:
        return "A+"
    if s >= 93:
        return "A"
    if s >= 90:
        return "A-"
    if s >= 87:
        return "B+"
    if s >= 83:
        return "B"
    if s >= 80:
        return "B-"
    if s >= 77:
        return "C+"
    if s >= 73:
        return "C"
    if s >= 70:
        return "C-"
    if s >= 67:
        return "D+"
    if s >= 63:
        return "D"
    if s >= 60:
        return "D-"
    return "F"


def chunk_text(text: str, limit: int = 1800) -> list[str]:
    text = text or ""
    if len(text) <= limit:
        return [text]
    out: list[str] = []
    cur = ""
    for part in text.split(" "):
        if not cur:
            cur = part
            continue
        if len(cur) + 1 + len(part) <= limit:
            cur += " " + part
        else:
            out.append(cur)
            cur = part
    if cur:
        out.append(cur)
    final: list[str] = []
    for s in out:
        if len(s) <= limit:
            final.append(s)
        else:
            for i in range(0, len(s), limit):
                final.append(s[i : i + limit])
    return final


def md_to_blocks(md: str) -> list[dict]:
    """Very small markdown-ish parser:
    - # / ## / ### headings
    - - bullets
    - 1. / 1) numbered items
    - blank lines
    """

    blocks: list[dict] = []

    def add_paragraph(p: str):
        if not p.strip():
            blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}})
            return
        for chunk in chunk_text(p.strip(), 1800):
            blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(chunk)}})

    for line in (md or "").splitlines():
        s = line.rstrip("\n")
        if not s.strip():
            add_paragraph("")
            continue

        if s.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3", "heading_3": {"rich_text": rt(s[4:].strip())}})
            continue
        if s.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(s[3:].strip())}})
            continue
        if s.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1", "heading_1": {"rich_text": rt(s[2:].strip())}})
            continue

        if s.startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(s[2:].strip())}})
            continue

        if len(s) >= 2 and s[0].isdigit() and s[1:2] in (".", ")"):
            blocks.append({"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": rt(s.strip())}})
            continue

        add_paragraph(s)

    return blocks


def append_children_batched(token: str, block_id: str, children: list[dict], batch_size: int = 80) -> None:
    for i in range(0, len(children), batch_size):
        req("PATCH", f"/blocks/{block_id}/children", token, {"children": children[i : i + batch_size]})
        time.sleep(0.25)


def list_children_blocks(token: str, block_id: str) -> list[dict]:
    out: list[dict] = []
    start_cursor = None
    while True:
        qs = {"page_size": 100}
        if start_cursor:
            qs["start_cursor"] = start_cursor
        path = f"/blocks/{block_id}/children?{urllib.parse.urlencode(qs)}"
        resp = req("GET", path, token)
        out.extend(resp.get("results", []) or [])
        if not resp.get("has_more"):
            break
        start_cursor = resp.get("next_cursor")
    return out


def delete_all_children(token: str, page_id: str) -> None:
    for b in list_children_blocks(token, page_id):
        bid = b.get("id")
        if not bid:
            continue
        try:
            req("DELETE", f"/blocks/{bid}", token)
        except Exception:
            pass
        time.sleep(0.35)


def parse_page_id(page_id_or_url: str) -> str:
    s = (page_id_or_url or "").strip()
    if not s:
        return ""
    if re.fullmatch(r"[0-9a-fA-F-]{32,36}", s):
        # normalize to dashed uuid if needed
        if len(s) == 32:
            return f"{s[0:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:32]}".lower()
        return s.lower()

    m = re.search(r"([0-9a-fA-F]{32})", s)
    if m:
        z = m.group(1)
        return f"{z[0:8]}-{z[8:12]}-{z[12:16]}-{z[16:20]}-{z[20:32]}".lower()

    m2 = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", s)
    if m2:
        return m2.group(1).lower()

    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="notion/homework_math.json", help="ids json from notion_homework_setup.py")

    ap.add_argument("--page-id", default="")
    ap.add_argument("--page-url", default="")
    ap.add_argument("--replace-body", action="store_true")

    ap.add_argument("--name", default="")
    ap.add_argument("--hw-date", default="")
    ap.add_argument("--due-date", default="")
    ap.add_argument("--course", default="")
    ap.add_argument("--module", default="")
    ap.add_argument("--topic", default="")
    ap.add_argument("--status", default="Checked")
    ap.add_argument("--result", default="Unknown")
    ap.add_argument("--wrong", type=int, default=None)
    ap.add_argument("--score", type=float, default=None)
    ap.add_argument("--grade", default="", help="Letter grade, e.g., A/B/C/D/F")
    ap.add_argument("--short-note", default="")
    ap.add_argument("--source", default="Telegram")
    ap.add_argument("--raw-url", default="")

    # New workflow fields
    ap.add_argument("--wrong-pdf", action="append", default=[], help="Path to 错题讲解 PDF (repeatable)")
    ap.add_argument("--tutoring-pdf", action="append", default=[], help="Path(s) to 补习讲解及扩展练习 PDFs (repeatable)")
    ap.add_argument("--practice-link", default="", help="扩展练习条目链接 URL")
    ap.add_argument("--homework-type", default="", help="学校作业 or 家庭扩展练习")

    ap.add_argument("files", nargs="*")
    args = ap.parse_args()

    token = notion_key()

    page_id = parse_page_id(args.page_id) or parse_page_id(args.page_url)

    md = sys.stdin.read() if not sys.stdin.isatty() else ""

    def upload_many(paths: list[str], label: str) -> list[str]:
        ids: list[str] = []
        for p in paths:
            if not p:
                continue
            if not os.path.exists(p):
                print(f"Missing {label} file: {p}", file=sys.stderr)
                continue
            ids.append(upload_file_to_notion(token, p))
        return ids

    # Upload attachments
    uploaded_ids = upload_many(args.files, "homework image")
    wrong_pdf_ids = upload_many(args.wrong_pdf, "wrong-pdf")
    tutoring_pdf_ids = upload_many(args.tutoring_pdf, "tutoring-pdf")

    files_prop = [{"type": "file_upload", "file_upload": {"id": fid}} for fid in uploaded_ids]
    wrong_pdf_prop = [{"type": "file_upload", "file_upload": {"id": fid}} for fid in wrong_pdf_ids]
    tutoring_pdf_prop = [{"type": "file_upload", "file_upload": {"id": fid}} for fid in tutoring_pdf_ids]

    props: dict = {}
    if args.hw_date:
        props["作业日期"] = {"date": {"start": args.hw_date}}
    if args.due_date:
        props["截止日期"] = {"date": {"start": args.due_date}}
    if args.course:
        props["课程名称"] = {"rich_text": rt(args.course)}
    if args.module:
        props["Module"] = {"rich_text": rt(args.module)}
    if args.topic:
        props["Lesson/Topic"] = {"rich_text": rt(args.topic)}
    if args.status:
        props["状态"] = {"select": {"name": args.status}}
    if args.result:
        props["检查结果"] = {"select": {"name": args.result}}
    if args.wrong is not None:
        props["错题数"] = {"number": args.wrong}
    if args.score is not None:
        props["得分"] = {"number": args.score}

    # Grade: explicit --grade wins; otherwise derive from numeric score when available.
    grade = (args.grade or "").strip()
    if not grade and args.score is not None:
        grade = score_to_grade(args.score)
    if grade:
        props["评分"] = {"select": {"name": grade}}
    if args.short_note:
        props["检查备注"] = {"rich_text": rt(args.short_note)}
    if args.source:
        props["来源"] = {"select": {"name": args.source}}
    if args.raw_url:
        props["原始链接"] = {"url": args.raw_url}
    if args.practice_link:
        props["扩展练习条目链接"] = {"url": args.practice_link}
    if args.homework_type:
        props["作业类型"] = {"select": {"name": args.homework_type}}
    if files_prop:
        props["作业图片"] = {"files": files_prop}
    if wrong_pdf_prop:
        props["错题讲解"] = {"files": wrong_pdf_prop}
    if tutoring_pdf_prop:
        props["补习讲解及扩展练习"] = {"files": tutoring_pdf_prop}

    created = False

    if page_id:
        if props:
            req("PATCH", f"/pages/{page_id}", token, {"properties": props})
    else:
        # create
        with open(args.ids, "r", encoding="utf-8") as f:
            ids = json.load(f)
        dsid = (ids.get("database") or {}).get("data_source_id")
        if not dsid:
            print("Missing data_source_id in ids json", file=sys.stderr)
            return 2
        if not args.name:
            print("--name required when creating a new record", file=sys.stderr)
            return 2

        props2 = {"Name": {"title": [{"text": {"content": args.name}}]}}
        props2.update(props)

        page = req(
            "POST",
            "/pages",
            token,
            {
                "parent": {"type": "data_source_id", "data_source_id": dsid},
                "properties": props2,
            },
        )
        page_id = page.get("id")
        created = True

    if (args.replace_body or created) and md.strip() and page_id:
        if args.replace_body:
            delete_all_children(token, page_id)
        blocks = md_to_blocks(md)
        append_children_batched(token, page_id, blocks)

    if not page_id:
        return 2

    page2 = req("GET", f"/pages/{page_id}", token)
    print(page2.get("url", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
