# Competitor LP Extraction Schema

競合 LP / SaaS サイトから構造化抽出するスキーマ。Firecrawl `/scrape` JSON mode に渡す。

完全な JSON Schema は `scripts/extract_lp_schema.py` 内に実装。

## トップレベル構造

```json
{
  "meta": { "url", "company", "product_name", "category", "language", "fetched_at" },
  "hero": { "headline", "subhead", "primary_cta_text", "hero_visual_type", "awareness_level_target" },
  "value_proposition": { "core_promise", "icp_signals[]", "differentiators[]" },
  "problem_amplify": { "problems_listed[]", "pain_intensity_signals[]" },
  "benefits": [ { "label", "outcome", "feature_mapped" } ],
  "features": [ { "name", "description", "order_in_page" } ],
  "social_proof": {
    "logos[]",
    "testimonials": [ { "quote", "author", "role", "company" } ],
    "case_studies": [ { "company", "kpi_improvement", "summary" } ],
    "metrics_claimed[]",
    "media_mentions[]"
  },
  "pricing": {
    "plans": [ { "name", "price", "billing_cycle", "features_highlighted[]", "is_recommended" } ],
    "free_trial": bool,
    "freemium": bool
  },
  "ctas": [ { "text", "position": "hero|mid|sticky|footer", "type": "signup|demo|contact|download|trial" } ],
  "faq": [ { "question", "answer", "objection_category" } ],
  "narrative_structure": {
    "framework_match": "AIDA|PASTOR|PAS|StoryBrand|other",
    "section_order[]",
    "page_length_words"
  },
  "tech_signals": { "form_fields_count", "has_video", "has_chatbot", "analytics_tools_detected[]" }
}
```

## 各フィールドの埋め方

### hero.awareness_level_target

LP のファーストビューから Schwartz 5 段階のどれを狙っているか推定：
- `unaware`: 問題を提示するヘッダ
- `problem_aware`: 「こうなっていませんか？」共感ヘッダ
- `solution_aware`: カテゴリ名 + ベネフィット
- `product_aware`: 差別化 + USP
- `most_aware`: オファー + 緊急性

### value_proposition.differentiators

「他社にない独自要素」と読み取れる訴求。
推測ではなく、サイト本文に明示的に書かれている表現のみ。

### social_proof.metrics_claimed

「導入企業1000社」「制作時間70%削減」など数値主張。出典が明示されているかも記録。

### narrative_structure.framework_match

セクション順から該当フレームを判定。`knowledge/lp-frameworks.md` 参照。

### tech_signals

ページの実装ヒント（後続のサイト制作に役立つ）。form_fields_count は CV ハードルの目安。

## ノイズ除外ルール

抽出後、以下は事実レポートに採用しない：

- ヘッダ・フッタの汎用ナビゲーション
- クッキー同意・プライバシーバナー
- 「お知らせ」「ニュース」など更新ストリーム
- ボイラープレート（コピーライト、特商法）
