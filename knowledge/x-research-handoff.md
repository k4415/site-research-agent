# x-research-expert へのハンドオフ

既存の `x-research-expert` agent を `aachat session run` で起動し、VOC 調査を委譲する。

## 起動前チェック

```bash
aachat session list --project <project> --agent x-research-expert
```

該当 project に running session があれば：
- 同じ目的なら `session send` で追加依頼
- 異なる目的なら新規 `session run`（並行 session として扱われる）

## 依頼テンプレ

```bash
aachat session run x-research-expert.<owner> --project <project> "
目的: <case-id> の業界 VOC を X 上で調査

対象:
- キーワード: <requirements の research_needs.voc[].keyword から>
- 期間: 直近 3 ヶ月（適宜調整可）
- 言語: 日本語（必要なら英語も）
- 除外: 公式アカウントの宣伝投稿、ボット投稿

成果物:
- ファクトレポートを [[aachat/docs/<team>/<project>/research-x/<case-id>.md]] に保存
- 考察レポートを [[aachat/docs/<team>/<project>/research-x-insight/<case-id>.md]] に保存
- 投稿グループ・代表投稿・検索ログを既存テンプレ通りに

完了後:
- 上記 2 doc のリンクを返してください
- cases/<case-id>.md の children に追加してください
"
```

## x-research-expert の出力を取り込む

site-research-agent は x-research-expert の **ファクトレポート** だけを `research/<case-id>.md` に統合する。
考察レポート（research-x-insight）の内容は、自分の `research-insight/<case-id>.md` でも別途独自の VOC 解釈を加えて使う。

## 注意

- 同一目的の `/loop` セッションを重複起動しない（identity.md L61）
- ファクトレポートに仮説を混ぜない原則（identity.md L57）を尊重
- x-research-expert の出力は X 観察に限定。Web 全般の VOC が必要なら自分で `market-research` skill 内で実施
