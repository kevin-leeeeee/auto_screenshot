import argparse
import random
import time
import webbrowser
import pyautogui
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from docx import Document
except ImportError:
    Document = None

from config import (
    BATCH_REST_RANGE,
    BATCH_SIZE,
    BSMI_KEYWORDS,
    CAPTCHA_KEYWORDS,
    CAPTURE_ACTIVE_WINDOW_DEFAULT,
    DEFAULT_URLS_FILE,
    DONE_LOG,
    FINAL_COUNTDOWN_SECONDS,
    LOGIN_KEYWORDS,
    NOT_FOUND_KEYWORDS,
    TEXT_CHECK_ENABLED_DEFAULT,
    PAGE_WAIT_RANGE,
    SKIP_DONE_DEFAULT,
    RECORD_OUTPUT_DEFAULT,
    SCROLL_CAPTURE_DEFAULT,
    SCROLL_CAPTURE_MULTIPLIER,
    SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT,
    SCROLL_CAPTURE_WAIT_SECONDS,
    SCROLL_SIMILARITY_THRESHOLD,
    UI_HIDE_BUFFER_SECONDS,
    WARM_UP_ENABLED,
    WARM_UP_URL,
    WARM_UP_WAIT_RANGE,
    WEBPAGE_BOTTOM_CROP_PX_DEFAULT,
    WEBPAGE_TOP_CROP_PX_DEFAULT,
    WORD_ENABLED_DEFAULT,
    RunConfig,
)
from logger_setup import logger
from ui import OverlayUI, show_error_ui, show_info_ui, ui_collect_settings
from utils_system import (
    append_text_log,
    append_to_word,
    click_window_corner,
    default_output_dir_from_urls,
    load_done_data,
    load_urls,
    new_word_path,
    safe_filename,
    save_done_data,
    short_url,
    sleep_random,
)
from utils_image import (
    capture_active_window,
    classify_text,
    crop_webpage_area,
    image_similarity,
    extract_text_content,
    capture_scrolling_page,

)

# 初始化設定
pyautogui.PAUSE = 0.15

class DummyOverlay:
    """
    A dummy overlay that does nothing, used when running in headless/API mode
    to avoid tkinter thread issues.
    """
    def __init__(self, *args, **kwargs): pass
    def set_paused(self, paused: bool): pass
    def wait_if_paused(self) -> str | None: return None
    def set_footer(self, text: str): pass
    def show(self): pass
    def close(self): pass
    def countdown_with_status(self, base_lines: list[str], total_seconds: int, final_seconds: int) -> str:
        for t in range(total_seconds, 0, -1):
             time.sleep(1)
        return "done"
    def set_footer(self, text: str): pass
    def show(self): pass
    def close(self): pass
    def countdown_with_status(self, base_lines: list[str], total_seconds: int, final_seconds: int) -> str:
        for t in range(total_seconds, 0, -1):
             time.sleep(1)
        return "done"


def parse_args():
    parser = argparse.ArgumentParser(
        description="用真實瀏覽器開啟網址清單並截圖（預設 urls.txt；輸出資料夾自動同步 urls 檔名；一開頁即顯示倒數）"
    )
    parser.add_argument(
        "urls_file",
        nargs="?",
        default=DEFAULT_URLS_FILE,
        help=f"網址清單檔（預設：{DEFAULT_URLS_FILE}）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="輸出資料夾（預設：screenshots_<urls檔名>）",
    )
    parser.add_argument(
        "--done-log",
        default=DONE_LOG,
        help=f"完成紀錄檔（預設：{DONE_LOG}）",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="停用暖機",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="開啟互動 UI 設定參數",
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="不使用 UI",
    )
    parser.add_argument(
        "--word",
        action="store_true",
        help="輸出 Word (.docx)",
    )
    parser.add_argument(
        "--word-path",
        default=None,
        help="Word 檔案路徑（預設輸出資料夾內）",
    )
    return parser.parse_args()


