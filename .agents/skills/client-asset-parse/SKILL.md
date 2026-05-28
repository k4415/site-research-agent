---
name: client-asset-parse
description: クライアント提供資料を pre_shared_assets リストから自動取得し構造化する。「資料解析」「事前資料を読む」「pre_shared_assets parse」などのトリガーで起動。
---

# client-asset-parse

research-plan の W4 ワークストリーム。**`requirements/<case-id>.md` の `research_needs.client_assets` と `cases/<case-id>.md` の `pre_shared_assets`** を入力源とし、各 URL を `scripts/fetch_lp.py` で自動取得して構造化する。

hearing 段階で集めた事前共有資料を network 経由で実取得・構造化することが目的。

## いつ起動するか

- `research-plan` skill から並列起動される
- 単独で「クライアント提供資料を解析」と依頼された時

## 入力

優先順位:
1. **`requirements/<case-id>.md` の `research_needs.client_assets`**（requirements-agent が生成した deep_scan 指示リスト）
2. `cases/<case-id>.md` の `pre_shared_assets`（client_assets が無い場合のフォールバック）
3. クライアントが aachat shared doc にアタッチした PDF / 画像

## 実行手順

### 1. 対象 URL リストの構築

`research_needs.client_assets` を全件読み、priority high のものから処理する。

```yaml
research_needs:
  client_assets:
    - { type: existing_website, url: "https://client.example.com/", deep_scan: true, priority: high }
    - { type: product_catalog, url: "https://client.example.com/products", deep_scan: true, priority: high }
    - { type: voc_review, url: "https://client.example.com/reviews", deep_scan: true, priority: medium }
    - { type: sales_deck, url: "https://drive.google.com/...", deep_scan: false, priority: low }
```

`deep_scan: false` のものは取得をスキップ（または summary だけ取る）。`deep_scan: true` を全件処理する。

### 2. URL を順次取得（rate limit 配慮）

各 URL に対し:

```bash
python scripts/fetch_lp.py <url> --mode auto --out /tmp/client_asset_<i>.json
```

`--mode auto` は Jina Reader → Firecrawl の順にフォールバック。

**rate limit 考慮**:
- Jina 無料枠: 20 req/分。10 URL 以上ある場合は 3 秒間隔で順次実行
- 失敗（403 / 認証必要 / 404）は黙らず `failed_fetches` に理由付きで記録

### 3. type 別の構造化抽出

#### existing_website / inspiration_like / inspiration_dislike

`knowledge/extraction-schema.md` の競合 LP 抽出スキーマと同じものを適用（自社サイトでも構造は同じ）。`scripts/extract_lp_schema.py` を使う:

```bash
python scripts/extract_lp_schema.py <url> --out /tmp/client_extract_<i>.json
```

抽出項目: hero / value_proposition / benefits / features / social_proof / pricing / faq / narrative_structure / tech_signals

#### product_catalog

商品/サービス情報を Markdown 化 → 以下を抽出:
- 商品名 / カテゴリ
- 価格 / プラン
- 機能 / スペック
- ターゲット記述（クライアントが書いた言葉）
- 既存のコピー文（後続制作の参考）

#### voc_review

レビュー・お客様の声ページから:
- 投稿者・属性
- レビュー本文（**生の引用** で保存）
- 評価点 / 評価日
- ポジティブ / ネガティブの分類

これは VOC として要件・ブリーフに反映される第一級の情報源。

#### sales_deck

PDF / Slides を取得して:
- 主張している USP
- ベネフィット表現
- 数値根拠 / RTB
- 使われている言葉遣い

#### industry_report

業界レポート URL を取得して、市場規模・トレンド・主要プレイヤーに関する記述を抽出。
→ `market-research` skill にも共有して preferred_sources として活用。

### 4. クライアントの公式記述は最優先

- 競合分析や Perplexity の出力と矛盾があった場合、クライアント公式記述（existing_website / product_catalog / sales_deck）を優先
- 矛盾は **`research-insight/<case-id>.md`** の「他社情報との差異」として明示

### 5. case doc の pre_shared_assets を更新

各 URL を取得・構造化したら、case doc の対応 entry を `status: parsed` に更新（orchestrator に session send）:

```
cases/<case-id>.md の pre_shared_assets で type=existing_website, url=https://... のエントリを status: parsed に更新してください。
```

### 6. 結果記録

`research-plan/<case-id>.md`（中間 doc）に:

```yaml
w4_client_asset_parse:
  status: done
  assets_parsed:
    - source: "https://client.example.com/"
      type: existing_website
      tool_used: jina_reader
      extracted: { ... }  # extraction-schema 準拠
      fetched_at: <ISO8601>
    - source: "https://client.example.com/products"
      type: product_catalog
      extracted:
        products: [...]
        pricing: [...]
        existing_copy: [...]
    - source: "https://client.example.com/reviews"
      type: voc_review
      extracted:
        reviews: [
          { author: "...", text: "<生引用>", date: "...", sentiment: positive }
        ]
  failed_fetches:
    - { url: "https://drive.google.com/...", reason: "認証必要" }
```

最終 fact レポート `research/<case-id>.md` には、これらの抽出結果を「クライアント既存資産」セクションとして統合する。

## NG

- 提供資料の数値・固有名詞を意訳・改変する
- 機密情報（売上数値など）を考察レポートに不必要に出す
- 取得失敗を黙る（必ず `failed_fetches` に記録）
- secret / token / 内部 URL を doc に書く
- rate limit を無視して並列大量 fetch（Jina 無料枠を一気に使い切る）
