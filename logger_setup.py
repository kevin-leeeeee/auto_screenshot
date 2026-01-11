import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "app", log_file: str = "logs/app.log", level: int = logging.INFO) -> logging.Logger:
    """
    設定並回傳一個 Logger 實例。
    同時輸出到 Console (Level 由參數決定) 和 File (固定為 DEBUG)。
    """
    logger = logging.getLogger(name)
    
    # 如果已經設定過 handlers 就不要重複設定 (避免 Jupyter 或重複呼叫時 log 重複)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # 設定 Root Logger 為最低級別，再由 Handler 過濾

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 確保 logs 資料夾存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File Handler (Rotating, Max 5MB, Backup 3)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG) # 檔案紀錄所有細節
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level) # Console 只顯示 INFO 以上 (除非 debug mode)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# 預設 Logger
logger = setup_logger()
