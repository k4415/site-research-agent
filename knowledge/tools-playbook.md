# Tools Playbook

リサーチツールの使い分け。

## 自動トリガー条件（research-plan が判断するルール）

各ツールはこの条件で自動起動される。手動指示なしで `research-plan` skill が分岐する:

| 条件 | 起動するツール | 担当 skill |
|---|---|---|
| `research_needs.competitors[].url` がある | `scripts/extract_lp_schema.py`（Firecrawl JSON mode） | `competitor-scrape` |
| `research_needs.competitors[].discover: true` | `scripts/query_perplexity.py` で発見 → `extract_lp_schema.py` | `competitor-scrape` |
| `research_needs.market_intelligence[]` にエントリ | `scripts/query_perplexity.py`（必須） + `scripts/query_estat.py`（日本国内案件） | `market-research` |
| `research_needs.market_intelligence[].preferred_sources` に URL が含まれる | `scripts/fetch_lp.py` でその URL も取得 | `market-research` |
| `research_needs.voc[].media: x` | `aachat session run x-research-expert`（AUTH_TOKEN + CT0 + X_BEARER_TOKEN） | `voc-research` |
| `research_needs.voc[].media: client_voc_url` | `scripts/fetch_lp.py` でレビューページ取得 | `voc-research` |
| `research_needs.client_assets[].deep_scan: true` | `scripts/fetch_lp.py` (auto = Jina → Firecrawl fallback) | `client-asset-parse` |
| `pre_shared_assets[].type == existing_website` で deep_scan 未指定 | デフォルト deep_scan: true として扱う | `client-asset-parse` |

すべての URL は **常に Jina Reader を先に試し、失敗 or 不十分な場合のみ Firecrawl にフォールバック**（コスト最適化）。

### env 要件

- `FIRECRAWL_API_KEY`: `competitor-scrape` / `client-asset-parse` の fallback に必要
- `PERPLEXITY_API_KEY`: `market-research` / `competitor-scrape`（discover）に必要
- `ESTAT_APP_ID`: 日本国内 `market-research` に推奨（無料）
- `JINA_API_KEY`: 任意（無料枠 20 req/分で多くの場合足りる）
- `AUTH_TOKEN` + `CT0`: x-research-expert の bird CLI 認証に必要
- `X_BEARER_TOKEN`: x-research-expert の X API v2 fallback に必要

env がない場合、該当 skill は fail-fast し `failed_fetches` に記録、orchestrator にエスカレーション。

## LP 取得

### 一次選択: Jina Reader

```bash
curl -s "https://r.jina.ai/<URL>"
```

- 無料 20 req/分。API key で 500 req/分
- URL の頭に `r.jina.ai/` を付けるだけで Markdown 化
- JS heavy なサイト（Wix, Webflow, React SPA）でも基本的に動く
- 失敗時は status 5xx を返す

### 二次選択: Firecrawl `/scrape` JSON mode

```python
import requests
r = requests.post(
    "https://api.firecrawl.dev/v1/scrape",
    headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
    json={
        "url": url,
        "formats": ["json"],
        "jsonOptions": { "schema": EXTRACTION_SCHEMA }
    }
)
```

- 構造化抽出が必要な場合
- Jina Reader が失敗 / 取得が不完全な場合
- Hobby $16/月（1,000 ページ）

### 三次選択（最後の手段）: Playwright + readability

```python
from playwright.sync_api import sync_playwright
from readability import Document
```

- Bot 検知が厳しいサイト
- ログイン必須サイト（クライアント許可ある場合のみ）
- 完全自前ホストで無料だが実装コスト高い

## 構造化抽出

### Firecrawl JSON mode（推奨）

スキーマを渡せば自動で抽出される。`knowledge/extraction-schema.md` のスキーマを使う。

### LLM 抽出（fallback）

Jina で取得した Markdown を Claude / GPT に渡し、スキーマ準拠の JSON を出させる。
プロンプトに `additionalProperties: false` を明示し、enum を制約に使う。

## 市場リサーチ

### Perplexity Sonar API

```python
import requests
r = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
    json={
        "model": "sonar",
        "messages": [{
            "role": "user",
            "content": "<question>"
        }],
        "search_recency_filter": "year"
    }
)
```

- 検索付き LLM。出典 URL を必ず返す
- Sonar Pro は $3/Mtok 入力 / $15/Mtok 出力
- 「市場規模」「主要プレイヤー」「業界トレンド」に最適

### e-Stat API

```python
import requests
r = requests.get(
    "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData",
    params={
        "appId": ESTAT_APP_ID,
        "statsDataId": "<該当 stats data ID>",
        "limit": 100
    }
)
```

- 経済センサス・商業統計・産業別生産動態
- 無料、要 appId
- 日本国内市場の一次情報

## VOC

### X（既存 x-research-expert に委譲）

`knowledge/x-research-handoff.md` のテンプレに従う。

### Reddit / Yahoo知恵袋

必要なら Apify などのスクレイピングサービスを検討。robots.txt と ToS に注意。

## クライアント提供資料

- URL → Jina Reader で取得
- PDF → 適切な PDF parser（pypdf / pdfplumber）
- テキスト → そのまま読む

## コスト管理

月額目安：

- Firecrawl Hobby: $16
- Perplexity（従量）: $5〜$20
- Jina / e-Stat / x-research-expert: 無料

合計 **$20〜$40 で実用ライン**。priority high の項目に予算を集中する。
