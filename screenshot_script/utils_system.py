import os
import sys
import time
import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pyautogui
try:
    import pygetwindow as gw
except Exception:
    gw = None
try:
    from PIL import Image
except Exception:
    Image = None

from config import (
    BROWSER_TITLE_KEYWORDS,
    DEDUP_URLS,
    DEFAULT_URLS_FILE,
)
from logger_setup import logger

def default_output_dir_from_urls(urls_file: str | Path) -> str:
    """
    urls3.txt -> screenshots_urls3
    urls.txt  -> screenshots_urls
    urls_20260107.txt -> screenshots_urls_20260107
    """
    base = Path(urls_file).name
    name, _ = os.path.splitext(base)
    return f"screenshots_{name}"

def default_word_path(output_dir: Path, urls_file: Path) -> Path:
    base = Path(output_dir).name.strip()
    if not base or base == ".":
        base = f"screenshots_{Path(urls_file).stem}"
    return Path(output_dir) / f"{base}.docx"

def new_word_path(output_dir: Path, urls_file: Path, base_path: str | Path | None = None) -> Path:
    if base_path:
        p = Path(base_path)
        if p.suffix.lower() == ".docx" or "." in p.name:
            parent = p.parent if str(p.parent) else Path(output_dir)
            base = p.stem or Path(output_dir).name.strip()
        else:
            parent = p
            base = p.name or Path(output_dir).name.strip()
    else:
        parent = Path(output_dir)
        base = Path(output_dir).name.strip() or f"screenshots_{Path(urls_file).stem}"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return parent / f"{base}_{ts}.docx"

def format_relative_path(path: str) -> str:
    try:
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent
        else:
            base = Path.cwd()
        return os.path.relpath(path, base)
    except Exception:
        return path

def resolve_path(path: str) -> str:
    if Path(path).is_absolute():
        return path
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()
    return str((base / path).resolve())

def safe_filename(s: str) -> str:
    repl = s.replace("https://", "").replace("http://", "")
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        repl = repl.replace(ch, "_")
    return repl[:23]

def parse_keywords(raw: str) -> list[str]:
    items = []
    for part in raw.replace(";", ",").replace("\n", ",").split(","):
        s = part.strip()
        if s:
            items.append(s)
    return items

def append_to_word(doc, word_path: Path, url: str, image_path: Path, note: str | None = None) -> None:
    if note:
        doc.add_paragraph(note)
    doc.add_paragraph(url)
    max_width = None
    try:
        section = doc.sections[0]
        max_width = section.page_width - section.left_margin - section.right_margin
    except Exception:
        max_width = None

    width = None
    if max_width:
        width = max_width
        if Image is not None:
            try:
                with Image.open(image_path) as img:
                    dpi = img.info.get("dpi", (96, 96))
                    dpi_x = dpi[0] if dpi and dpi[0] else 96
                    width_emu = int(img.size[0] / dpi_x * 914400)
                    if width_emu <= max_width:
                        width = None
            except Exception:
                pass

    if width is not None:
        doc.add_picture(str(image_path), width=width)
    else:
        doc.add_picture(str(image_path))
    doc.add_paragraph("")
    doc.save(word_path)

