r"""
commands_restart - 既存プロジェクトの再開支援ツール

Created: 2026-02-15
Updated: 2026-02-15 18:30

【環境依存情報】2026年2月時点のPC環境に依存
PC引っ越し時の要修正箇所:
- VSCODE_PATH: VS Codeのインストールパス（現在は C:\Users\14506928\... に固定）
  → 新PC環境に合わせてフルパスを修正してください
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# 【環境依存】PC引っ越し時にこのパスを新環境に合わせて修正
VSCODE_PATH = r"C:\Users\14506928\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"


def get_git_info(project_path: Path) -> dict:
    """Git情報を取得"""
    git_info = {
        "is_git_repo": False,
        "current_branch": None,
        "uncommitted_changes": [],
        "recent_commits": [],
        "remote_url": None
    }

    if not (project_path / ".git").exists():
        return git_info

    git_info["is_git_repo"] = True

    try:
        # 現在のブランチ
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        git_info["current_branch"] = result.stdout.strip()

        # 未コミットの変更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        if result.stdout and result.stdout.strip():
            git_info["uncommitted_changes"] = result.stdout.strip().split("\n")

        # 最近のコミット（5件）
        result = subprocess.run(
            ["git", "log", "-5", "--oneline", "--decorate"],
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        if result.stdout and result.stdout.strip():
            git_info["recent_commits"] = result.stdout.strip().split("\n")

        # リモートURL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode == 0 and result.stdout:
            git_info["remote_url"] = result.stdout.strip()

    except subprocess.CalledProcessError:
        pass
    except Exception:
        pass

    return git_info


def get_env_info(project_path: Path) -> dict:
    """環境情報を取得"""
    return {
        "venv_exists": (project_path / ".venv").exists(),
        "requirements_exists": (project_path / "requirements.txt").exists(),
        "claude_md_exists": (project_path / "CLAUDE.md").exists(),
        "env_exists": (project_path / ".env").exists()
    }


def read_claude_md(project_path: Path) -> str | None:
    """CLAUDE.mdの内容を読み込み"""
    claude_md_path = project_path / "CLAUDE.md"
    if claude_md_path.exists():
        return claude_md_path.read_text(encoding="utf-8")
    return None


def info_mode(project_path: str):
    """LLM経由実行：プロジェクト情報をJSON出力"""
    path = Path(project_path).resolve()

    if not path.exists():
        print(json.dumps({
            "success": False,
            "error": f"プロジェクトパスが存在しません: {path}"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 情報収集
    git_info = get_git_info(path)
    env_info = get_env_info(path)
    claude_md_content = read_claude_md(path)

    # JSON出力
    output = {
        "success": True,
        "project_path": str(path),
        "project_name": path.name,
        "git": git_info,
        "environment": env_info,
        "claude_md": claude_md_content
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


def interactive_mode():
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

    # エクスプローラーでフォルダ選択
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

    # プロジェクト情報を収集
    git_info = get_git_info(project_path)
    env_info = get_env_info(project_path)
    claude_md_content = read_claude_md(project_path)

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

    # 情報出力
    output = {
        "success": True,
        "project_path": str(project_path),
        "project_name": project_path.name,
        "git": git_info,
        "environment": env_info,
        "claude_md": claude_md_content,
        "vscode_opened": vscode_opened
    }

    if vscode_error:
        output["vscode_error"] = vscode_error

    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="既存プロジェクトの再開支援ツール"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="プロジェクトのパス（指定時は情報出力モード）"
    )

    args = parser.parse_args()

    if args.path:
        # LLM経由：情報出力モード
        info_mode(args.path)
    else:
        # 手動実行：対話モード
        interactive_mode()


if __name__ == "__main__":
    main()
