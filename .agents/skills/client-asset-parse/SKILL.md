---
name: client-asset-parse
description: クライアント提供資料（既存サイト・提案資料・商品資料）を読んで構造化。「資料解析」「提供資料を読む」などのトリガーで起動。
---

# client-asset-parse

research-plan の W4 ワークストリーム。クライアント提供資料を読み、構造化する。

## いつ起動するか

- `research-plan` skill から並列起動される
- 単独で「クライアント提供の<URL/PDF>を解析」と依頼された時

## 入力

クライアント提供資料は以下のいずれかの形で渡される：

- 既存サイト URL（クライアントの現サイト）
- PDF / Word / テキスト
- aachat shared doc（クライアントが書いてくれたもの）
- スプレッドシート（商品リスト・価格表など）

## 実行手順

1. **資料リストを把握**
   - hearing doc の「既存素材」「参考資料」セクションを確認
   - 案件ハブ doc の `children` に追加されている資料 doc

2. **資料種別ごとに処理**

   ### URL の場合
   ```bash
   python scripts/fetch_lp.py <url> --mode auto --out /tmp/asset_<i>.json
   ```

   ### PDF の場合
   ```python
   import pypdf  # or pdfplumber
   reader = pypdf.PdfReader("path/to/file.pdf")
   text = "\n".join(p.extract_text() for p in reader.pages)
   ```

   ### shared doc の場合
   - 直接 Markdown を読む

3. **構造化抽出**
   - 既存サイトなら `extraction-schema.md` 準拠で抽出
   - 商品資料なら以下を抽出：
     - 商品名 / カテゴリ
     - 価格 / プラン
     - 機能 / スペック
     - ターゲット記述
     - 既存のコピー文（後続制作で参考になる）

4. **クライアントの公式記述として最優先**
   - 競合分析や Perplexity の出力と矛盾があった場合、クライアント公式記述を優先
   - 矛盾は考察レポートに「他社情報との差異」として明示

5. **結果記録**

```yaml
w4_client_asset_parse:
  status: done
  assets_parsed:
    - source: "https://client-existing-site.com/"
      type: existing_website
      extracted: { ... }  # extraction-schema 準拠
    - source: "client-pricing.pdf"
      type: pricing_pdf
      extracted:
        plans: [...]
        notes: "..."
```

## NG

- 提供資料の数値・固有名詞を意訳・改変する
- 機密情報（売上数値など）を考察レポートに不必要に出す
- secret / token / 内部 URL を doc に書く