def handle_page_checks(cfg: RunConfig, overlay: OverlayUI) -> tuple[str | None, bool, bool]:
    """
    Check for login/captcha/not found pages.
    Returns: (classification_result, should_stop, should_skip)
    """
    if not cfg.text_check_enabled:
        return None, False, False

    # 進行文字檢查 (Ctrl+A)
    extracted_text = extract_text_content()
    
    cls = classify_text(
        extracted_text, 
        cfg.captcha_keywords, 
        cfg.not_found_keywords, 
        cfg.bsmi_keywords, 
        cfg.login_keywords
    )
    logger.info(f"  分類: {cls}")
    
    if cls == "登入":
        logger.warning("Detected login page. Pausing for manual intervention...")
        overlay.set_footer("偵測到登入頁面，請登入後按繼續")
        overlay.set_paused(True)
        overlay.show()
        # Wait for user to resume
        if overlay.wait_if_paused() == "stop":
            return cls, True, False
        overlay.set_footer("")
        # Return checking again? Or just continue? Original code continued re-processing.
        # But here we typically just assume user fixed it. 
        # For simplicity, we assume fixed and return. Ideally we might want to re-classify?
        # The caller loop will decide whether to retry screenshot.
        return cls, False, False

    elif cls == "驗證是否人類":
        logger.warning("Detected CAPTCHA. Pausing for manual intervention...")
        overlay.set_footer("偵測到驗證碼，請驗證後按繼續")
        overlay.set_paused(True)
        overlay.show()
        if overlay.wait_if_paused() == "stop":
            return cls, True, False
        overlay.set_footer("")
        return cls, False, False
    
    elif cls == "商品不存在":
        logger.warning("Product not found. Skipping...")
        return cls, False, True
    
    # If standard page, ensure window is ready for screenshot (click corner, esc)
    click_window_corner("bottom_left")
    time.sleep(0.05)
    pyautogui.press("esc")
    
    return cls, False, False


def capture_image(cfg: RunConfig, outpath: Path) -> tuple[object | None, bool]:
    """
    Perform the actual capture (single or scroll).
    Returns (image, used_window_mode)
    """
    try:
        if cfg.scroll_capture:
            return capture_scrolling_page(
                scroll_pagedown_times=cfg.scroll_pagedown_times,
                crop_top=cfg.crop_top_px,
                crop_bottom=cfg.crop_bottom_px,
                capture_window=cfg.capture_window,
            )
        else:
            # Single shot
            used_window = False
            img = None
            if cfg.capture_window:
                img = capture_active_window()
                if img:
                    used_window = True
            
            if img is None:
                img = pyautogui.screenshot()
                used_window = False
            
            # Crop logic
            if cfg.crop_enabled:
                 img = crop_webpage_area(img, cfg.crop_top_px, cfg.crop_bottom_px)
            
            return img, used_window
    except Exception as exc:
        logger.error(f"Capture failed: {exc}")
        return None, False


