#!/usr/bin/env python
"""Refresh the tracker from Aced's public FDE question listing."""

from __future__ import annotations

import argparse
import gzip
import html as html_lib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://www.aced.io/questions"
ROLE = "forward-deployed-engineer"
MIN_EXPECTED_QUESTIONS = 100
NEXT_DATA_RE = re.compile(
    r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', re.DOTALL
)
DATASET_RE = re.compile(r"const D=\[.*?\],K=", re.DOTALL)


def extract_payload(html: str) -> dict:
    match = NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("Aced page did not contain __NEXT_DATA__")
    document = json.loads(html_lib.unescape(match.group(1)))
    return document["props"]["pageProps"]["initialQuestions"]


def age_label(value: str | None, today: date | None = None) -> str:
    if not value:
        return "Recently"
    today = today or datetime.now(timezone.utc).date()
    asked = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    days = max(0, (today - asked).days)
    if days == 0:
        return "today"
    if days == 1:
        return "a day ago"
    if days < 30:
        return f"{days} days ago"
    months = max(1, days // 30)
    if months < 12:
        return "a month ago" if months == 1 else f"{months} months ago"
    years = max(1, days // 365)
    return "a year ago" if years == 1 else f"{years} years ago"


def normalize_question(raw: dict, today: date | None = None) -> dict:
    return {
        "title": raw["data"]["title"].strip(),
        "url": f"https://www.aced.io/questions/{raw['id']}/{raw['slug']}",
        "age": age_label(raw.get("last_asked_on"), today=today),
        "categories": list(dict.fromkeys(raw.get("category") or [])),
        "companies": list(
            dict.fromkeys(company["name"] for company in (raw.get("companies") or []) if company.get("name"))
        ),
    }


def fetch_page(page: int) -> dict:
    query = urlencode({"role": ROLE, "page": page})
    request = Request(
        f"{BASE_URL}?{query}",
        headers={
            "User-Agent": "fde-interview-tracker/1.0 (+https://github.com/FairyFox5700/fde-interview-tracker)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "gzip",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=90) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return extract_payload(body.decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch Aced page {page}") from last_error


def fetch_all_questions() -> list[dict]:
    first = fetch_page(1)
    expected_count = int(first["count"])
    limit = int(first["pagination"]["limit"])
    page_count = (expected_count + limit - 1) // limit
    if page_count > 50:
        raise RuntimeError("Refusing to fetch more than 50 pages")

    payloads = [first]
    if page_count > 1:
        with ThreadPoolExecutor(max_workers=4) as pool:
            payloads.extend(pool.map(fetch_page, range(2, page_count + 1)))

    raw_by_id: dict[int, dict] = {}
    for payload in payloads:
        if int(payload["count"]) != expected_count:
            raise RuntimeError("Aced question count changed during refresh; retry later")
        for question in payload["results"]:
            raw_by_id[question["id"]] = question

    if expected_count < MIN_EXPECTED_QUESTIONS:
        raise RuntimeError(f"Aced returned suspicious question count: {expected_count}")
    if len(raw_by_id) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} unique questions but collected {len(raw_by_id)}"
        )

    questions = [normalize_question(question) for question in raw_by_id.values()]
    questions.sort(key=lambda item: item["url"])
    return questions


def replace_dataset(html: str, questions: list[dict]) -> str:
    compact_json = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    replacement = f"const D={compact_json},K="
    updated, count = DATASET_RE.subn(lambda _: replacement, html, count=1)
    if count != 1:
        raise ValueError("Could not locate the embedded tracker dataset")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fetch and validate without writing index.html")
    parser.add_argument("--index", type=Path, default=Path(__file__).resolve().parents[1] / "index.html")
    args = parser.parse_args()

    questions = fetch_all_questions()
    current = args.index.read_text(encoding="utf-8")
    updated = replace_dataset(current, questions)
    changed = updated != current
    if changed and not args.check:
        args.index.write_text(updated, encoding="utf-8")
    print(json.dumps({"questions": len(questions), "changed": changed, "written": changed and not args.check}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
