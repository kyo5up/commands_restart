r"""
commands_restart - 既存プロジェクトの再開支援ツール

Created: 2026-02-15
Updated: 2026-02-24 16:26

【環境依存情報】2026年2月時点のPC環境に依存
PC引っ越し時の要修正箇所:
- VSCODE_PATH: VS Codeのインストールパス（現在は C:\Users\14506928\... に固定）
  → 新PC環境に合わせてフルパスを修正してください
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Windows環境での文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

TODAY = datetime.now().strftime("%Y-%m-%d")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# 【環境依存】PC引っ越し時にこのパスを新環境に合わせて修正
VSCODE_PATH = r"C:\Users\14506928\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"


# =============================================================================
# 環境整備
# =============================================================================

def ensure_venv(project_path: Path) -> str:
    """仮想環境がなければ作成する。結果メッセージを返す"""
    if (project_path / ".venv").exists():
        return "既存"
    result = subprocess.run(
        [sys.executable, "-m", "venv", ".venv"],
        cwd=project_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if result.returncode != 0:
        return f"作成失敗: {result.stderr.strip()}"
    return "新規作成"


def ensure_run_bat(project_path: Path) -> str:
    """run.batがなければ作成する。結果メッセージを返す"""
    run_bat = project_path / "run.bat"
    if run_bat.exists():
        return "既存"
    content = f"""\
@echo off
REM 実行用バッチファイル
REM Created: {TODAY}

