# commands_restart

既存プロジェクトの再開を支援するツール

## 概要

Claude Code の `/restart` スキルと連携し、既存プロジェクトの状態を素早く把握して作業を再開できるようにします。

**バージョン**: v0.1.0

## 機能

### 1. LLM経由実行（`/restart` スキル）
プロジェクト情報をJSON形式で出力し、LLMが解釈して次のアクションを提案します。

**収集する情報:**
- Git情報（ブランチ、未コミット変更、最近のコミット5件）
- 環境情報（.venv, requirements.txt, CLAUDE.md の有無）
- CLAUDE.mdの内容

### 2. 手動実行（対話モード）
Windowsエクスプローラーでフォルダを選択し、VSCodeで開きます。

## 使い方

### パターン1: Claude Code経由（推奨）
```bash
/restart
```
カレントディレクトリの情報を収集してLLMが解釈します。

### パターン2: 手動実行
```bash
python C:/Users/14506928/Projects/00_assistants/commands_restart/main.py
```
エクスプローラーが開き、フォルダを選択 → VSCodeで開きます。

### パターン3: 直接パス指定
```bash
python main.py --path "C:/Users/14506928/Projects/my_project"
```

## 出力例

```json
{
  "success": true,
  "project_path": "C:/Users/14506928/Projects/my_project",
  "project_name": "my_project",
  "git": {
    "is_git_repo": true,
    "current_branch": "develop",
    "uncommitted_changes": [
      " M src/main.py",
      "?? new_file.py"
    ],
    "recent_commits": [
      "a1b2c3d Update README",
      "e4f5g6h Add new feature"
    ],
    "remote_url": "https://github.com/user/repo.git"
  },
  "environment": {
    "venv_exists": true,
    "requirements_exists": true,
    "claude_md_exists": true,
    "env_exists": true
  },
  "claude_md": "# プロジェクトルール\n..."
}
```

## セットアップ

特別なセットアップは不要です（標準ライブラリのみ使用）。

## バージョン履歴

### v0.1.0 (2026-02-15)
- 初回リリース
- Git情報収集
- 環境チェック
- 手動実行時のVSCode連携

### 今後の予定
- v0.2.0: モデル最適化（haiku指定で省エネ実行）
