# Agent Skills監査チェックリスト

## 目次

- [棚卸し表](#棚卸し表)
- [重複判定](#重複判定)
- [日本語化の同等性](#日本語化の同等性)
- [公開前検査](#公開前検査)
- [完了報告](#完了報告)

## 棚卸し表

Skillごとに次の列を埋める。

| 列 | 内容 |
| --- | --- |
| name | frontmatterまたはディレクトリから解決した英語名 |
| path | 絶対パス |
| scope | user / project / repository / cache |
| product | Codex / Claude / OpenSkills / other |
| source | 上流URL、subpath、基準commit |
| license | ライセンス名、著作権者、NOTICEの有無 |
| resources | references / scripts / assets / agents |
| link | real directory / symlink / broken link |
| git | tracked / modified / untracked / outside repository |
| decision | unique / identical / diverged / convertible / non-skill / blocked |

## 重複判定

1. `name`だけで同一と判断しない。
2. `description`、本文、参照ファイル、スクリプト、アセットを比較する。
3. 改行、表示用メタデータ、翻訳だけの差分と、実行挙動の差分を分ける。
4. 更新時刻ではなく、Git履歴、上流commit、所有者の宣言を優先する。
5. 両方に独立した実質変更があれば競合として止める。

## 日本語化の同等性

- トリガーとなる依頼例が減っていない。
- MUST、NEVER、必須、禁止などの強度が維持されている。
- 実行順序、停止条件、例外処理、検証条件が維持されている。
- コマンド、引数、ファイル名、相対パスが壊れていない。
- 製品固有機能を、対応しているかのように誤記していない。
- 省略したフィールドの挙動を本文またはアダプタで補っている。

## 公開前検査

- LICENSE、著作権表示、NOTICEが揃っている。
- 上流URLと基準commitを記録している。
- APIキー、token、メールアドレス、個人の絶対パスを含まない。
- サンプルデータに個人情報を含まない。
- 相対リンクがすべて解決する。
- validatorが成功する。
- 代表スクリプトの実行結果を確認している。
- `git diff --check`が成功する。
- 無関係なdirty変更をstageしていない。
- public remoteへのpushが明示的に許可されている。

## 完了報告

```text
正本:
導入先:
追加:
既存版を維持:
競合:
非Skillとして除外:
ライセンス・出典:
検証:
コミット:
公開状態:
未解決事項:
```
