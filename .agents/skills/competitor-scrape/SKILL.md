---
name: competitor-scrape
description: 競合 LP を取得し、knowledge/extraction-schema.md 準拠で構造化抽出する。「競合分析」「LP取得」などのトリガーで起動。
---

# competitor-scrape

research-plan の W1 ワークストリーム。競合 LP を取得・抽出する。

## いつ起動するか

- `research-plan` skill から並列起動される
- 単独で「<URL> の競合分析」と依頼された時

## 実行手順

1. **対象 URL の決定**
   - research_needs.competitors を全件処理
   - `discover: true` のものは Perplexity Sonar で発見クエリ：
     ```
     「<カテゴリ名> 主要プレイヤー <地域>」
     ```
     出典 URL から候補を抽出

2. **各 URL を取得**
   ```bash
   python scripts/fetch_lp.py <url> --mode auto --out /tmp/lp_<i>.json
   ```
   - 自動で Jina → Firecrawl の順に試す
   - 取得失敗は `failed_fetches` に理由付きで記録

3. **構造化抽出**
   ```bash
   python scripts/extract_lp_schema.py <url> --out /tmp/extract_<i>.json
   ```
   - Firecrawl JSON mode でスキーマ準拠抽出

4. **narrative_structure の判定**
   - `knowledge/lp-frameworks.md` のアルゴリズムを適用
   - framework_match を確定

5. **awareness_level_target の推定**
   - hero セクションの文言から `knowledge/awareness-level-guide.md`（hearing-agent の knowledge を参照）の判定基準を適用

6. **ノイズ除外**
   - `knowledge/extraction-schema.md` のノイズ除外ルールに従う
   - クッキー同意・フッタ等を取り除く

7. **結果保存**
   - 各競合の抽出結果を `research-plan/<case-id>.md` の workstream 配下に追記
   - 取得失敗・除外理由も明示

## 出力フォーマット

```yaml
w1_competitor_scrape:
  status: done
  results:
    - name: "Canva"
      url: "https://www.canva.com/ja_jp/"
      extracted: { ... }  # extraction-schema 準拠 JSON
      fetched_at: <ISO8601>
      tool_used: jina_reader  # or firecrawl
  failed_fetches:
    - url: "https://example.com"
      reason: "403 Forbidden（Bot 検知）"
```

## NG

- スクレイピングの失敗を黙る（必ず failed_fetches に記録）
- 抽出結果に推測を混ぜる（サイトに書かれていないことを書かない）
- robots.txt 違反の強行