def run_capture(cfg: RunConfig, external_stop_callback=None, progress_callback=None, use_overlay=True) -> bool:
    """
    主要執行流程。
    Returns: bool (End execution request? True=Stop completely, False=Normal finish)
    Note: Original logic returned True to indicate "back to UI" or "Stop"?
    Original: returns True if "needs to return to UI to re-configure".
    Let's check the caller. 
    If returns True, loop `continue` (back to UI). 
    If returns False, loop `return` (exit program).
    Wait, original `run_capture` returned `bool`: `stop_requested`.
    If stopped manually -> return True (stop requested, back to UI to possibly restart or exit?)
    Actually lines 541: `back_to_ui = run_capture(...)`.
    The logic was a bit confusing. Let's stick to:
    Returns True if we should allow the user to go back to UI (e.g. stopped manually),
    Returns False if we are done completely.
    """
    
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup Word
    word_doc = None
    word_path_final = None
    if cfg.word_enabled:
        if Document is None:
            logger.info("Word export requires python-docx; skipping.")
        else:
            word_path_final = new_word_path(cfg.output_dir, cfg.urls_file, cfg.word_path)
            word_path_final.parent.mkdir(parents=True, exist_ok=True)
            word_doc = Document()
            word_doc.save(word_path_final)
            print(f"Word file: {word_path_final}")

    urls = load_urls(cfg.urls_file)
    if not urls:
        raise RuntimeError(f"{cfg.urls_file} 沒有網址，請檢查檔案內容。")

    done, done_outputs, done_classes = load_done_data(cfg.done_log)
    total = len(urls)
    
    logger.info(f"Config: {cfg}")
    logger.info(f"Loaded {total} URLs (Done: {len(done)})")

    # Control flags
    stop_requested = {"flag": False}
    manual_requested = {"flag": False}

    def request_stop():
        stop_requested["flag"] = True

    def request_manual():
        manual_requested["flag"] = True

    def consume_manual() -> bool:
        if manual_requested["flag"]:
            manual_requested["flag"] = False
            return True
        return False

    OverlayClass = OverlayUI if use_overlay else DummyOverlay
    overlay = OverlayClass(
        on_stop=request_stop,
        should_stop=lambda: stop_requested["flag"] or (external_stop_callback() if external_stop_callback else False),
        on_manual=request_manual,
        should_skip=consume_manual,
    )
    
    processed_this_run = 0
    skipped_this_run = 0
    done_dirty = False

    def flush_done(force: bool = False):
        nonlocal done_dirty
        if done_dirty or force:
            save_done_data(
                cfg.done_log,
                done,
                done_outputs,
                done_classes,
                cfg.record_output,
                record_classification=cfg.text_check_enabled,
            )
            done_dirty = False

    try:
        if cfg.warmup_enabled:
            logger.info(f"Warmup: {WARM_UP_URL}")
            overlay.set_footer("暖機中...")
            webbrowser.open(WARM_UP_URL, new=1)
            sleep_random(WARM_UP_WAIT_RANGE, "暖機等待")
            overlay.set_footer("")

        if progress_callback:
            progress_callback(0, total)

        for idx, (url, note) in enumerate(urls, start=1):
            if progress_callback:
                progress_callback(processed_this_run, total)

            if stop_requested["flag"]:
                flush_done(force=True)
                overlay.set_footer("已停止")
                return True
            
            # Check pause at start of loop
            if overlay.wait_if_paused() == "stop":
                flush_done(force=True)
                overlay.set_footer("已停止")
                return True

            if cfg.skip_done and url in done:
                skipped_this_run += 1
                continue

            url_short = short_url(url)
            
            # --- Single URL Processing Loop (Retry Logic) ---
            while True:
                logger.info(f"[{idx}/{total}] Processing {url_short}")
                overlay.set_footer(f"[{idx}/{total}] {short_url(url, 50)}")
                webbrowser.open(url, new=1)

                total_wait = random.randint(cfg.page_wait_range[0], cfg.page_wait_range[1])
                ts_human = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                base_lines = [
                    f"進度: {idx}/{total}",
                    f"時間: {ts_human}",
                    f"網址: {short_url(url, 95)}",
                ]

                # Countdown
                result = overlay.countdown_with_status(
                    base_lines=base_lines,
                    total_seconds=total_wait,
                    final_seconds=cfg.final_countdown,
                )

                if result == "stop":
                    flush_done(force=True)
                    overlay.set_footer("已停止")
                    return True
                if result == "skip":
                    # skip means "manual capture trigger" in overlay logic usually?
                    # Actually result='skip' comes from 'skip_wait' (manual button).
                    overlay.set_footer("手動截圖")

                time.sleep(UI_HIDE_BUFFER_SECONDS)

                # --- Page Checks (OCR) ---
                cls, should_stop, should_skip_url = handle_page_checks(cfg, overlay)
                if should_stop:
                    flush_done(force=True)
                    overlay.set_footer("已停止")
                    return True
                
                if should_skip_url:
                    # e.g. Product Not Found
                    done.add(url) # Mark as done even if skipped due to "not found"
                    if cfg.text_check_enabled and cls is not None:
                        done_classes[url] = cls
                    done_dirty = True
                    break # Next URL

                # If login/captcha was detected but user resolved it (cls is returned but not stop/skip),
                # we technically should re-check or just proceed to capture.
                # The original code did `continue` to re-process (re-open browser? or re-loop?)
                # Original code: `continue # Re-process current URL` which goes back to `while True`.
                # That means it re-opens the browser window? Yes `webbrowser.open(url, new=1)`.
                # That might be annoying if user just logged in on the current tab.
                # But let's stick to original behavior for safety: if we hit a blocker, we retry the whole flow for this URL.
                if cls in ["登入", "驗證是否人類"] and not should_skip_url: 
                     # "商品不存在" already handled by should_skip_url=True
                     # So this is for Login/Captcha where we want to retry the loop.
                     continue

                # --- Capture ---
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{idx:03d}_{ts}_{safe_filename(url)}.png"
                outpath = cfg.output_dir / fname

                img, used_window = capture_image(cfg, outpath)
                
                if img is None:
                    overlay.set_footer("截圖失敗")
                    # Retry logic? Original code says "continue" (retry this URL).
                    # Let's retry.
                    continue

                try:
                    img.save(outpath)
                    logger.info(f"  Saved: {outpath}")
                    overlay.set_footer("截圖完成")
                    
                    if cfg.text_check_enabled and cls is not None:
                        done_classes[url] = cls
                    
                    done.add(url)
                    if cfg.record_output:
                        done_outputs[url] = str(outpath)
                    
                    if word_doc and word_path_final:
                        try:
                            append_to_word(word_doc, word_path_final, url, outpath, note)
                        except Exception as e:
                            logger.error(f"Word export error: {e}")
                    
                    done_dirty = True
                    break # Done with this URL

                except Exception as exc:
                    logger.error(f"Save failed: {exc}")
                    overlay.set_footer(f"儲存失敗: {exc}")
                    continue # Retry

            # End While (Single URL)
            
            processed_this_run += 1
            if cfg.batch_size > 0 and processed_this_run > 0 and processed_this_run % cfg.batch_size == 0:
                flush_done()
                sleep_random(cfg.batch_rest_range, f"批次休息（每 {cfg.batch_size} 個）")

        # End For (URLs)
        
        logger.info("Run finished.")
        logger.info(f"Completed: {processed_this_run}, Skipped: {skipped_this_run}")
        logger.info(f"Completed: {processed_this_run}, Skipped: {skipped_this_run}")
        if progress_callback:
            progress_callback(processed_this_run, total)
        overlay.set_footer("完成")
        show_info_ui("完成", f"本次完成 {processed_this_run} 個，跳過 {skipped_this_run} 個。")

    except KeyboardInterrupt:
        flush_done(force=True)
        logger.info("\n已中止（Ctrl+C）。已保存 done_log。")
        overlay.set_footer("已停止")
        return True
    except Exception:
        flush_done(force=True)
        logger.exception("Unexpected error")
        overlay.set_footer("發生錯誤，請查看 Log")
        if cfg.output_dir: 
            # Check if UI was requested via config or args? 
            # The overlay is always active here.
             show_error_ui("發生未預期的錯誤，請查看 logs/app.log")
        return True
    finally:
        flush_done(force=True)
        overlay.close()


