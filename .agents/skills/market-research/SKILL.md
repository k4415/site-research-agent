---
name: market-research
description: Perplexity Sonar + e-Stat で市場規模・業界トレンドを取得。「市場リサーチ」「業界調査」などのトリガーで起動。
---

# market-research

research-plan の W2 ワークストリーム。市場規模・業界トレンドを出典付きで取得する。

## いつ起動するか

- `research-plan` skill から並列起動される
- 単独で「<業界>の市場規模を調べて」と依頼された時

## 実行手順

1. **research_needs.market_intelligence を読む**
   - 各 topic に preferred_sources が指定されていればそれに従う
   - priority high を先に処理

2. **e-Stat API（日本国内統計）**
   - preferred_sources に「e-Stat」が含まれる場合
   - まず統計表検索：
     ```bash
     python scripts/query_estat.py --search "<keyword>" --limit 10
     ```
   - 候補から該当する統計表 ID を選び、データ取得：
     ```bash
     python scripts/query_estat.py --stats-data-id <id> --out /tmp/estat_<topic>.json
     ```

3. **Perplexity Sonar（出典付き市場リサーチ）**
   - 各 topic に対し、出典 URL を必ず返すクエリを実行：
     ```bash
     python scripts/query_perplexity.py \
       "<topic> の市場規模を、出典 URL 付きで教えてください。時間軸: <time_horizon>" \
       --model sonar --recency year --out /tmp/perplexity_<topic>.json
     ```
   - 高精度が必要なら `--model sonar-pro`

4. **credibility 評価**
   - 各回答の citations を `knowledge/credibility-rules.md` で評価
   - Tier D は除外し、`excluded_sources` に記録
   - Tier A・B のみ採用

5. **数値の裏取り**
   - 市場規模など重要数値は 2 ソース以上で照合
   - 大幅乖離（30%以上）があれば両方記録 + 理由を考察に書く

6. **結果保存**

```yaml
w2_market_research:
  status: done
  results:
    - topic: "国内デザインツール市場規模"
      time_horizon: "2024-2026"
      findings:
        - statement: "国内デザインツール市場は2024年に約540億円"
          source_url: "https://..."
          source_tier: A
          source_name: "矢野経済研究所"
          fetched_at: <ISO8601>
      confidence: high  # high | medium | low
  excluded_sources:
    - url: "https://example.com/blog"
      tier: D
      reason: "出典不明の個人ブログ、数値が他のソースと乖離"
```

## NG

- 出典 URL のない数値を採用する
- 単一ソースだけで重要数値を確定する
- AI 生成記事（Powered by AI 等の明示あり）を採用する
- Statista などの paywall コンテンツを違法に取得する（要約のみ採用可、出典明示）
