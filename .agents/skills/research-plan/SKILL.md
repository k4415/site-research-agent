---
name: research-plan
description: requirements の research_needs + cases の pre_shared_assets を読み、4 並列ワークストリームに分解する。「リサーチ開始」「research-plan」などのトリガーで起動。
---

# research-plan

`requirements/<case-id>.md` の `research_needs` と `cases/<case-id>.md` の `pre_shared_assets` を読み、4 つのワークストリームに分解し、並列実行可能な形に整理する。

## いつ起動するか

- orchestrator から「リサーチを開始」依頼を受けた時
- `research/<case-id>.md` がまだ存在しない時

## 入力

- `requirements/<case-id>.md`（research_needs 必須）
- `cases/<case-id>.md`（pre_shared_assets を二次確認）

## 実行手順

### 1. 入力読み込み

- `requirements/<case-id>.md` の `research_needs` を全て読む（competitors / client_assets / market_intelligence / voc）
- priority、preferred_sources、reason を確認
- `cases/<case-id>.md` の `pre_shared_assets` も読んで research_needs から漏れた事前資料がないかチェック

### 2. 4 ワークストリームに分解

| W | skill | 入力 | ツール |
|---|---|---|---|
| W1 | competitor-scrape | `research_needs.competitors` 全件 | `scripts/fetch_lp.py` + `scripts/extract_lp_schema.py`（Firecrawl JSON mode） |
| W2 | market-research | `research_needs.market_intelligence` 全件 | `scripts/query_perplexity.py` + `scripts/query_estat.py` |
| W3 | voc-research | `research_needs.voc` で media:x のもの | `aachat session run x-research-expert`（AUTH_TOKEN + CT0 + X_BEARER_TOKEN 認証） |
| W4 | client-asset-parse | `research_needs.client_assets` 全件 + pre_shared_assets | `scripts/fetch_lp.py` |

### 3. コスト・時間見積もり

| W | 想定コスト | 想定時間 |
|---|---|---|
| W1 | 競合 N 本 × Firecrawl $0.016 = $0.016 × N | 1 本あたり 30 秒 |
| W2 | Perplexity Sonar M 件 × ~$0.005 = $0.005 × M | 1 件あたり 10 秒 |
| W3 | x-research-expert 起動（API 課金は X 側無料、bird CLI 無料） | 5〜15 分 |
| W4 | URL N 本 × Jina 無料 / Firecrawl fallback $0.016 | 1 本あたり 5〜30 秒 |

合計で **$1 未満〜$3 程度 / 案件**。priority high を優先消化、low は予算余裕があれば。

### 4. 実行計画を保存

中間 doc `research-plan/<case-id>.md` に保存:

```yaml
---
case_id: <case-id>
workstreams:
  w1_competitor_scrape:
    status: pending
    targets:
      - { name: "Canva", url: "https://...", source: hearing, priority: high }
      - { name: "Adobe Express", url: "https://...", source: pre_shared_assets, priority: high }
      - { name: null, url: null, discover: true, priority: medium }
    estimated_cost_usd: 0.05
  w2_market_research:
    status: pending
    queries:
      - { topic: "国内デザインツール市場規模", priority: high, sources: ["e-Stat", "Perplexity Sonar"] }
    estimated_cost_usd: 0.02
  w3_voc_research:
    status: pending
    keywords: ["AI バナー 違和感", "Canva やめた"]
    delegated_to: x-research-expert
  w4_client_asset_parse:
    status: pending
    assets:
      - { type: existing_website, url: "https://client.example.com/", deep_scan: true }
      - { type: voc_review, url: "https://...", deep_scan: true }
    estimated_cost_usd: 0.01
priority_order: [w1, w2, w4, w3]   # w3 は時間かかるので並列、w1/w2/w4 は短時間
total_estimated_cost_usd: 0.08
---
```

### 5. 並列実行を起動

4 つの skill を並列で起動：

- `competitor-scrape`
- `market-research`
- `voc-research`
- `client-asset-parse`

各 skill は完了時に `research-plan/<case-id>.md` の対応 status を `done` に更新する。

### 6. 全完了待ち → synthesize

4 ワークストリームが全て done になったら `synthesize-research` skill を起動。

ただし W3 だけ時間がかかる場合は、W3 を待つ間に W1/W2/W4 の中間結果を `synthesize-research` の事前整理に流せる（最終 synthesize は W3 完了後）。

## ツール起動条件サマリ（参照: `knowledge/tools-playbook.md`）

| 条件 | 起動するツール / skill |
|---|---|
| `research_needs.competitors[].url` がある | `competitor-scrape` → `extract_lp_schema.py`（Firecrawl） |
| `research_needs.competitors[].discover: true` | `competitor-scrape` → `query_perplexity.py` で発見 → `extract_lp_schema.py` |
| `research_needs.market_intelligence` にエントリ | `market-research` → `query_perplexity.py` + `query_estat.py` |
| `research_needs.voc[].media: x` | `voc-research` → `x-research-expert` に session run |
| `research_needs.client_assets[].deep_scan: true` | `client-asset-parse` → `fetch_lp.py`（auto = Jina→Firecrawl） |

## NG

- 並列化できるのに直列実行する
- `discover: true` の競合を「URL がないから skip」する（必ず発見を試みる）
- priority low のタスクで時間 / コストを使い切る
- pre_shared_assets / client_assets の存在を確認せず無視する
