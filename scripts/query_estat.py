#!/usr/bin/env python3
"""
query_estat.py — e-Stat（政府統計総合窓口）API で日本国内統計を取得

使い方:
    # 統計表 ID を知っている場合
    python query_estat.py --stats-data-id 0003000001

    # キーワードから統計表を探す
    python query_estat.py --search "経済センサス"

env:
    ESTAT_APP_ID (必須)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests

BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json"


def search_stats_list(keyword: str, limit: int = 20) -> dict:
    app_id = os.environ.get("ESTAT_APP_ID")
    if not app_id:
        raise RuntimeError("ESTAT_APP_ID is required")

    r = requests.get(
        f"{BASE_URL}/getStatsList",
        params={
            "appId": app_id,
            "searchWord": keyword,
            "limit": limit,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def get_stats_data(stats_data_id: str, limit: int = 100) -> dict:
    app_id = os.environ.get("ESTAT_APP_ID")
    if not app_id:
        raise RuntimeError("ESTAT_APP_ID is required")

    r = requests.get(
        f"{BASE_URL}/getStatsData",
        params={
            "appId": app_id,
            "statsDataId": stats_data_id,
            "limit": limit,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats-data-id")
    ap.add_argument("--search")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out")
    args = ap.parse_args()

    if not args.stats_data_id and not args.search:
        ap.error("either --stats-data-id or --search is required")

    if args.search:
        result = search_stats_list(args.search, limit=args.limit)
    else:
        result = get_stats_data(args.stats_data_id, limit=args.limit)

    payload = {
        "query": {"stats_data_id": args.stats_data_id, "search": args.search},
        "response": result,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
