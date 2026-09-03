# 調査と設計判断

調査日: 2026-09-03

## 仕様上の前提

- GitHub Copilotのcustom agentは`.github/agents`へ置き、YAML frontmatterで`tools`、`user-invocable`、`disable-model-invocation`などを指定できる。[GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- VS Codeではcustom agentから別のcustom agentをsubagentとして呼び出せる。`handoffs`は人が工程を切り替えるUIであり、GitHub.com上のCopilot cloud agentでは無視されるため、このテンプレートの自動進行はsubagent委譲を中心にした。[VS Code Docs](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- Agent Skillsは`.github/skills/<skill-name>/SKILL.md`へ置き、必要なときだけ読み込ませられる。skill名は親ディレクトリ名と一致させる。[GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)、[VS Code Docs](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- `AGENTS.md`は複数のAIツールで共有する常設ルールに向く。タスク固有の手順はskill、役割と権限はcustom agentへ置く。[GitHub customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

## 論文から採用した点

### 役割は分けるが、成果物の契約を共通化する

AgentCoderはprogrammer、test designer、test executorを分離し、実行結果をprogrammerへ返す構成で、HumanEvalとMBPPにおけるコード生成性能の向上を報告した。[AgentCoder](https://arxiv.org/abs/2312.13010)

ChatDevは設計、実装、テストの専門agentを連鎖させ、自然言語とプログラム上のフィードバックを工程間の共通媒体として使った。[ChatDev](https://arxiv.org/abs/2307.07924)

このテンプレートでは、会話の要約だけでなく`requirements.md`、`plan.md`、各種evidenceを引き渡す。agentごとに自由な報告形式を許すより、次工程が検証可能な最低限の契約を置く。

### テストは要件を固定するために使い、件数を目的にしない

関数レベルの課題では、テストを問題文と一緒に与えることでLLMの正答率が上がるとの報告がある。[Test-Driven Development for Code Generation](https://arxiv.org/abs/2402.13521)

一方、リポジトリレベルのSWE-bench Verifiedを対象にした2026年のプレプリントでは、agentへ新規テスト作成を促しても解決率の有意な改善は見られず、API呼び出しや出力tokenが増える場合があった。生成テストはassertionより観測用printに偏る傾向も報告された。[Rethinking the Value of Agent-Generated Tests](https://arxiv.org/abs/2602.07900)

このためtest agentには、既存の人手テストを優先し、新規テストを受け入れ条件へ対応付け、意図した理由で失敗することを確認させる。ドキュメントや機械的設定変更では、新規テストを作らず既存検証で済ませられる。

### ツールと出力の設計もagent性能の一部として扱う

SWE-agentは、リポジトリ探索、編集、テスト実行に適したagent-computer interfaceが性能へ大きく影響すると報告した。[SWE-agent](https://arxiv.org/abs/2405.15793)

このテンプレートでは、agentごとのツールを最小化し、レビュー対象の変更、テスト編集、実装編集、外部操作を分離する。reviewerの編集対象は`review.md`だけに制限し、誤操作を起こしにくい操作面を優先する。

## 元記事から変更した点

[元のQiita記事](https://qiita.com/shivvvvvv/items/c84bee4af0b2c9ff640e)のIssue→計画→計画レビュー→実装→レビュー→PRという骨格を保ちつつ、次を変更した。

1. `test`と`implement`を分離した。
2. reviewerはplanやcodeを直接修正せず、findingを成果物へ書く。修正責任はplanまたはimplementへ戻す。
3. 各工程に入力、出力、完了条件を定義した。
4. テスト作成を常時必須にせず、変更に応じてvalidation-onlyを許可した。
5. model名を固定せず、環境の既定値を使う。
6. PR本文の準備と、push・PR作成という外部変更を別の承認点にした。

## 運用上の限界

- agentを分けても、同じモデルが同じ誤解を共有する可能性は残る。高リスク変更は人間の設計・テスト・セキュリティレビューを省略しない。
- skillやagentの指示は確率的に解釈される。絶対に守る必要がある検査はCIやhooksで決定的に強制する。
- 生成されたテストが仕様そのものではない。Issueの受け入れ条件、人間が管理する既存テスト、公開契約との矛盾があれば停止する。
