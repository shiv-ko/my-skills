---
name: pull-request-preparation
description: 検証済みの変更からPRタイトル、本文、Issueとの対応、テスト証拠、リスク、ロールバック情報を準備し、承認後だけbranch・commit・push・PR操作を行う。開発フローの最終工程に使う。
---

# Pull request preparation

## 準備

1. `requirements.md`から`review.md`までを読み、未解消の`[blocker]`と失敗中の必須検証がないことを確認する。
2. git statusと比較対象との差分を確認し、task外の変更が混ざっていないか調べる。
3. PRタイトルと本文案を`pr-artifacts.md`へ保存する。
4. 未実行検証、既知の制約、migration・rollout・rollback、follow-upを隠さず記載する。

## PR本文の最低要素

```markdown
## Summary
## Why
## Changes
## Acceptance criteria
## Verification
## Risks and rollback
## Related issue
```

## 外部操作

branch作成、commit、push、Issue更新、PR作成、merge、releaseは準備とは別の操作である。実行対象と予定内容を示し、ユーザーが明示的に承認した操作だけを行う。CIが失敗した場合は原因を報告し、無関係な変更で迂回しない。
