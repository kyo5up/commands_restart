# commands_restart

## 概要
commands_restart - 既存プロジェクトの再開支援ツール

## セットアップ
外部パッケージ不要（Python標準ライブラリのみ使用）。

## 使い方
```bash
python main.py
```

Created: 2026-02-15
Updated: 2026-02-16 14:40

## バージョン履歴
- **v0.1.1** (2026-02-16): ログ出力フォルダを _logs に統一、既存の logs フォルダをリネーム
- **v0.1.0** (2026-02-15): 初回リリース

【環境依存情報】2026年2月時点のPC環境に依存
PC引っ越し時の要修正箇所:
- VSCODE_PATH: VS Codeのインストールパス（現在は C:\Users\14506928\... に固定）
  → 新PC環境に合わせてフルパスを修正してください

## ファイル構成
```
commands_restart/
├── .gitignore
├── CLAUDE.md
├── README.md
├── logger_config.py
├── main.py
└── requirements.txt
```
