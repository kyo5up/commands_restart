"""
ロギング設定モジュール

Created: 2026-02-15
Updated: 2026-02-15 17:10
"""
import logging
import os
from datetime import datetime


def setup_logger(name: str = __name__) -> logging.Logger:
    """ロガーをセットアップして返す"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # _logsフォルダがなければ作成
    os.makedirs("_logs", exist_ok=True)

    # ファイルハンドラ（タイムスタンプ付きファイル名）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(
        f"_logs/app_{timestamp}.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # フォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
