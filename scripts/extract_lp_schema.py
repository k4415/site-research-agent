#!/usr/bin/env python3
"""
extract_lp_schema.py — 競合 LP を Firecrawl JSON mode で構造化抽出する

knowledge/extraction-schema.md のスキーマを使い、competitor_lp.json を出力する。

使い方:
    python extract_lp_schema.py <url> [--out path]

env:
    FIRECRAWL_API_KEY (必須)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests

EXTRACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "product_name": {"type": "string"},
                "category": {"type": "string"},
                "language": {"type": "string"},
            },
        },
        "hero": {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "subhead": {"type": "string"},
                "primary_cta_text": {"type": "string"},
                "hero_visual_type": {
                    "type": "string",
                    "enum": ["product_screenshot", "illustration", "video", "photo", "none"],
                },
                "awareness_level_target": {
                    "type": "string",
                    "enum": ["unaware", "problem_aware", "solution_aware", "product_aware", "most_aware"],
                },
            },
        },
        "value_proposition": {
            "type": "object",
            "properties": {
                "core_promise": {"type": "string"},
                "icp_signals": {"type": "array", "items": {"type": "string"}},
                "differentiators": {"type": "array", "items": {"type": "string"}},
            },
        },
        "problem_amplify": {
            "type": "object",
            "properties": {
                "problems_listed": {"type": "array", "items": {"type": "string"}},
                "pain_intensity_signals": {"type": "array", "items": {"type": "string"}},
            },
        },
        "benefits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "outcome": {"type": "string"},
                    "feature_mapped": {"type": "string"},
                },
            },
        },
        "features": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "order_in_page": {"type": "integer"},
                },
            },
        },
        "social_proof": {
            "type": "object",
            "properties": {
                "logos": {"type": "array", "items": {"type": "string"}},
                "testimonials": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "quote": {"type": "string"},
                            "author": {"type": "string"},
                            "role": {"type": "string"},
                            "company": {"type": "string"},
                        },
                    },
                },
                "case_studies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "kpi_improvement": {"type": "string"},
                            "summary": {"type": "string"},
                        },
                    },
                },
                "metrics_claimed": {"type": "array", "items": {"type": "string"}},
                "media_mentions": {"type": "array", "items": {"type": "string"}},
            },
        },
        "pricing": {
            "type": "object",
            "properties": {
                "plans": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "string"},
                            "billing_cycle": {"type": "string"},
                            "features_highlighted": {"type": "array", "items": {"type": "string"}},
                            "is_recommended": {"type": "boolean"},
                        },
                    },
                },
                "free_trial": {"type": "boolean"},
                "freemium": {"type": "boolean"},
            },
        },
        "ctas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "position": {"type": "string", "enum": ["hero", "mid", "sticky", "footer"]},
                    "type": {
                        "type": "string",
                        "enum": ["signup", "demo", "contact", "download", "trial"],
                    },
                },
            },
        },
        "faq": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "objection_category": {"type": "string"},
                },
            },
        },
        "narrative_structure": {
            "type": "object",
            "properties": {
                "framework_match": {
                    "type": "string",
                    "enum": ["AIDA", "PASTOR", "PAS", "StoryBrand", "SaaS_default", "other"],
                },
                "section_order": {"type": "array", "items": {"type": "string"}},
                "page_length_words": {"type": "integer"},
            },
        },
        "tech_signals": {
            "type": "object",
            "properties": {
                "form_fields_count": {"type": "integer"},
                "has_video": {"type": "boolean"},
                "has_chatbot": {"type": "boolean"},
                "analytics_tools_detected": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


def extract(url: str) -> dict:
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is required")

    r = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "url": url,
            "formats": ["json"],
            "jsonOptions": {"schema": EXTRACTION_SCHEMA},
        },
        timeout=180,
    )
    r.raise_for_status()
    data = r.json().get("data", {})
    return {
        "meta": {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat()},
        "extracted": data.get("json", {}),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out")
    args = ap.parse_args()

    result = extract(args.url)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
