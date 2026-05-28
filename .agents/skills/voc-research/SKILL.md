---
name: voc-research
description: X 上の VOC を既存 x-research-expert に委譲して取得。「VOC調査」「X調査」などのトリガーで起動。
---

# voc-research

research-plan の W3 ワークストリーム。X 上の VOC を既存 `x-research-expert` agent に委譲する。

## いつ起動するか

- `research-plan` skill から並列起動される
- 単独で「<キーワード>の X 上の VOC を調べて」と依頼された時

## 実行手順

1. **research_needs.voc を読む**
   - 各エントリの keyword と media、reason、priority を確認
   - media が `x` のものだけを処理（他媒体は将来拡張）

2. **既存 session の重複チェック**
   ```bash
   aachat session list --project <project> --agent x-research-expert
   ```
   - 同 project に running session があれば判断：同じ目的なら `session send`、別目的なら新規 `session run`

3. **x-research-expert を起動**
   `knowledge/x-research-handoff.md` のテンプレに従う：
   ```bash
   aachat session run x-research-expert.<owner> --project <project> "
   目的: <case-id> の業界 VOC を X 上で調査

   対象:
   - キーワード: <list from research_needs.voc>
   - 期間: 直近 3 ヶ月
   - 言語: 日本語
   - 除外: 公式アカウントの宣伝投稿、ボット投稿

   成果物:
   - ファクトレポート: [[aachat/docs/<team>/<project>/research-x/<case-id>.md]]
   - 考察レポート: [[aachat/docs/<team>/<project>/research-x-insight/<case-id>.md]]

   完了したら cases/<case-id>.md の children に追加してください。
   "
   ```

4. **完了待ち**
   - x-research-expert からのファクトレポート保存通知を待つ
   - タイムアウト（仮 60 分）したら orchestrator に通知

5. **ファクトレポートを取り込む**
   - `research-x/<case-id>.md` を読む
   - 投稿グループ・代表投稿を VOC 観察事項として `research/<case-id>.md` に統合できる形に整える

6. **結果記録**

```yaml
w3_voc_research:
  status: done
  delegated_to: x-research-expert
  session_id: <x-research-expert の session-id>
  reports:
    - "../research-x/<case-id>.md"
    - "../research-x-insight/<case-id>.md"
  highlights:
    - observation: "<生の投稿引用>"
      group: "#group-3"
      post_id: "#post-12"
      relevance: "<どのリサーチ論点に関係するか>"
```

## NG

- x-research-expert の出力を勝手に意訳する
- 同一 project / 同一目的の session を重複起動
- ファクトレポートと考察レポートを混ぜて読む
