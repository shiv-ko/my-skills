# Codex Skills 日本語版

このリポジトリは、個人用Codex Skillの正本です。Skillをこのリポジトリで編集・検証・コミットし、各PCのCodex環境へインストールします。

## 収録Skill

| Skill | 概要 |
| --- | --- |
| `create-recurring-google-takeout-export` | Google Takeoutの定期エクスポートを作成 |
| `digest-kindle-highlights` | Kindleハイライトを知識ノートへ再構成 |
| `explain-diff-html` | コード差分を対話的HTMLで解説 |
| `explain-diff-markdown` | コード差分をMarkdownで解説 |
| `grill-me` | 計画や設計を徹底的に質問して検証 |
| `hallmark` | AIらしい凡庸さを避けたUI設計・監査・再設計 |
| `natural-japanese` | 仕事の日本語文書を自然で読みやすく作成・推敲 |
| `review-presentation` | PowerPointの論理・可読性・一貫性をレビュー |
| `sync-codex-claude` | CodexとClaude Codeの設定やSkillを意味的に同期 |

## インストール

すべてのSkillを新規インストールします。

```bash
./scripts/install.sh
```

特定のSkillだけを指定することもできます。

```bash
./scripts/install.sh grill-me review-presentation
```

既存のSkillがある場合は安全のため停止します。リポジトリ版で更新する場合は`--replace`を指定します。既存コピーは削除せず、タイムスタンプ付きのバックアップへ移動します。

```bash
./scripts/install.sh --replace grill-me
```

既定のインストール先は`${CODEX_HOME:-$HOME/.codex}/skills`です。

## 差分確認

リポジトリ版とインストール済みSkillを比較します。

```bash
./scripts/status.sh
```

## 運用方針

1. `skills/<name>/`を編集する。
2. Skillを検証する。
3. 変更をGitへコミットする。
4. `./scripts/install.sh --replace <name>`でCodex環境へ反映する。
5. 別のPCではclone後に`./scripts/install.sh`を実行する。

`~/.codex/skills`側を直接編集するとリポジトリと差分が生じます。原則として、このリポジトリを正本にしてください。

## ライセンス

`hallmark`と`natural-japanese`には、それぞれの元プロジェクトのMIT Licenseと著作権表示を同梱しています。それ以外のSkillに適用するリポジトリ共通ライセンスは、公開前に決定してください。

## 外部から取り込んだSkill

- `hallmark`: `Nutlope/hallmark`、基準commit `13ac0ec7e148655948100b6396439e481361d690`
- `natural-japanese`: `coji/natural-japanese`、基準commit `0f1cc1c5a4e2aa7590598c88a15c213a60d9545a`
