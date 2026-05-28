---
name: synthesize-research
description: 4 並列タスクの結果を統合し、事実レポートと考察レポートを分離して保存。「リサーチ統合」「synthesize」などのトリガーで起動。
---

# synthesize-research

W1〜W4 が全完了した時、`research/<case-id>.md`（事実）と `research-insight/<case-id>.md`（考察）に分離して保存する。

## いつ起動するか

- `research-plan` の 4 ワークストリームが全 done になった時
- 一部失敗でもエスカレーション後の判断で「現状で synthesize」と決まった時

## 出力 1: research/<case-id>.md（事実レポート）

x-research-expert と同じ「事実だけ」原則。評価語・推測 NG。

```yaml
---
title: "<案件名> リサーチ事実レポート"
status: done
case_id: <case-id>
sources_used:
  - { type: web, tool: jina_reader, urls: [...] }
  - { type: web, tool: firecrawl, urls: [...] }
  - { type: x, tool: x-research-expert, session_id: "<id>", reports: ["../research-x/<case-id>.md"] }
  - { type: market, tool: perplexity_sonar, queries: [...] }
  - { type: estat, tool: estat_api, queries: [...] }
quality_notes:
  - "競合A社はJSレンダリングが重く、Firecrawl にfallback"
excluded_sources:
  - { url: "...", tier: D, reason: "..." }
failed_fetches:
  - { url: "...", reason: "..." }
last_updated: <ISO8601>
---

# 1. 競合 LP 構造化抽出（事実）

## 1.1 競合A: <URL>
<extraction-schema 準拠の主要フィールドを Markdown 化>

### Hero
- Headline: "<原文>"
- Subhead: "<原文>"
- Primary CTA: "<原文>"
- 推定 awareness_level_target: solution_aware

### Value proposition
- Core promise: "..."
- Differentiators: [...]

### Social proof
- Logos: [...]
- Testimonials:
  - "<引用>" — <author>, <role>, <company>
- Metrics claimed: [...]

### Pricing
| プラン | 価格 | 推奨 |
|---|---|---|
| Free | ¥0 | - |
| Pro | ¥1,500/月 | ✓ |

### Narrative structure
- Framework match: SaaS_default
- Section order: [hero, social_proof_strip, problem, ...]

## 1.2 競合B: <URL>
...

# 2. 市場・業界事実

## 2.1 市場規模
- 国内デザインツール市場: 約540億円（2024年）
  - 出典: 矢野経済研究所「2024年版 デザインツール市場の現状と展望」
  - URL: https://...
  - tier: A
  - 取得日: 2026-05-28

## 2.2 業界トレンド
- AI 制作ツール導入率（広告代理店）: ... 
  - 出典: ...

# 3. VOC（X 経由、x-research-expert ファクトレポートから）

## 3.1 観察された不満
- "[user_X] 「AIで作ったバナー、結局手で直してる」" — #post-12（#group-3）
- ...

## 3.2 観察された期待
- ...

# 4. クライアント提供資料の抽出

## 4.1 既存サイト
...

## 4.2 商品資料
...

# 5. 取得失敗・除外

## 5.1 失敗した取得
...

## 5.2 除外したソース（理由付き）
...
```

## 出力 2: research-insight/<case-id>.md（考察レポート）

事実レポートの引用 ID を必ず付ける。

```yaml
---
title: "<案件名> リサーチ考察"
status: done
case_id: <case-id>
based_on: "../research/<case-id>.md"
last_updated: <ISO8601>
---

# 1. 推奨ポジショニング

## 1.1 Competitive alternatives
- 内製チーム（事実: hearing G ブロック）
- 競合A社（事実: research/<case-id>.md §1.1）
- 競合B社（事実: research/<case-id>.md §1.2）

## 1.2 Unique attributes（要件・リサーチから抽出）
- <unique attribute 1>
  - 根拠: 競合A・Bともに該当機能を持たない（research §1.1, §1.2）
- <unique attribute 2>
  - 根拠: VOC で「<X>が無いことへの不満」を観察（research §3.1）

## 1.3 Market category（推奨）
- "<新カテゴリ名>"
  - 根拠: 競合の category 表記は <既存カテゴリ> だが、本案件は <差別化要素> がある（research §1）

# 2. 推奨意識レベル設定

## 2.1 主ターゲット意識レベル
- solution_aware
  - 根拠1: hearing で「お客さんは AI ツールがあるのは知ってる」（hearing C ブロック）
  - 根拠2: 競合 A・B が共に「カテゴリ名 + ベネフィット」の hero（research §1.1.hero, §1.2.hero）
  - 信頼度: high

## 2.2 副ターゲット意識レベル
- problem_aware（少数だが想定）
  - 別 CTA / 別セクションで対応推奨

# 3. 推奨 LP/サイト構成

## 3.1 推奨セクション順
1. hero（推奨 headline tone: カテゴリ名 + Outcome 数値）
2. social_proof_strip（ロゴ 3〜5 社、研究: 競合A・Bともに採用）
3. problem
4. solution_overview
5. benefits（Outcome → Benefit → Feature の 3 層、研究: §2.4）
6. features
7. case_studies（研究: §1.1, §1.2 ともに重視）
8. pricing
9. faq
10. final_cta

## 3.2 推奨 Hero
- Headline 方向性: "<具体提案>"
  - 根拠: VOC §3.1 で観察された "<生の言葉>" を起点
- Visual: <product_screenshot 推奨など>

# 4. 推奨 RTB（Reason to Believe）候補

- <数値主張1>（クライアント側で公表可能か要確認）
- <数値主張2>
- <第三者評価>

# 5. リスク・反証可能性

- 競合A は近日 <機能 X> を発表しており、本案件の unique_attributes が侵食される可能性
- 市場規模数値はソース間で <30%> の乖離あり、要追加調査

# 6. 仮説・次論点（followup_research）

- <さらに調べた方が良いこと>
- <別アングルでのリサーチが効きそうな論点>
```

## 実行手順

1. **W1〜W4 の結果を読む**（research-plan/<case-id>.md から）

2. **事実レポートを組み立てる**
   - 取得した raw data を整形して保存
   - 評価語・推測を混ぜない

3. **考察レポートを組み立てる**
   - 事実レポートの該当 § を必ず引用
   - クライアント像・hearing の生の言葉も根拠として引用可

4. **保存**
   - `research/<case-id>.md` と `research-insight/<case-id>.md` を `status: done` で保存
   - case ハブ doc の `status: drafting_brief`、`assignee: site-brief-agent` に更新
   - case ハブ doc の `children` に 2 doc を追加

5. **次フェーズへハンドオフ**
   - orchestrator に通知 → orchestrator が site-brief-agent を session run で起動

## NG

- 事実レポートに評価語（「優良」「狙い目」「強い」）を入れる
- 考察レポートで事実レポートにない情報を持ち出す
- 単一ソースだけで結論する
- 取得失敗を隠す
