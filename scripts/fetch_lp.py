#!/usr/bin/env python3
"""
fetch_lp.py — LP の本文を取得する

優先順位:
1. Jina Reader (r.jina.ai/<URL>) - 無料 20 req/分
2. Firecrawl /scrape - 構造化が必要 or Jina 失敗時
3. Playwright + readability - 上記が両方失敗時

使い方:
    python fetch_lp.py <url> [--mode jina|firecrawl|auto] [--out path]

env:
    JINA_API_KEY (任意)
    FIRECRAWL_API_KEY (必須 for firecrawl mode)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone

import requests


def fetch_via_jina(url: str) -> dict:
    headers = {}
    if api_key := os.environ.get("JINA_API_KEY"):
        headers["Authorization"] = f"Bearer {api_key}"
    headers["X-Return-Format"] = "markdown"

    encoded = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%")
    r = requests.get(f"https://r.jina.ai/{encoded}", headers=headers, timeout=60)
    r.raise_for_status()
    return {
        "source": "jina_reader",
        "url": url,
        "markdown": r.text,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch_via_firecrawl(url: str, schema: dict | None = None) -> dict:
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is required for firecrawl mode")

    payload: dict = {"url": url, "formats": ["markdown"]}
    if schema:
        payload["formats"].append("json")
        payload["jsonOptions"] = {"schema": schema}

    r = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    data = r.json().get("data", {})
    return {
        "source": "firecrawl",
        "url": url,
        "markdown": data.get("markdown", ""),
        "json": data.get("json"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch_auto(url: str) -> dict:
    """Jina で試し、失敗 or markdown が短すぎたら Firecrawl にフォールバック"""
    try:
        result = fetch_via_jina(url)
        if len(result["markdown"]) >= 500:
            return result
        # 500 字未満は失敗とみなす
        sys.stderr.write(f"Jina returned too short content ({len(result['markdown'])} chars), falling back to Firecrawl\n")
    except Exception as e:
        sys.stderr.write(f"Jina failed: {e}, falling back to Firecrawl\n")

    return fetch_via_firecrawl(url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--mode", choices=["jina", "firecrawl", "auto"], default="auto")
    ap.add_argument("--out", help="output JSON file path. default stdout")
    args = ap.parse_args()

    if args.mode == "jina":
        result = fetch_via_jina(args.url)
    elif args.mode == "firecrawl":
        result = fetch_via_firecrawl(args.url)
    else:
        result = fetch_auto(args.url)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
