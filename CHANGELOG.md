# CHANGELOG

## [Unreleased]

## [v0.3.0] - 2026-03-24

### Added
- `get_project_type()` を追加: `CLAUDE.md` から `project_type` を読み取る

### Changed
- `project_type: web` の場合 `main.py` / `logger_config.py` を生成しないよう分岐
- README.md に `project_type` による分岐の説明を追記

## [v0.2.0] - 2026-03-23

### Added
- `/start` で生成される全ファイルの `ensure_xxx` を追加（env/requirements/readme/main_py/logger_config/claude_md/changelog/git_status/logs_dir）
- セクション見出し抽出・テンプレート照合のJSON出力を追加（doc_sections/template_sections）
- `commands_start/_templates/` を参照する `render_template()` を追加

### Removed
- `ensure_develop_branch()` を削除（developブランチは廃止済み）

### Changed
- README.mdを書庫規約に準拠したフォーマットに更新

## [v0.1.3] - 2026-03-09

### Changed
- 憲法（CLAUDE.md）を更新

## [v0.1.2] - 2026-02-24

### Added
- .gitignoreの確認・追記機能を追加

## [v0.1.1] - 2026-02-16

### Added
- VS Code仮想環境実行用のlaunch.jsonを追加

## [v0.1.0] - 2026-02-15

### Added
- 初版リリース
