---
name: research-plan
description: requirements の research_needs を読み、4 並列ワークストリームに分解する。「リサーチ開始」「research-plan」などのトリガーで起動。
---

# research-plan

`requirements/<case-id>.md` の `research_needs` を読み、4 つのワークストリームに分解し、並列実行可能な形に整理する。

## いつ起動するか

- orchestrator から「リサーチを開始」依頼を受けた時
- `research/<case-id>.md` がまだ存在しない時

## 実行手順

1. **入力読み込み**
   - `requirements/<case-id>.md` の `research_needs` を全て読む
   - priority、preferred_sources、reason を確認

2. **4 ワークストリームに分解**
   - **W1: competitor-scrape**: research_needs.competitors を入力
   - **W2: market-research**: research_needs.market_intelligence を入力
   - **W3: voc-research**: research_needs.voc を入力
   - **W4: client-asset-parse**: クライアント提供資料があれば

3. **コスト・時間見積もり**
   - W1: 競合 N 本 × Firecrawl 1 ページ = $0.016 × N
   - W2: Perplexity Sonar クエリ M 件 × ~$0.005 = $0.005 × M
   - W3: x-research-expert 起動（無料、X cookie 必要）
   - W4: 提供資料の量による

4. **実行計画を保存**
   - 一時 doc として `research-plan/<case-id>.md` に保存（後で参照可能に）
   - 構造:
     ```yaml
     ---
     case_id: <case-id>
     workstreams:
       w1_competitor_scrape:
         status: pending
         targets: [...]
         estimated_cost: $0.16
       w2_market_research:
         status: pending
         queries: [...]
         estimated_cost: $0.05
       w3_voc_research:
         status: pending
         keywords: [...]
         delegated_to: x-research-expert
       w4_client_asset_parse:
         status: pending
         assets: [...]
     priority_order: [w1, w2, w3, w4]
     ---
     ```

5. **並列実行を起動**
   - 4 つの skill を並列で起動：`competitor-scrape`、`market-research`、`voc-research`、`client-asset-parse`
   - 各 skill は完了時に `research-plan/<case-id>.md` の対応 status を `done` に更新する

6. **全完了待ち**
   - 4 ワークストリームが全て done になったら `synthesize-research` skill を起動

## NG

- 並列化できるのに直列実行する
- discover: true の競合を「URL がないから skip」する（必ず発見を試みる）
- priority low のタスクで時間 / コストを使い切る