def run_from_api(should_stop_callback, config_overrides=None, progress_callback=None):
    """
    Entry point for API/Server to run the capture process.
    should_stop_callback: a callable that returns True if we should abort.
    config_overrides: dict of configuration options from UI
    """
    # 1. Resolve URLs file (Must be absolute as we will chdir later)
    urls_file_raw = config_overrides.get("urls_file") if config_overrides else None
    if not urls_file_raw:
        urls_file_raw = DEFAULT_URLS_FILE
    
    urls_file = Path(urls_file_raw).resolve()
    
    # 2. Resolve Output Dir
    if config_overrides and config_overrides.get("output_dir"):
         output_dir = Path(config_overrides["output_dir"]).resolve()
    else:
         output_dir = Path(default_output_dir_from_urls(urls_file)).resolve()
    
    # Base config
    cfg = RunConfig(
        urls_file=urls_file,
        output_dir=output_dir,
        done_log=Path(DONE_LOG).resolve(),
        warmup_enabled=WARM_UP_ENABLED,
        word_enabled=WORD_ENABLED_DEFAULT,
    )

    # Apply overrides if present
    if config_overrides:
        if "autoWordExport" in config_overrides:
            cfg.word_enabled = config_overrides["autoWordExport"]
        if "skip_done" in config_overrides:
            cfg.skip_done = config_overrides["skip_done"]
        if "text_check_enabled" in config_overrides:
            cfg.text_check_enabled = config_overrides["text_check_enabled"]
        if "scroll_capture" in config_overrides:
            cfg.scroll_capture = config_overrides["scroll_capture"]
        if "crop_top_px" in config_overrides:
            cfg.crop_top_px = config_overrides["crop_top_px"]
            cfg.crop_enabled = True # Auto enable crop if px is set
        if "crop_bottom_px" in config_overrides:
            cfg.crop_bottom_px = config_overrides["crop_bottom_px"]
            cfg.crop_enabled = True
        if "page_wait_range" in config_overrides:
            cfg.page_wait_range = config_overrides["page_wait_range"]

        # Add other fields as needed
        if "keywords" in config_overrides:
             # Basic keyword mapping - this might need more robust logic if strict mapping is required
             pass

    run_capture(cfg, external_stop_callback=should_stop_callback, progress_callback=progress_callback, use_overlay=True)
    return str(cfg.output_dir)




