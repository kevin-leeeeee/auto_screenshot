import pyautogui
from pathlib import Path
try:
    from PIL import Image, ImageGrab, ImageChops, ImageStat
except Exception:
    Image = None
    ImageGrab = None
    ImageChops = None
    ImageStat = None
try:
    import pygetwindow as gw
except Exception:
    gw = None

import time
import time
from utils_system import focus_browser_window, click_window_corner, looks_like_url, sleep_random
from logger_setup import logger
from config import SCROLL_CAPTURE_MULTIPLIER, SCROLL_SIMILARITY_THRESHOLD, SCROLL_CAPTURE_WAIT_SECONDS

def image_similarity(img1: Image.Image, img2: Image.Image) -> float:
    """
    計算兩張圖片的相似度 (0.0 ~ 1.0)。
    會先將圖片縮放至相同大小，再計算差異。
    """
    if ImageChops is None or ImageStat is None:
        return 0.0
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    max_w = 800
    if img1.width > max_w:
        scale = max_w / img1.width
        new_size = (max_w, max(1, int(img1.height * scale)))
        img1 = img1.resize(new_size)
        img2 = img2.resize(new_size)
    diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
    stat = ImageStat.Stat(diff)
    mean = sum(stat.mean) / len(stat.mean)
    return max(0.0, 1.0 - (mean / 255.0))

def capture_active_window() -> Image.Image | None:
    """
    截取目前作用中視窗的畫面。
    """
    if gw is None or ImageGrab is None:
        return None
    win = gw.getActiveWindow()
    if win is None:
        return None
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    if right <= left or bottom <= top:
        return None
    return ImageGrab.grab(bbox=(left, top, right, bottom))

def crop_webpage_area(img: Image.Image, top_px: int, bottom_px: int) -> Image.Image:
    """
    裁切圖片的頂部與底部。
    """
    top_px = max(0, int(top_px))
    bottom_px = max(0, int(bottom_px))
    if top_px == 0 and bottom_px == 0:
        return img
    if img.height <= top_px + bottom_px + 1:
        return img
    return img.crop((0, top_px, img.width, img.height - bottom_px))

def focus_page_for_copy() -> None:
    try:
        if gw is not None:
            wins = [
                w
                for w in gw.getAllWindows()
                if w is not None and w.isVisible and w.width > 300 and w.height > 200
            ]
            if wins:
                win = max(wins, key=lambda w: w.width * w.height)
                try:
                    win.activate()
                except Exception:
                    pass
                time.sleep(0.1)
    except Exception:
        pass

    focus_browser_window()
    click_window_corner("bottom_left")

import ctypes
from ctypes import wintypes as w

def get_clipboard_text_ctypes() -> str:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    
    if not user32.OpenClipboard(None):
        return ""
    try:
        if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
            return ""
        h_data = user32.GetClipboardData(CF_UNICODETEXT)
        if not h_data:
            return ""
        p_data = kernel32.GlobalLock(h_data)
        if not p_data:
            return ""
        try:
            return ctypes.c_wchar_p(p_data).value
        finally:
            kernel32.GlobalUnlock(h_data)
    except Exception:
        return ""
    finally:
        user32.CloseClipboard()

def extract_text_content(region: tuple[int, int, int, int] | None = None) -> str:
    """
    Extract text content using clipboard (Ctrl+A).
    """
    # 1. Focus browser to ensure hotkeys work
    focus_browser_window()
    
    # 2. Use Ctrl+A -> Ctrl+C to get text
    wait_seconds = 0.15
    prev_text = get_clipboard_text_ctypes()

    text = ""
    marker = f"__CLIPBOARD_MARKER_{time.time_ns()}__"
    
    # Set marker (simplified, just clear first)
    # Since we can't easily SET clipboard with just ctypes without more code, 
    # and relying on clearing is usually enough difference.
    # Actually setting clipboard with ctypes is also verbose.
    # Let's rely on checking if content CHANGED or is new.
    # Or keep it simple: clear clipboard via simple open/empty/close
    
    def clear_clipboard():
        user32 = ctypes.windll.user32
        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            user32.CloseClipboard()

    for attempt in range(3):
        focus_page_for_copy()
        clear_clipboard()
        
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(wait_seconds)
        
        click_window_corner("bottom_left")
        time.sleep(0.05)
        pyautogui.press("esc")
        time.sleep(0.05)
        
        for _ in range(10):
            text = get_clipboard_text_ctypes()
            if text:
                break
            time.sleep(0.1)
            
        if text.strip() and not looks_like_url(text):
            break
        time.sleep(0.2)
        
    snippet = text[:200].replace("\n", " ").replace("\r", " ")
    logger.debug(f"  文字長度: {len(text)} | 節錄: {snippet!r}")

    # No need to restore previous text, it's usually not critical for this tool
    return text

def normalize_text(text: str) -> str:
    return "".join(text.lower().split())

def classify_text(
    text: str,
    captcha_keywords: list[str],
    not_found_keywords: list[str],
    bsmi_keywords: list[str],
    login_keywords: list[str],
) -> str:
    """
    根據關鍵字將文字分類。
    """
    if not text:
        return "無法判斷"
    limit = max(200, int(len(text) * 0.05))
    t = normalize_text(text[:limit])
    if any(normalize_text(k) in t for k in login_keywords):
        return "登入"
    if any(normalize_text(k) in t for k in captcha_keywords):
        return "驗證是否人類"
    if any(normalize_text(k) in t for k in not_found_keywords):
        return "商品不存在"
    if any(normalize_text(k) in t for k in bsmi_keywords):
        return "商品存在 且有BSMI認證"
    return "無法判斷"

def capture_scrolling_page(
    scroll_pagedown_times: int,
    crop_top: int,
    crop_bottom: int,
    capture_window: bool = False,
    similarity_threshold: float = SCROLL_SIMILARITY_THRESHOLD,
    max_pages: int = SCROLL_CAPTURE_MULTIPLIER,
    wait_seconds: float = SCROLL_CAPTURE_WAIT_SECONDS,
) -> tuple[Image.Image, bool]:
    """
    執行捲動截圖並合併。
    
    Returns:
        tuple[Image.Image, bool]: (合併後的圖片, 是否使用了視窗截圖模式)
    """
    if Image is None:
        raise RuntimeError("PIL is not available")

    shots = []
    used_window_mode = False

    def take_shot() -> tuple[Image.Image, bool]:
        if capture_window:
            img = capture_active_window()
            if img is not None:
                return img, True
        return pyautogui.screenshot(), False

    def post_process(img: Image.Image) -> Image.Image:
        return crop_webpage_area(img, crop_top, crop_bottom)

    no_scroll = False
    for i in range(max_pages):
        img, used_win = take_shot()
        if used_win:
            used_window_mode = True
        
        img = post_process(img)
        
        if shots:
            sim = image_similarity(shots[-1], img)
            if sim >= similarity_threshold:
                no_scroll = True
                break
        
        shots.append(img)
        
        if i < max_pages - 1:
            for _ in range(scroll_pagedown_times):
                pyautogui.press("pagedown")
            time.sleep(wait_seconds)

    if not shots:
        # Should not happen typically
        return pyautogui.screenshot(), False

    if no_scroll or len(shots) == 1:
        return shots[0], used_window_mode

    # Stitch images
    total_height = sum(img.height for img in shots)
    merged = Image.new("RGB", (shots[0].width, total_height))
    y = 0
    for img in shots:
        merged.paste(img, (0, y))
        y += img.height
    
    return merged, used_window_mode