def load_urls(path: str | Path) -> list[tuple[str, str | None]]:
    """
    讀取網址清單檔案。
    支援 # 開頭的註解行 (會被視為下一個網址的附註)。
    
    Args:
        path: 網址清單檔案路徑

    Returns:
        list[tuple[str, str | None]]: 每個元素為 (url, note) 的 Tuple
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {path}")

    urls = []
    pending_note: str | None = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                pending_note = s[1:].strip() or None
                continue
            urls.append((s, pending_note))
            pending_note = None

    if DEDUP_URLS:
        seen = set()
        deduped = []
        for u, note in urls:
            if u not in seen:
                seen.add(u)
                deduped.append((u, note))
        urls = deduped

    return urls

def load_done_data(path: str | Path) -> tuple[set[str], dict[str, str], dict[str, str]]:
    """
    讀取已完成的紀錄檔 (JSON)。
    
    Args:
        path: 紀錄檔路徑

    Returns:
        tuple[set[str], dict[str, str], dict[str, str]]: 
            - done_set: 已完成的 URL 集合
            - outputs: URL 對應的輸出檔案路徑 (dict)
            - classes: URL 對應的分類結果 (dict)
    """
    path = Path(path)
    done_set: set[str] = set()
    outputs: dict[str, str] = {}
    classes: dict[str, str] = {}
    if not path.exists():
        return done_set, outputs, classes
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    done_set.add(item)
                elif isinstance(item, dict):
                    url = item.get("url") or item.get("u")
                    if url:
                        done_set.add(url)
                        output = item.get("output") or item.get("path")
                        if output:
                            outputs[url] = output
                        cls = item.get("class") or item.get("classification")
                        if cls:
                            classes[url] = cls
        elif isinstance(data, dict):
            urls = data.get("done") or data.get("urls")
            if isinstance(urls, list):
                for u in urls:
                    if isinstance(u, str):
                        done_set.add(u)
            out_map = data.get("outputs") or data.get("paths")
            if isinstance(out_map, dict):
                for k, v in out_map.items():
                    if isinstance(k, str) and isinstance(v, str):
                        outputs[k] = v
                        done_set.add(k)
            class_map = data.get("classes") or data.get("classifications")
            if isinstance(class_map, dict):
                for k, v in class_map.items():
                    if isinstance(k, str) and isinstance(v, str):
                        classes[k] = v
                        done_set.add(k)
    except Exception as exc:
        logger.warning(f"Warning: failed to read done_log, starting fresh: {path} ({exc})")
    return done_set, outputs, classes

def save_done_data(
    path: str | Path,
    done_set: set[str],
    outputs: dict[str, str],
    classes: dict[str, str],
    record_output: bool,
    record_classification: bool,
) -> None:
    """
    將完成紀錄寫入 JSON 檔案。
    
    Args:
        path: 紀錄檔路徑
        done_set: 已完成的 URL 集合
        outputs: 輸出路徑對應
        classes: 分類結果對應
        record_output: 是否記錄輸出路徑
        record_classification: 是否記錄分類結果
    """
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if record_output or record_classification:
        data = []
        for url in sorted(done_set):
            item = {"url": url}
            if record_output:
                output = outputs.get(url)
                if output:
                    item["output"] = output
            if record_classification:
                cls = classes.get(url)
                if cls:
                    item["class"] = cls
            data.append(item)
    else:
        data = sorted(done_set)
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def clear_done_log(path: str | Path) -> bool:
    path = Path(path)
    if not path.exists():
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    tmp.replace(path)
    return True

def focus_browser_window() -> bool:
    """
    嘗試將焦點移至瀏覽器視窗。
    會根據 BROWSER_TITLE_KEYWORDS 搜尋視窗標題。
    
    Returns:
        bool: 是否成功找到並嘗試啟用視窗
    """
    if gw is None:
        return False
    try:
        wins = []
        for w in gw.getAllWindows():
            if not w or not w.isVisible:
                continue
            title = (w.title or "").lower()
            if any(k in title for k in BROWSER_TITLE_KEYWORDS):
                wins.append(w)
        if not wins:
            return False
        win = max(wins, key=lambda w: max(1, w.width) * max(1, w.height))
        try:
            win.activate()
        except Exception:
            pass
        time.sleep(0.1)
        return True
    except Exception:
        return False

def click_window_corner(where: str = "bottom_left", double: bool = False) -> None:
    try:
        focus_browser_window()
        win = gw.getActiveWindow() if gw is not None else None
        if win is not None:
            screen_w, screen_h = pyautogui.size()
            inset_x = 16
            inset_y = 40
            x = int(win.left) + inset_x
            y = int(win.top + win.height) - inset_y
            x = max(0, min(screen_w - 1, x))
            y = max(0, min(screen_h - 1, y))
            if where == "bottom_left":
                if double:
                    pyautogui.doubleClick(x, y, interval=0.05)
                else:
                    pyautogui.click(x, y)
            return
    except Exception:
        pass
    try:
        w, h = pyautogui.size()
        pyautogui.click(8, max(8, h - 8))
    except Exception:
        pass



def looks_like_url(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if " " in t or "\n" in t or "\r" in t:
        return False
    return t.startswith("http://") or t.startswith("https://")

def append_text_log(log_path: Path, url: str, text: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snippet = text[:200].replace("\n", " ").replace("\r", " ")
    line = f"[{ts}] len={len(text)} url={url} snippet={snippet!r}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", errors="replace") as f:
        f.write(line)

def short_url(url: str, n: int = 90) -> str:
    return url if len(url) <= n else url[: n - 3] + "..."

def sleep_random(rng: tuple[float, float], reason: str = "") -> float:
    sec = random.uniform(rng[0], rng[1])
    if reason:
        logger.debug(f"  等待 {sec:.1f}s（{reason}）")
    time.sleep(sec)
    return sec

def is_shopee_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
        return "shopee.tw" in host
    except Exception:
        return False
