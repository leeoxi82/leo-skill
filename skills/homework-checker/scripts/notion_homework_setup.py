#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ensure a Notion Homework database exists and has the required schema.

Default target (Ethan):
  Haber / Ethan'sPG / College Prep / Homework / Math
  DB title: 🧮 Math Homework

Usage:
  python3 skills/homework-checker/scripts/notion_homework_setup.py \
    --path "Haber/Ethan'sPG/College Prep/Homework/Math" \
    --db-title "🧮 Math Homework" \
    --out notion/homework_math.json

Notes:
- Notion API 2025-09-03+: database schema lives on the data_source.
- This script finds/creates the page hierarchy, then finds/creates the inline database, then patches the schema.

Requires: ~/.config/notion/api_key
"""

from __future__ import annotations

import argparse
import json
import os
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


def req(method: str, path: str, token: str, body: dict | None = None) -> dict:
    url = API + path
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
        "User-Agent": "clawdbot/notion",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            if resp.status == 204:
                return {}
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} {url}: {raw}")


def page_title(page: dict) -> str:
    props = page.get("properties") or {}
    for v in props.values():
        if isinstance(v, dict) and v.get("type") == "title":
            arr = v.get("title") or []
            return "".join([x.get("plain_text", "") for x in arr])
    return ""


def data_source_title(ds: dict) -> str:
    arr = ds.get("title") or []
    return "".join([x.get("plain_text", "") for x in arr])


def search_pages_exact(token: str, title: str, limit: int = 20) -> list[dict]:
    out = req(
        "POST",
        "/search",
        token,
        {
            "query": title,
            "page_size": limit,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        },
    )
    results = []
    for r in out.get("results", []) or []:
        if r.get("object") != "page":
            continue
        if page_title(r).strip() == title:
            results.append(r)
    return results


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


def find_child_page_id(token: str, parent_page_id: str, child_title: str) -> str | None:
    for b in list_children_blocks(token, parent_page_id):
        if b.get("type") == "child_page":
            t = (b.get("child_page") or {}).get("title", "").strip()
            if t == child_title:
                return b.get("id")
    return None


def create_page_under_parent(token: str, parent_page_id: str, title: str) -> dict:
    return req(
        "POST",
        "/pages",
        token,
        {
            "parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": [{"text": {"content": title}}]}},
        },
    )


def ensure_path(token: str, path_titles: list[str]) -> dict:
    """Ensure a nested page path exists; return the final page object.

    Important: Workspaces can contain multiple pages with the same title (e.g., multiple "Haber").
    To avoid accidentally creating duplicate hierarchies, try all root candidates and prefer the one
    that already contains the deepest existing prefix of the target path.
    """

    root_title = path_titles[0]
    candidates = search_pages_exact(token, root_title, limit=50)

    if not candidates:
        # Attempt to create at workspace root (may fail depending on integration permissions)
        root_page = req(
            "POST",
            "/pages",
            token,
            {
                "parent": {"workspace": True},
                "properties": {"title": {"title": [{"text": {"content": root_title}}]}},
            },
        )
        candidates = [root_page]

    def traverse(root: dict) -> tuple[dict, int]:
        cur = root
        reached = 1
        for i, title in enumerate(path_titles[1:], start=2):
            cur_id = cur.get("id")
            if not cur_id:
                break
            child_id = find_child_page_id(token, cur_id, title)
            if not child_id:
                break
            cur = req("GET", f"/pages/{child_id}", token)
            reached = i
            time.sleep(0.05)
        return cur, reached

    best_root = candidates[0]
    best_cur, best_reached = traverse(best_root)

    for c in candidates[1:]:
        cur, reached = traverse(c)
        if reached > best_reached:
            best_root, best_cur, best_reached = c, cur, reached
        if best_reached >= len(path_titles):
            break

    # Create any missing tail pages under the best existing prefix.
    cur = best_cur
    for title in path_titles[best_reached:]:
        cur_id = cur.get("id")
        if not cur_id:
            raise RuntimeError("Could not resolve current page id")
        cur = create_page_under_parent(token, cur_id, title)
        best_reached += 1
        time.sleep(0.12)

    return cur


def find_data_source_by_title(token: str, title: str) -> dict | None:
    # In 2025-09-03+, search returns databases as object=data_source.
    out = req(
        "POST",
        "/search",
        token,
        {
            "query": title,
            "page_size": 50,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        },
    )
    for r in out.get("results", []) or []:
        if r.get("object") != "data_source":
            continue
        if data_source_title(r).strip() == title:
            return r
    return None


def ensure_database(token: str, parent_page_id: str, title: str) -> dict:
    existing_ds = find_data_source_by_title(token, title)
    if existing_ds and existing_ds.get("id"):
        ds_full = req("GET", f"/data_sources/{existing_ds['id']}", token)
        parent = ds_full.get("parent") or {}
        dbid = parent.get("database_id")
        if dbid:
            return req("GET", f"/databases/{dbid}", token)

    body = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": title}}],
        "is_inline": True,
        # schema is on data source in 2025-09-03+
        "properties": {},
    }
    return req("POST", "/databases", token, body)


def database_data_source_id(token: str, database_id: str) -> str:
    db = req("GET", f"/databases/{database_id}", token)
    dss = db.get("data_sources") or []
    if not dss:
        raise RuntimeError("database has no data_sources")
    dsid = dss[0].get("id")
    if not dsid:
        raise RuntimeError("missing data_source_id")
    return dsid


def patch_schema(token: str, data_source_id: str, desired: dict) -> list[str]:
    ds = req("GET", f"/data_sources/{data_source_id}", token)
    existing = set((ds.get("properties") or {}).keys())

    to_add = {k: v for k, v in desired.items() if k not in existing}
    if not to_add:
        return []

    req("PATCH", f"/data_sources/{data_source_id}", token, {"properties": to_add})
    return list(to_add.keys())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--path",
        default="Haber/Ethan'sPG/College Prep/Homework/Math",
        help="Slash-separated Notion page path (only used when creating a new hierarchy)",
    )
    ap.add_argument("--db-title", default="🧮 Math Homework")
    ap.add_argument("--out", default="notion/homework_math.json")
    ap.add_argument(
        "--force-create",
        action="store_true",
        help="Ignore existing --out file and create/resolve by --path",
    )
    args = ap.parse_args()

    token = notion_key()

    path_titles = [p.strip() for p in args.path.split("/") if p.strip()]

    # If an ids file already exists, treat it as the source of truth to avoid
    # accidentally creating duplicate page hierarchies in workspaces with duplicate titles.
    if (not args.force_create) and os.path.exists(args.out):
        with open(args.out, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if isinstance(existing.get("path"), list) and existing.get("path"):
            path_titles = existing["path"]

        dbid = (existing.get("database") or {}).get("database_id")
        dsid = (existing.get("database") or {}).get("data_source_id")
        if dbid and dsid:
            final_page = existing.get("page") or {}
            page_id = final_page.get("id")
            db = req("GET", f"/databases/{dbid}", token)
        else:
            # fall back to path resolution
            final_page = None
            page_id = None
            db = None
            dsid = None
    else:
        final_page = None
        page_id = None
        db = None
        dsid = None

    if not dsid or not db:
        if len(path_titles) < 2:
            print("--path must contain at least 2 segments", file=sys.stderr)
            return 2

        final_page = ensure_path(token, path_titles)
        page_id = final_page.get("id")
        if not page_id:
            raise RuntimeError("Could not resolve final page id")

        db = ensure_database(token, page_id, args.db_title)
        dbid = db.get("id")
        if not dbid:
            raise RuntimeError("Could not resolve database id")

        dsid = database_data_source_id(token, dbid)

    status_opts = [
        {"name": "New", "color": "blue"},
        {"name": "Submitted", "color": "gray"},
        {"name": "Checked", "color": "green"},
        {"name": "Needs Fix", "color": "red"},
        {"name": "Done", "color": "default"},
    ]

    result_opts = [
        {"name": "All correct", "color": "green"},
        {"name": "Minor mistakes", "color": "yellow"},
        {"name": "Needs redo", "color": "red"},
        {"name": "Unknown", "color": "gray"},
    ]

    source_opts = [
        {"name": "Telegram", "color": "blue"},
        {"name": "Notion upload", "color": "default"},
        {"name": "Other", "color": "gray"},
    ]

    hw_type_opts = [
        {"name": "学校作业", "color": "blue"},
        {"name": "家庭扩展练习", "color": "purple"},
    ]

    # Default +/- grading scale (common US HS scale).
    # If Leo later provides LOHS-specific cutoffs, update these boundaries and re-run setup.
    grade_opts = [
        {"name": "A+", "color": "green"},
        {"name": "A", "color": "green"},
        {"name": "A-", "color": "green"},
        {"name": "B+", "color": "blue"},
        {"name": "B", "color": "blue"},
        {"name": "B-", "color": "blue"},
        {"name": "C+", "color": "yellow"},
        {"name": "C", "color": "yellow"},
        {"name": "C-", "color": "yellow"},
        {"name": "D+", "color": "orange"},
        {"name": "D", "color": "orange"},
        {"name": "D-", "color": "orange"},
        {"name": "F", "color": "red"},
    ]

    desired_schema = {
        "作业日期": {"name": "作业日期", "date": {}},
        "截止日期": {"name": "截止日期", "date": {}},
        "课程名称": {"name": "课程名称", "rich_text": {}},
        "Module": {"name": "Module", "rich_text": {}},
        "Lesson/Topic": {"name": "Lesson/Topic", "rich_text": {}},
        "状态": {"name": "状态", "select": {"options": status_opts}},
        "检查结果": {"name": "检查结果", "select": {"options": result_opts}},
        "错题数": {"name": "错题数", "number": {"format": "number"}},
        "得分": {"name": "得分", "number": {"format": "number"}},
        "评分": {"name": "评分", "select": {"options": grade_opts}},
        "检查备注": {"name": "检查备注", "rich_text": {}},
        "作业图片": {"name": "作业图片", "files": {}},
        "答案/参考": {"name": "答案/参考", "files": {}},
        "错题讲解": {"name": "错题讲解", "files": {}},
        "补习讲解及扩展练习": {"name": "补习讲解及扩展练习", "files": {}},
        "扩展练习条目链接": {"name": "扩展练习条目链接", "url": {}},
        "作业类型": {"name": "作业类型", "select": {"options": hw_type_opts}},
        "来源": {"name": "来源", "select": {"options": source_opts}},
        "原始链接": {"name": "原始链接", "url": {}},
    }

    added = patch_schema(token, dsid, desired_schema)

    out = {
        "path": path_titles,
        "page": {"id": page_id, "title": path_titles[-1], "url": final_page.get("url")},
        "database": {"database_id": dbid, "data_source_id": dsid, "title": args.db_title, "url": db.get("url")},
        "schema_added": added,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