cd /d %~dp0
call .venv\\Scripts\\activate.bat
python main.py %*
pause
"""
    run_bat.write_text(content, encoding="utf-8")
    return "新規作成"


def ensure_launch_json(project_path: Path) -> str:
    """.vscode/launch.jsonがなければ作成する。結果メッセージを返す"""
    vscode_dir = project_path / ".vscode"
    launch_json = vscode_dir / "launch.json"
    if launch_json.exists():
        return "既存"
    vscode_dir.mkdir(exist_ok=True)
    content = """\
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: main.py (venv)",
      "type": "debugpy",
      "request": "launch",
      "program": "${fileDirname}/main.py",
      "console": "integratedTerminal",
      "python": "${fileDirname}/.venv/Scripts/python.exe",
      "args": [],
      "cwd": "${fileDirname}",
      "justMyCode": true
    }
  ]
}
"""
    launch_json.write_text(content, encoding="utf-8")
    return "新規作成"


def ensure_develop_branch(project_path: Path) -> str:
    """mainブランチにいる場合はdevelopに切り替える。結果メッセージを返す"""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=project_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    current = result.stdout.strip()
    if current != "main":
        return f"変更なし（現在: {current}）"

    result = subprocess.run(
        ["git", "branch", "--list", "develop"],
        cwd=project_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if not result.stdout.strip():
        return "developブランチが存在しないためスキップ"

    result = subprocess.run(
        ["git", "checkout", "develop"],
        cwd=project_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return f"切り替え失敗: {result.stderr.strip()}"
    return "main → develop に切り替え"


# =============================================================================
# 情報収集
# =============================================================================

def get_git_info(project_path: Path) -> dict:
    """Git情報を取得"""
    git_info = {
        "is_git_repo": False,
        "current_branch": None,
        "uncommitted_changes": [],
        "remote_url": None,
    }

    if not (project_path / ".git").exists():
        return git_info

    git_info["is_git_repo"] = True

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path, capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=True,
        )
        git_info["current_branch"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path, capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=True,
        )
        if result.stdout and result.stdout.strip():
            git_info["uncommitted_changes"] = result.stdout.strip().split("\n")

        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0 and result.stdout:
            git_info["remote_url"] = result.stdout.strip()

    except (subprocess.CalledProcessError, Exception):
        pass

    return git_info


def read_claude_md(project_path: Path) -> str | None:
    """CLAUDE.mdの内容を読み込み"""
    claude_md_path = project_path / "CLAUDE.md"
    if claude_md_path.exists():
        return claude_md_path.read_text(encoding="utf-8")
    return None


# =============================================================================
# 表形式出力・ログ保存
# =============================================================================

def _row(label: str, value: str, w1: int = 20, w2: int = 35) -> str:
    return f"| {label:<{w1}}| {value:<{w2}}|"


def _sep(w1: int = 20, w2: int = 35) -> str:
    return f"|{'-' * (w1 + 1)}+{'-' * (w2 + 1)}|"


def _top(w1: int = 20, w2: int = 35) -> str:
    return f"|{'=' * (w1 + 1)}+{'=' * (w2 + 1)}|"


def build_report(project_name: str, setup: dict, git_info: dict) -> str:
    """表形式のレポート文字列を生成する"""
    lines = []
    lines.append(f"=== /restart: {project_name} ===")
    lines.append(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 環境整備
    lines.append("")
    lines.append("【環境整備】")
    labels = {
        "venv":        ".venv",
        "run_bat":     "run.bat",
        "launch_json": ".vscode/launch.json",
        "branch":      "ブランチ",
    }
    lines.append(_top())
    lines.append(_row("項目", "結果"))
    lines.append(_sep())
    for key, label in labels.items():
        lines.append(_row(label, setup.get(key, "-")))
    lines.append(_top())

    # プロジェクト状態
    lines.append("")
    lines.append("【プロジェクト状態】")
    changes = git_info.get("uncommitted_changes", [])
    if changes:
        change_str = f"{len(changes)}件（{changes[0].strip()}ほか）" if len(changes) > 1 else changes[0].strip()
    else:
        change_str = "なし"
    remote = git_info.get("remote_url") or "なし"
    if len(remote) > 35:
        remote = remote[:32] + "..."
    lines.append(_top())
    lines.append(_row("ブランチ", git_info.get("current_branch") or "-"))
    lines.append(_sep())
    lines.append(_row("未コミット変更", change_str))
    lines.append(_sep())
    lines.append(_row("リモート", remote))
    lines.append(_top())

    return "\n".join(lines)


def save_log(project_path: Path, report: str) -> Path:
    """_logs/ にログファイルを保存する"""
    logs_dir = project_path / "_logs"
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / f"restart_{TIMESTAMP}.log"
    log_path.write_text(report, encoding="utf-8")
    return log_path


# =============================================================================
# CLIモード
# =============================================================================

def info_mode(project_path: str) -> None:
    """LLM経由実行：環境整備・表形式レポート出力・JSON出力"""
    path = Path(project_path).resolve()

    if not path.exists():
        print(json.dumps({
            "success": False,
            "error": f"プロジェクトパスが存在しません: {path}"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 環境整備
    setup_results = {}
    if (path / ".git").exists():
        setup_results["venv"]        = ensure_venv(path)
        setup_results["run_bat"]     = ensure_run_bat(path)
        setup_results["launch_json"] = ensure_launch_json(path)
        setup_results["branch"]      = ensure_develop_branch(path)

    # 情報収集
    git_info = get_git_info(path)
    claude_md_content = read_claude_md(path)

    # 表形式レポートを生成・表示・ログ保存
    report = build_report(path.name, setup_results, git_info)
    print(report)
    log_path = save_log(path, report)
    print(f"\nログ保存: {log_path}")

    # ClaudeへのJSON出力（CLAUDE.md読み取り用）
    print("\n---JSON---")
    print(json.dumps({
        "success": True,
        "project_path": str(path),
        "project_name": path.name,
        "setup": setup_results,
        "git": git_info,
        "claude_md": claude_md_content,
    }, ensure_ascii=False, indent=2))


# =============================================================================
# GUIモード
# =============================================================================

def interactive_mode() -> None:
    """手動実行：エクスプローラー → VSCode起動"""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print(json.dumps({
            "success": False,
            "error": "tkinterがインストールされていません"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        title="再開するプロジェクトフォルダを選択",
        initialdir="C:/Users/14506928/Projects"
    )
    root.destroy()

    if not folder:
        print(json.dumps({
            "success": False,
            "error": "フォルダが選択されませんでした"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    project_path = Path(folder)

    # 環境整備
    setup_results = {}
    if (project_path / ".git").exists():
        setup_results["venv"]        = ensure_venv(project_path)
        setup_results["run_bat"]     = ensure_run_bat(project_path)
        setup_results["launch_json"] = ensure_launch_json(project_path)
        setup_results["branch"]      = ensure_develop_branch(project_path)

    git_info = get_git_info(project_path)
    claude_md_content = read_claude_md(project_path)

    # 表形式レポート・ログ保存
    report = build_report(project_path.name, setup_results, git_info)
    print(report)
    save_log(project_path, report)

    # VSCodeで開く
    try:
        subprocess.run([VSCODE_PATH, str(project_path)], check=True)
        vscode_opened = True
        vscode_error = None
    except FileNotFoundError:
        vscode_opened = False
        vscode_error = f"VS Codeが見つかりません: {VSCODE_PATH}"
    except subprocess.CalledProcessError as e:
        vscode_opened = False
        vscode_error = f"VS Code起動失敗: {e}"
    except Exception as e:
        vscode_opened = False
        vscode_error = f"予期しないエラー: {e}"

    if vscode_error:
        print(f"\n[警告] {vscode_error}")


# =============================================================================
# メイン
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="既存プロジェクトの再開支援ツール")
    parser.add_argument("--path", type=str, help="プロジェクトのパス（指定時はCLIモード）")
    args = parser.parse_args()

    if args.path:
        info_mode(args.path)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
