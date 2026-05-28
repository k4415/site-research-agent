# Tools Playbook

リサーチツールの使い分け。

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
