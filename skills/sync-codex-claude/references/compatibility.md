# Codex と Claude Code の互換性

## 目次

- [設計上の結論](#設計上の結論)
- [永続的な指示](#永続的な指示)
- [Skills](#skills)
- [エージェントとサブエージェント](#エージェントとサブエージェント)
- [推奨される共有レイアウト](#推奨される共有レイアウト)
- [公式ソース](#公式ソース)

## 設計上の結論

両製品とも `SKILL.md`、progressive disclosure(段階的開示)、再利用可能なリソースを備えたディレクトリベースの Agent Skills を実装している。しかし、永続的な instructions の発見方法、skill の配置場所、衝突ルール、呼び出し構文、拡張機能は異なる。ポータブルなコア + 製品アダプタという方式を使うこと。双方向の「最後に書き込んだ方が勝つ」というミラーリングは使わないこと。

## 永続的な指示

| 観点 | Codex | Claude Code | 同期上の結果 |
| --- | --- | --- | --- |
| 主要ファイル | `AGENTS.md`; ディレクトリ内では `AGENTS.override.md` が優先される | `CLAUDE.md`; プロジェクトファイルは `.claude/CLAUDE.md` でもよい; `CLAUDE.local.md` はローカル専用 | 共有ルールは意味的に変換し、ツール固有ファイルはそのまま保持する |
| ユーザースコープ | デフォルトは `~/.codex/AGENTS.md`; `CODEX_HOME` で上書き可能 | `~/.claude/CLAUDE.md`; `CLAUDE_CONFIG_DIR` で上書き可能 | 設定を解決する前にホームパスをハードコードしないこと |
| プロジェクトでの発見 | プロジェクトルートから CWD まで、各ディレクトリにつき最大1つの instructions ファイル | 起動時に祖先(ancestor)のファイルが読み込まれ、Claude がそのディレクトリで作業する際に子(descendant)のファイルが読み込まれる | ディレクトリスコープを保持すること。1つに平坦化したファイルにすると挙動が変わる |
| 上書き | より新しく、より局所的なガイダンスが以前のガイダンスを上書きする; ディレクトリ内では override ファイル名が優先される | より具体的なプロジェクトのコンテキストが後に現れる; 矛盾した文章は決定論的な強制力を持たない | 矛盾がある場合は、想定上の勝者を作り出すのではなくフラグを立てて報告する |
| 上限 | プロジェクト instructions の合計は既定で 32 KiB | ガイダンスはファイルごとに200行未満を目標とする; auto memory には別の上限がある | 常時読み込まれる共通ルールは小さく保ち、手順は skills に移す |
| 追加の仕組み | 設定可能なフォールバック instructions ファイル名 | `.claude/rules/`、imports、auto memory、hooks | 明示的に変換しない限り、これらは製品アダプタとして保持する |

## Skills

| 観点 | Codex | Claude Code | ポータブルにする方針 |
| --- | --- | --- | --- |
| プロジェクトパス | `.agents/skills/<name>/SKILL.md`; CWD からリポジトリルートに向かって探索される | `.claude/skills/<name>/SKILL.md`; ネストされた skill は必要に応じて現れる | 両方のパスを1つのポータブルな source から生成する |
| ユーザーパス | `~/.agents/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` | ユーザーの skills とリポジトリの skills は分離しておく |
| 最小限のメタデータ | Codex のドキュメントでは `name` と `description` が必須 | `description` が推奨される; ディレクトリ名が name の代わりになりうる | 共有コアには `name` と `description` の両方を含める |
| 呼び出し | `$skill-name`; `/skills` で選択画面が開く | `/skill-name` | 呼び出し構文を調整せずにそのまま同期しないこと |
| 自動使用 | description に基づく暗黙的な選択 | 無効化されていない限り、description に基づく暗黙的な選択 | 共有する description は両方の自動選択機構向けに書くこと |
| 追加メタデータ | 表示/依存関係用の任意の `agents/openai.yaml` | Claude 専用フィールドには、呼び出し制御、ツール制限、動的コンテキスト、subagent 実行などが含まれる | 拡張機能はそれぞれの対象アダプタ内にのみ保持する |
| 重複名 | 同名の skill はマージされず、両方が表示される場合がある | enterprise が personal を上書きし、personal が project を上書きする; ネストされたバリアントは修飾名の下で共存できる | 重複を検出し、明示的な決定を要求する |
| 動的コマンド | 引用されている Codex の skill 仕様には対応する仕組みが確立されていない | ``!`command` `` はコマンド出力を注入する; `$ARGUMENTS` や関連する置換がサポートされている | 無効な Markdown としてそのままコピーしないこと。ワークフローを書き直すか、非対応であると明記する |

ポータブルな skill のコンテンツは、`name`、`description`、通常の Markdown instructions、相対パスで参照される同梱リソースを持つ `SKILL.md` から成る。両方の公式仕様で確認が取れるまで、それ以外のすべての frontmatter フィールドは非ポータブルとして扱うこと。

## エージェントとサブエージェント

両製品とも専用の subagent をサポートしているが、そのスキーマとランタイムのセマンティクスは安定した一対一の形式ではない。Claude の定義には、ツールのリスト、禁止されたツール、モデル、権限モード、MCP サーバー、hooks、ターン数の制限、プリロードされる skill、永続的なメモリ、effort、バックグラウンドモード、分離(isolation)を含めることができる。Codex には独自の agent 設定とランタイムがある。意図は保守的に変換し、元の定義はアダプタとして保持すること。

Claude では、skill をプリロードすると、その全内容が起動時に subagent へ注入される。これは、subagent が skill を発見できるようにするだけの状態とは異なる。この違いを暗黙のうちに失わないこと。

## 推奨される共有レイアウト

1つのリポジトリが両方のツールに対応する必要がある場合は、中立的な著者側の source と、そこから生成される製品ビューを使用する:

```text
.agent-shared/
  instructions.md
  skills/<name>/
    SKILL.md
    references/
.agents/skills/<name>/       # 生成された Codex 用ビュー
.claude/skills/<name>/       # 生成された Claude 用ビュー
AGENTS.md                    # 共有コア + Codex アダプタ
CLAUDE.md                    # 共有コア + Claude アダプタ
```

生成先から再帰的に生成しないこと。各共有アイテムのコンテンツハッシュと宣言された所有者を含むマニフェストを保持する。以前に生成したハッシュとの三方比較を使うことで、同期処理が「source の更新」と「生成先への手動編集」を区別できるようにする。

## 公式ソース

- OpenAI, [Build skills](https://learn.chatgpt.com/docs/build-skills)
- OpenAI, [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- OpenAI, [Import from another agent](https://learn.chatgpt.com/docs/import)
- Anthropic, [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- Anthropic, [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- Anthropic, [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory)
- Anthropic, [Create custom subagents](https://code.claude.com/docs/en/sub-agents)

これらのページは時間の経過で内容が変わりうる。パス、優先順位、frontmatter、ランタイムの挙動に依存する変換を実装する前に、必ず再確認すること。
