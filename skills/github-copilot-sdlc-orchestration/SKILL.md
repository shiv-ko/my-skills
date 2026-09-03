---
name: github-copilot-sdlc-orchestration
description: GitHub Copilotのcustom agentsとagent skillsを使い、Issue整理、計画、テスト、実装、独立レビュー、PR準備を役割分離した開発フローとしてリポジトリへ導入・改善する。`.github/agents`、`.github/skills`、`AGENTS.md`の作成や、既存のCopilotオーケストレーションの見直しを依頼された場合に使用する。
---

# GitHub Copilot SDLC オーケストレーション

GitHub Copilot向けの開発フローを、権限を絞ったcustom agentと再利用可能なskillに分けて構成する。

## 方針

- `agent.md`には役割、入力、出力、利用可能なツール、禁止事項だけを置く。
- 詳細な作業手順は対応する`SKILL.md`へ置き、agentから相対リンクで参照する。
- 工程間の受け渡しは会話だけに依存せず、`docs/development/issues/<task-id>/`の成果物へ残す。
- 計画者、テスト担当、実装者、レビュー担当を分離する。ただし、テスト作成に価値がない変更へ新規テストを強制しない。
- 共有リポジトリへ影響する操作と、仕様・設計の未決事項には人間の判断点を設ける。

設計根拠を説明するとき、または構成を変更するときは[調査と設計判断](references/research-and-rationale.md)を読む。

## 導入手順

1. 対象リポジトリの`AGENTS.md`、`.github/copilot-instructions.md`、`.github/agents`、`.github/skills`、ビルド・テスト設定を確認する。
2. [assets/template](assets/template)を基に、対象リポジトリへ必要なファイルだけを追加する。
3. 既存ファイルと同名のものがあれば上書きしない。責務、権限、成果物契約の差分を示し、既存設計を保った最小変更として統合する。
4. `AGENTS.md`にはリポジトリ固有の正しいコマンド、変更禁止領域、アーキテクチャ上の制約を追記する。推測したコマンドを書かない。
5. 各agentの`tools`を実際のCopilot環境で利用できる名前へ合わせる。読み取り担当へ不要な編集権限を与えない。
6. agentからskillへの相対リンク、skill名と親ディレクトリ名、YAML frontmatterを検証する。
7. VS Codeの「Chat: Open Customizations」またはChat Diagnosticsで読み込みエラーがないことを確認するよう案内する。

## テンプレートの構成

```text
AGENTS.md
.github/
├── agents/
│   ├── orchestrator.agent.md
│   ├── issue.agent.md
│   ├── plan.agent.md
│   ├── plan-review.agent.md
│   ├── test.agent.md
│   ├── implement.agent.md
│   ├── review.agent.md
│   └── pr.agent.md
└── skills/
    ├── issue-refinement/SKILL.md
    ├── implementation-planning/SKILL.md
    ├── plan-review/SKILL.md
    ├── test-first-change/SKILL.md
    ├── planned-implementation/SKILL.md
    ├── code-change-review/SKILL.md
    └── pull-request-preparation/SKILL.md
```

## 導入後の確認

- オーケストレーターだけが通常のagent pickerに表示される。
- worker agentはサブエージェントとして呼び出せる。
- planとreviewのagentはプロダクションコードを編集できない。
- test agentはプロダクションコードを、implement agentは原則としてテストを変更しない。
- テスト失敗、未解消の`[blocker]`、仕様の曖昧さがある状態でPR作成へ進まない。
- `git push`、Issue・PR作成などの外部変更は、ユーザーの明示的な承認後に限る。

## 適応の基準

- 小規模なドキュメント変更や機械的変更では、テスト工程を「既存検証の実行」に縮退してよい。
- DB移行、認可、課金、公開API、並行処理を含む変更では、計画とレビューの観点を追加し、人間の承認点を増やす。
- monorepoでは、共通ルールをルート`AGENTS.md`、領域固有のルールをnested `AGENTS.md`またはpath-specific instructionsへ分ける。nested `AGENTS.md`はVS Codeで実験的機能である点を伝える。
- モデル名はテンプレートへ固定しない。利用環境の既定値を継承し、評価結果がある場合だけ固定する。
