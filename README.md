# commands_restart

## 概要
`/restart` カスタムコマンドの処理をPythonで実行する支援ツール。
既存プロジェクトの再開時に環境整備・状態確認を自動化する。

## 機能

### CLIモード（`--path` 引数あり）
`/restart` コマンドからClaudeが呼び出す。以下を自動実行する：

1. **環境整備**（不足していれば自動作成）
   - `.venv` 仮想環境
   - `run.bat` 実行用バッチファイル
   - `.vscode/launch.json` VS Code仮想環境デバッグ設定
   - `main` ブランチの場合 → `develop` に自動切り替え

2. **表形式レポートを標準出力に表示**
   - 環境整備の結果（既存 / 新規作成）
   - ブランチ・未コミット変更・リモートURL

3. **`_logs/` にログファイルを保存**
   - ファイル名: `restart_YYYYMMDD_HHMMSS.log`

4. **ClaudeへのJSON出力**（`---JSON---` 区切り）
   - CLAUDE.mdの内容をClaudeが読み取るために使用

### GUIモード（引数なし）
フォルダ選択ダイアログを表示し、選んだプロジェクトで環境整備を実行してVS Codeで開く。

## セットアップ
外部パッケージ不要（Python標準ライブラリのみ使用）。

## 使い方
```bash
# CLIモード（/restart コマンドから自動呼び出し）
python main.py --path "C:/Users/14506928/Projects/my-project"

# GUIモード（手動実行）
python main.py
```

Created: 2026-02-15
Updated: 2026-02-24 16:26

## バージョン履歴
- **v0.2.0** (2026-02-24): 環境整備の自動化・表形式レポート出力・ログ保存・developブランチ自動切り替えを追加
- **v0.1.1** (2026-02-16): ログ出力フォルダを _logs に統一
- **v0.1.0** (2026-02-15): 初回リリース

## 注意事項
【環境依存情報】2026年2月時点のPC環境に依存
PC引っ越し時の要修正箇所:
- `VSCODE_PATH`: VS Codeのインストールパス（現在は `C:\Users\14506928\...` に固定）
  → 新PC環境に合わせてフルパスを修正してください（`main.py` 内の定数）

## ファイル構成
```
commands_restart/
├── .gitignore
├── CLAUDE.md
├── README.md
├── _logs/         # 実行ログの保存先
├── main.py
└── requirements.txt
```
