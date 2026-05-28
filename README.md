# site-research-agent

サイト制作向け専用のリサーチ agent。競合LP・市場・VOC・クライアント提供資料を並列で調査し、事実レポートと考察レポートを分離して出力する。

## できること

- requirements doc の `research_needs` に従って 4 つの情報源を並列リサーチ
  - 競合LPスクレイピング（Jina Reader → Firecrawl JSON mode）
  - 市場リサーチ（Perplexity Sonar + e-Stat API）
  - VOC（既存 x-research-expert を `aachat session run` で起動）
  - クライアント提供資料解析
- 事実レポート `research/<case-id>.md` と考察レポート `research-insight/<case-id>.md` を分離保存
- ノイズ・取得失敗・credibility 低い情報は除外、理由を明示
- 「次に試すべき追加リサーチ」を `followup_research` に残す

## 使い方

通常は `site-strategy-orchestrator` から起動される。

```bash
aachat session run site-research-agent --project <project> --via claude-code "
要件定義に従ってリサーチを実行。
context:
- 案件ハブ: [[aachat/docs/<team>/<project>/cases/<case-id>.md]]
- 要件: [[aachat/docs/<team>/<project>/requirements/<case-id>.md]]
"
```

## 構成

- `identity.md` / `environment.yaml`
- `knowledge/extraction-schema.md` — 競合LP抽出スキーマ
- `knowledge/lp-frameworks.md` — AIDA/PASTOR/PAS/StoryBrand の判定
- `knowledge/credibility-rules.md` — ソース信頼度評価
- `knowledge/x-research-handoff.md` — x-research-expert への依頼
- `knowledge/tools-playbook.md` — Jina/Firecrawl/Perplexity の使い分け
- `scripts/fetch_lp.py` — LP 取得（Jina/Firecrawl 切替）
- `scripts/extract_lp_schema.py` — 構造化抽出
- `scripts/query_perplexity.py` — Perplexity Sonar
- `scripts/query_estat.py` — e-Stat API
- `.agents/skills/research-plan` — 4 並列タスク分解
- `.agents/skills/competitor-scrape` — 競合LP取得+抽出
- `.agents/skills/market-research` — 市場・業界リサーチ
- `.agents/skills/voc-research` — x-research-expert 委譲
- `.agents/skills/client-asset-parse` — 提供資料解析
- `.agents/skills/synthesize-research` — 事実/考察分離レポート化

## 設計ドキュメント

[[aachat/docs/agent-development/site-creation-suite/specs/site-research-agent.md]]

## 必要な env

`environment.yaml` の `config.env[]` で宣言。値は `~/aachat/.state/env.toml` か Infisical へ：

- `FIRECRAWL_API_KEY`: Firecrawl `/scrape` と `/extract`
- `PERPLEXITY_API_KEY`: Perplexity Sonar API
- `ESTAT_APP_ID`: e-Stat 統計表 API
- `JINA_API_KEY`: Jina Reader 有料枠（任意。無料 20req/分なら不要）

## 注意

- スクレイピング対象の robots.txt と ToS を尊重
- credibility が低い情報源（個人ブログ・出典不明レポート）は採用せず、その判断を `excluded_sources` に明示
- secret は repo に含めない
