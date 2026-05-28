#!/usr/bin/env python3
"""
query_perplexity.py — Perplexity Sonar API で市場リサーチ

使い方:
    python query_perplexity.py "<question>" [--model sonar|sonar-pro] [--recency month|year]

env:
    PERPLEXITY_API_KEY (必須)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests


def query(
    question: str,
    model: str = "sonar",
    recency: str | None = "year",
) -> dict:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY is required")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "あなたは事実ベースの市場リサーチャーです。"
                    "数値・固有名詞・統計には必ず出典 URL を付け、"
                    "推測や評価語を含めないでください。"
                ),
            },
            {"role": "user", "content": question},
        ],
    }
    if recency:
        payload["search_recency_filter"] = recency

    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()

    answer = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])

    return {
        "question": question,
        "model": model,
        "answer": answer,
        "citations": citations,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--model", default="sonar", choices=["sonar", "sonar-pro"])
    ap.add_argument("--recency", default="year", choices=["month", "year", "none"])
    ap.add_argument("--out")
    args = ap.parse_args()

    recency = None if args.recency == "none" else args.recency
    result = query(args.question, model=args.model, recency=recency)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
