import os
import sys
import json
from dataclasses import dataclass
from pathlib import Path

# ==========================
# 預設值（可用參數覆蓋）
DEFAULT_URLS_FILE = "urls.txt"     # 預設網址清單檔
DONE_LOG = "done_urls.json"        # 已完成網址紀錄（避免重複訪問）

# 一開頁就倒數（載入中 + 最終截圖倒數）
PAGE_WAIT_RANGE = (15, 30)         # 一個網址從開頁到截圖前的總倒數秒數（含「載入中」與「準備截圖」）
FINAL_COUNTDOWN_SECONDS = 5        # 最後 N 秒顯示「準備截圖」

# 批次節奏
BATCH_SIZE = 8
BATCH_REST_RANGE = (20, 30)

# UI 隱藏後到截圖前的重繪緩衝（避免殘影）
UI_HIDE_BUFFER_SECONDS = 0.45

# 暖機
WARM_UP_ENABLED = False
WARM_UP_URL = "https://shopee.tw/"
WARM_UP_WAIT_RANGE = (3, 5)

# 其它
DEDUP_URLS = True # (This seems unused or I missed it? Ah, line 29)
SKIP_DONE_DEFAULT = True # New default
RECORD_OUTPUT_DEFAULT = True

TEXT_CHECK_ENABLED_DEFAULT = False
WORD_ENABLED_DEFAULT = False
SCROLL_CAPTURE_DEFAULT = False
SCROLL_CAPTURE_MULTIPLIER = 2
SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT = 4
CAPTURE_ACTIVE_WINDOW_DEFAULT = False
SCROLL_SIMILARITY_THRESHOLD = 0.99
TOOLTIP_ALPHA = 0.75
WEBPAGE_TOP_CROP_PX_DEFAULT = 120
WEBPAGE_BOTTOM_CROP_PX_DEFAULT = 0
SCROLL_CAPTURE_WAIT_SECONDS = 0.6
OCR_LANG = "chi_tra+eng"
PREFS_FILE = "preferences.json"

BROWSER_TITLE_KEYWORDS = ("chrome", "edge", "firefox", "brave", "opera", "vivaldi")

CAPTCHA_KEYWORDS = [
    "驗證碼", "人機驗證", "我不是機器人", "captcha", "verify", "請驗證您是人類",
    "安全驗證", "驗證資訊失敗", "拼圖", "puzzle", "robot", "automated", "rate limit",
    "verification", "滑動圖塊", "完成驗證", "安全性驗證"
]
NOT_FOUND_KEYWORDS = [
    "商品不存在", "已下架", "找不到商品", "商品已刪除", "商品已下架", "查無資料"
]
BSMI_KEYWORDS = [
    "bsmi",
    "b s m i",
    "商品檢驗標識",
]
LOGIN_KEYWORDS = [
    "登入",
    "登錄",
    "sign in",
    "log in",
    "login",
    "會員登入",
    "帳號",
    "密碼",
]
# ==========================

@dataclass
class RunConfig:
    urls_file: Path = Path(DEFAULT_URLS_FILE)
    output_dir: Path | None = None
    done_log: Path = Path(DONE_LOG)
    warmup_enabled: bool = WARM_UP_ENABLED
    page_wait_range: tuple[int, int] = PAGE_WAIT_RANGE
    final_countdown: int = FINAL_COUNTDOWN_SECONDS
    skip_done: bool = SKIP_DONE_DEFAULT
    record_output: bool = RECORD_OUTPUT_DEFAULT
    word_enabled: bool = WORD_ENABLED_DEFAULT
    text_check_enabled: bool = TEXT_CHECK_ENABLED_DEFAULT
    captcha_keywords: list[str] = None
    not_found_keywords: list[str] = None
    bsmi_keywords: list[str] = None
    login_keywords: list[str] = None
    scroll_capture: bool = SCROLL_CAPTURE_DEFAULT
    capture_window: bool = CAPTURE_ACTIVE_WINDOW_DEFAULT
    crop_enabled: bool = False
    scroll_pagedown_times: int = SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT
    crop_top_px: int = WEBPAGE_TOP_CROP_PX_DEFAULT
    crop_bottom_px: int = WEBPAGE_BOTTOM_CROP_PX_DEFAULT
    batch_size: int = BATCH_SIZE
    batch_rest_range: tuple[int, int] = BATCH_REST_RANGE
    word_path: str | Path | None = None
    login_mode: bool = False
    headless: bool = True
    cdp_mode: bool = False
    custom_categories: dict = None
    category_pause: dict = None
    keywords: list = None



    def __post_init__(self):
        if self.captcha_keywords is None:
            self.captcha_keywords = CAPTCHA_KEYWORDS
        if self.not_found_keywords is None:
            self.not_found_keywords = NOT_FOUND_KEYWORDS
        if self.bsmi_keywords is None:
            self.bsmi_keywords = BSMI_KEYWORDS
        if self.login_keywords is None:
            self.login_keywords = LOGIN_KEYWORDS

    def validate(self):
        """檢查設定值是否合法，若不合法則拋出 ValueError"""
        if self.page_wait_range[0] > self.page_wait_range[1]:
            raise ValueError("每頁等待最小值不可大於最大值")
        if self.final_countdown < 0:
            raise ValueError("截圖倒數不可為負數")
        
        if self.batch_size < 0:
             # Allow 0 = disabled, but UI sets batch_size to int
             raise ValueError("批次大小不可為負數")
             
        if self.batch_rest_range[0] > self.batch_rest_range[1]:
            raise ValueError("批次休息最小值不可大於最大值")
            
        if self.scroll_capture and self.scroll_pagedown_times <= 0:
            raise ValueError("PageDown 次數需大於 0")
            
        if self.crop_enabled:
            if self.crop_top_px < 0 or self.crop_bottom_px < 0:
                raise ValueError("裁切像素不可為負數")
        
        if self.text_check_enabled:
            if not self.captcha_keywords or not self.not_found_keywords or \
               not self.bsmi_keywords or not self.login_keywords:
                raise ValueError("開啟文字檢查時，關鍵字清單不可為空")


from logger_setup import logger

def load_prefs(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning(f"Failed to load prefs: {exc}")
        return {}


def save_prefs(path: str | Path, prefs: dict) -> None:
    path = Path(path)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.warning(f"Failed to save prefs: {exc}")
