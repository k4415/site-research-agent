# LP Frameworks

LP の narrative_structure を判定するためのフレームワークリファレンス。

## AIDA

Attention → Interest → Desire → Action

- セクション順: hero（注目）→ problem/curiosity（興味）→ benefits/proof（欲求）→ CTA
- LP 全般で最も多い古典的構成
- 短尺〜中尺 LP 向き

## PASTOR

Problem → Amplify → Story → Transformation → Offer → Response

- セクション順: problem → 痛みの拡大 → ストーリー（事例） → 変化 → オファー → CTA
- B2C・健康・自己啓発系で多い
- 長尺セールスレターに近い

## PAS

Problem → Agitate → Solution

- セクション順: problem → 痛みを増幅 → 解決策提示
- 短尺の広告 LP で多い
- 即時 CV 訴求向き

## StoryBrand (Donald Miller)

Character → Problem → Guide → Plan → Action → Failure/Success

- 顧客を主人公、ブランドをガイドに据える
- B2B SaaS で増えている
- 「失敗の代償」と「成功の姿」を両方提示

## SaaS 王道構成（フレーム外）

Hero → Social proof strip → Problem → Solution overview → Benefits → Features → How it works → Case studies → Pricing → FAQ → Final CTA

- 上記フレームの混合
- Outcome-first（数値成果を benefits で前出し）が 2026 年のデファクト

## 判定アルゴリズム（簡易）

1. ファーストビューに数値訴求 → SaaS 王道
2. 第 2 セクションが problem/agitate → PAS or PASTOR
3. 第 2 セクションが social proof strip → SaaS 王道
4. 全体に「キャラクター視点」のストーリー → StoryBrand
5. 上記すべて該当しない → AIDA（default）

`narrative_structure.framework_match` に上記いずれかを書く。判定が曖昧なら `other` + メモ。