def main():
    args = parse_args()
    # Default to UI if not explicitly no-ui
    if not args.ui and not args.no_ui:
        args.ui = True

    while True:
        # 1. Build Base Config from Args
        cfg = RunConfig(
            urls_file=Path(args.urls_file),
            output_dir=Path(args.output) if args.output else None, # will be calculated if None
            done_log=Path(args.done_log),
            warmup_enabled=not args.no_warmup and WARM_UP_ENABLED,
            word_enabled=args.word,
            word_path=args.word_path,
        )
        
        # 2. If UI, collect settings to override Config
        if args.ui:
            # We need to calculate default output dir for UI preset if needed
            default_out = cfg.output_dir if cfg.output_dir else Path(default_output_dir_from_urls(cfg.urls_file))
            
            ui_res = ui_collect_settings(cfg.urls_file, default_out)
            if not ui_res:
                print("UI Canceled.")
                return

            # Update Config from UI
            cfg.urls_file = Path(ui_res["urls_file"])
            cfg.output_dir = Path(ui_res["output_dir"]) if ui_res["output_dir"] else Path(default_output_dir_from_urls(cfg.urls_file))
            cfg.page_wait_range = ui_res["page_wait_range"]
            cfg.final_countdown = ui_res["final_countdown"]
            cfg.skip_done = ui_res.get("skip_done", SKIP_DONE_DEFAULT)
            cfg.record_output = ui_res.get("record_output", RECORD_OUTPUT_DEFAULT)
            cfg.word_enabled = ui_res.get("word_enabled", WORD_ENABLED_DEFAULT)
            cfg.ocr_enabled = ui_res.get("text_check_enabled", TEXT_CHECK_ENABLED_DEFAULT) # Config expects text_check_enabled, let's fix this in next step or here?
            # Config defined as text_check_enabled field
            cfg.text_check_enabled = ui_res.get("text_check_enabled", TEXT_CHECK_ENABLED_DEFAULT)
            cfg.captcha_keywords = ui_res.get("captcha_keywords", CAPTCHA_KEYWORDS)
            cfg.not_found_keywords = ui_res.get("not_found_keywords", NOT_FOUND_KEYWORDS)
            cfg.bsmi_keywords = ui_res.get("bsmi_keywords", BSMI_KEYWORDS)
            cfg.login_keywords = ui_res.get("login_keywords", LOGIN_KEYWORDS)
            cfg.scroll_capture = ui_res.get("scroll_capture", SCROLL_CAPTURE_DEFAULT)
            
            capture_mode = ui_res.get("capture_mode", "window" if CAPTURE_ACTIVE_WINDOW_DEFAULT else "full")
            cfg.capture_window = (capture_mode == "window")
            
            cfg.crop_enabled = ui_res.get("crop_enabled", False)
            cfg.scroll_pagedown_times = ui_res.get("scroll_pagedown_times", SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT)
            cfg.crop_top_px = ui_res.get("crop_top_px", WEBPAGE_TOP_CROP_PX_DEFAULT)
            cfg.crop_bottom_px = ui_res.get("crop_bottom_px", WEBPAGE_BOTTOM_CROP_PX_DEFAULT)
            cfg.batch_size = ui_res["batch_size"]
            cfg.batch_rest_range = ui_res["batch_rest_range"]
        
        else:
            # Non-UI mode: ensure output directory is set if not provided
            if not cfg.output_dir:
                 cfg.output_dir = Path(default_output_dir_from_urls(cfg.urls_file))

        # 3. Run
        try:
            back_to_ui = run_capture(cfg)
            if args.ui and back_to_ui:
                continue
            return
        except Exception as exc:
            if args.ui:
                show_error_ui(str(exc))
                continue
            raise

if __name__ == "__main__":
    main()
