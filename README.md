# commands_restart

Created: 2026-02-15
Updated: 2026-03-24 10:39

## 概要
`/restart` コマンドの処理をPythonで実行し、既存プロジェクトの再開を支援する。

## 目的
既存プロジェクトの環境整備・状態確認・書類チェックをPythonに委譲し、Claude側のトークン消費を最小化する。

## インストール方法
外部パッケージ不要（Python標準ライブラリのみ使用）。

## 使い方
```bash
# CLIモード（/restart コマンドから自動呼び出し）
python main.py --path "C:/Users/14506928/Projects/my-project"

# GUIモード（手動実行・フォルダ選択ダイアログ）
python main.py
```

## ディレクトリ構成・ファイル役割説明
```
commands_restart/
├── main.py             # メインスクリプト（CLI/GUIモード・環境整備・書類チェックの実体）
├── logger_config.py    # ログ設定モジュール
├── requirements.txt    # 依存パッケージ一覧（標準ライブラリのみのため空）
├── run.bat             # GUIモード起動用バッチ
├── README.md           # このファイル
├── CHANGELOG.md        # バージョン変更履歴
├── CLAUDE.md           # プロジェクト固有ルール（条例）
└── _logs/              # 実行ログ（gitignore対象）
```

## 設定ファイルの場所と用途

| ファイル | 用途 |
|---------|------|
| `../commands_start/_templates/` | 書類ひな型の参照先（commands_startと共有） |

## スクリプトの動作・引数の概要

### 動作（CLIモード）
1. 対象プロジェクトの `CLAUDE.md` から `project_type` を読み取る
2. `project_type` に応じて環境整備の内容を分岐する（詳細は下記）
3. `/start` で生成される全ファイルの存在チェック・不足分を自動作成
4. Git情報（ブランチ・未コミット変更・リモートURL）を収集
5. 書類（README.md・CHANGELOG.md）のセクション見出しを抽出
6. テンプレートと比較してClaudeに差異を報告するためJSONを出力
7. 表形式レポートを標準出力に表示・`_logs/` にログ保存

### project_type による分岐

対象プロジェクトの `CLAUDE.md` に以下の形式で記載する:

```
## プロジェクト種別
project_type: web
```

| project_type | `main.py` | `logger_config.py` |
|---|---|---|
| `python`（または未設定） | 生成する | 生成する |
| `web` | 生成しない | 生成しない |

種別の詳細・追加候補は書庫（`~/.claude/CLAUDE.ref.md`）の「プロジェクト種別」セクションを参照。

### 引数

| 引数 | 型 | デフォルト | 説明 |
|------|----|-----------|------|
| `--path` | str | なし（GUIモード） | 対象プロジェクトのパス |

## ライセンス
Private
