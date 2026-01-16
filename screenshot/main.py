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
    def __init__(self, *args, **kwargs): 
        pass
    
    def set_paused(self, paused: bool): 
        pass
    
    def wait_if_paused(self) -> str | None: 
        return None
    
    def set_footer(self, text: str): 
        pass
    
    def show(self): 
        pass
    
    def close(self): 
        pass
    
    def countdown_with_status(self, base_lines: list[str], total_seconds: int, final_seconds: int) -> str:
        """Simulate countdown by sleeping"""
        import time
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
    Check for login/captcha/not found pages based on priority order.
    Returns: (classification_result, should_stop, should_skip)
    """
    if not cfg.text_check_enabled:
        return None, False, False

    # 進行文字檢查 (Ctrl+A)
    extracted_text = extract_text_content()
    if not extracted_text:
        return "無法判斷", False, False

    from utils_image import normalize_text
    t = normalize_text(extracted_text[:min(2000, len(extracted_text))])

    # 定義類別與其關鍵字/邏輯的映射
    # 注意：這裡的 Key 必須與前端傳來的 cfg.keywords 內容一致
    category_logic = {
        "登入": {
            "keywords": cfg.login_keywords,
            "pause_msg": "偵測到登入頁面，請登入後按繼續",
            "footer": "偵測到登入頁面"
        },
        "拼圖與人機驗證": {
            "keywords": cfg.captcha_keywords,
            "pause_msg": "偵測到驗證碼或拼圖，請處理後按繼續",
            "footer": "偵測到驗證碼/拼圖"
        },
        "查無資料": {
            "keywords": cfg.not_found_keywords,
            "is_skip": True,
            "footer": "查無資料"
        },
        "BSMI": {
            "keywords": cfg.bsmi_keywords,
            "footer": "偵測到 BSMI"
        }
    }

    # 取得優先順序 (優先讀取前端傳來的順序)
    priority_order = getattr(cfg, "keywords", None)
    if not priority_order:
        priority_order = ["登入", "拼圖與人機驗證", "查無資料", "BSMI"]
    
    # 確保 priority_order 是列表（防止 None 或其它類型導致循環報錯）
    if not isinstance(priority_order, list):
        priority_order = ["登入", "拼圖與人機驗證", "查無資料", "BSMI"]


    detected_cls = None
    
    # 依照優先順序循環檢查
    for cat_name in priority_order:
        # 1. 檢查預設類別
        if cat_name in category_logic:
            logic = category_logic[cat_name]
            kws = logic.get("keywords", [])
            if any(normalize_text(k) in t for k in kws):
                detected_cls = cat_name
                break
        
        # 2. 檢查自訂類別
        elif cfg.custom_categories and cat_name in cfg.custom_categories:
            kws = cfg.custom_categories[cat_name]
            if any(normalize_text(k) in t for k in kws):
                detected_cls = cat_name
                break

    if not detected_cls:
        # Standard page behavior
        click_window_corner("bottom_left")
        time.sleep(0.05)
        pyautogui.press("esc")
        return "無法判斷", False, False

    logger.info(f"  優先權判定結果: {detected_cls}")

    # --- 暫停邏輯 ---
    should_pause = False
    if cfg.category_pause:
        should_pause = cfg.category_pause.get(detected_cls, False)
    else:
        # 相容舊版預設
        should_pause = detected_cls in ["登入", "拼圖與人機驗證"]

    if should_pause:
        logger.warning(f"Detected {detected_cls}. Pausing for manual intervention...")
        logic = category_logic.get(detected_cls, {})
        msg = logic.get("pause_msg", f"偵測到 {detected_cls}，請處理後按繼續")
        
        overlay.set_footer(msg)
        overlay.set_paused(True)
        overlay.show()
        if overlay.wait_if_paused() == "stop":
            return detected_cls, True, False
        overlay.set_footer("")

    # --- 預設行為 (跳過或繼續) ---
    if detected_cls == "查無資料":
        logger.warning("No data found. Skipping...")
        return detected_cls, False, True
    
    # 正常頁面微調
    click_window_corner("bottom_left")
    time.sleep(0.05)
    pyautogui.press("esc")
    
    return detected_cls, False, False




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
                scroll_stitch=cfg.scroll_stitch,
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


def run_capture(cfg: RunConfig, external_stop_callback=None, progress_callback=None, use_overlay=True, suppress_popups=False, input_files=None) -> dict:
    """ 主要執行流程。 """
    
    # Auto-correct output_dir if it points to a specific screenshot folder (prevents nesting)
    if cfg.output_dir.name.startswith("screenshots_"):
        logger.info(f"Detected sub-folder in output path ({cfg.output_dir.name}), moving up one level to prevent nesting.")
        cfg.output_dir = cfg.output_dir.parent
        
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aggregate URLs and track source files
    urls = []
    url_to_source_file = {}  # Map URL to its source file for Word generation
    
    if input_files:
        for f in input_files:
            file_urls = load_urls(Path(f))
            urls.extend(file_urls)
            # Track which file each URL came from
            for url_tuple in file_urls:
                url_to_source_file[url_tuple[0]] = Path(f)
    else:
        urls = load_urls(cfg.urls_file)
        for url_tuple in urls:
            url_to_source_file[url_tuple[0]] = cfg.urls_file
        
    if not urls:
        raise RuntimeError(f"沒有網址可供處理,請檢查輸入內容。")

    # Tracking results for API
    run_results = {
        "processed": 0,
        "errors": [],
        "results": [],
        "back_to_ui": False,
        "word_documents": []  # Track all generated Word documents
    }
    
    # Setup Word documents - one per source file
    word_docs = {}  # Map source file path to (Document, final_path)
    if cfg.word_enabled:
        if Document is None:
            logger.info("Word export requires python-docx; skipping.")
        else:
            # Create a Word document for each unique source file
            unique_files = set(url_to_source_file.values())
            for source_file in unique_files:
                word_path = new_word_path(cfg.output_dir, source_file, cfg.word_path)
                word_path.parent.mkdir(parents=True, exist_ok=True)
                doc = Document()
                doc.save(word_path)
                word_docs[source_file] = (doc, word_path)
                run_results["word_documents"].append(str(word_path))
                print(f"Word file: {word_path}")

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
            progress_callback(0, total, "開始處理")

        for idx, (url, note) in enumerate(urls, start=1):
            if progress_callback:
                progress_callback(processed_this_run, total, f"處理中 ({processed_this_run}/{total})")

            if stop_requested["flag"]:
                flush_done(force=True)
                overlay.set_footer("已停止")
                run_results["back_to_ui"] = True
                return run_results
            
            # Check pause at start of loop
            if overlay.wait_if_paused() == "stop":
                flush_done(force=True)
                overlay.set_footer("已停止")
                run_results["back_to_ui"] = True
                return run_results

            if cfg.skip_done and url in done:
                skipped_this_run += 1
                continue

            url_short = short_url(url)
            
            # --- Single URL Processing Loop (Retry Logic) ---
            max_retries = 3  # Maximum retry attempts per URL
            retry_count = 0
            
            while retry_count < max_retries:
                logger.info(f"[{idx}/{total}] Processing {url_short} (Attempt {retry_count + 1}/{max_retries})")
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
                    run_results["back_to_ui"] = True
                    return run_results
                if result == "skip":
                    overlay.set_footer("手動截圖")

                time.sleep(UI_HIDE_BUFFER_SECONDS)

                # --- Page Checks (OCR) ---
                cls, should_stop, should_skip_url = handle_page_checks(cfg, overlay)
                if should_stop:
                    flush_done(force=True)
                    overlay.set_footer("已停止")
                    run_results["back_to_ui"] = True
                    return run_results
                
                if should_skip_url:
                    # e.g. Product Not Found
                    done.add(url)
                    if cfg.text_check_enabled and cls is not None:
                        done_classes[url] = cls
                    done_dirty = True
                    break  # Exit retry loop, move to next URL

                # If login/captcha detected and user resolved it, retry
                if cls in ["登入", "拼圖與人機驗證"]:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"  Retrying after {cls} resolution...")
                        time.sleep(2)  # Brief pause before retry
                        continue
                    else:
                        logger.warning(f"  Max retries reached for {url_short}")
                        break

                # --- Capture ---
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{idx:03d}_{ts}_{safe_filename(url)}.png"
                # Use source file to influence output directory (group by file)
                if url in url_to_source_file:
                    src_f = url_to_source_file[url]
                    f_stem = src_f.stem
                    sub_d = f"screenshots_{f_stem}"
                    
                    if cfg.output_dir.name == sub_d:
                        target_d = cfg.output_dir
                    else:
                        target_d = cfg.output_dir / sub_d
                        target_d.mkdir(parents=True, exist_ok=True)
                    outpath = target_d / fname
                    
                    # Update output_subdir for API results so folder open works correctly
                    # Note: We can't easily update run_results here, but 'folder' logic in core/main.py 
                    # relies on 'output_subdir'. But Wait! output_subdir is derived from outpath.parent.name later.
                    # Or run_results["results"].append uses outpath.parent.name. Perfect.
                else:
                    outpath = cfg.output_dir / fname

                img, used_window = capture_image(cfg, outpath)
                
                if img is None:
                    overlay.set_footer("截圖失敗")
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"  Capture failed, retrying... ({retry_count}/{max_retries})")
                        time.sleep(1)
                        continue
                    else:
                        logger.error(f"  Max retries reached, skipping {url_short}")
                        break

                try:
                    img.save(outpath)
                    logger.info(f"  Saved: {outpath}")
                    overlay.set_footer("截圖完成")
                    
                    if cfg.text_check_enabled and cls is not None:
                        done_classes[url] = cls
                    
                    done.add(url)
                    if cfg.record_output:
                        done_outputs[url] = str(outpath)
                    
                    # Append to the correct Word document for this URL's source file
                    if word_docs and url in url_to_source_file:
                        source_file = url_to_source_file[url]
                        if source_file in word_docs:
                            word_doc, word_path = word_docs[source_file]
                            try:
                                append_to_word(word_doc, word_path, url, outpath, note)
                            except Exception as e:
                                logger.error(f"Word export error: {e}")
                    
                    done_dirty = True
                    
                    # Record result
                    run_results["results"].append({
                        "url": url,
                        "status": "success",
                        "output": str(outpath),
                        "output_subdir": outpath.parent.name,
                        "classification": cls
                    })
                    run_results["processed"] += 1
                    
                    # Release image from memory
                    del img
                    
                    break  # Success, exit retry loop

                except Exception as exc:
                    logger.error(f"Save failed: {exc}")
                    overlay.set_footer(f"儲存失敗: {exc}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(1)
                        continue
                    else:
                        break

            # End While (Single URL)
            
            processed_this_run += 1
            if cfg.batch_size > 0 and processed_this_run > 0 and processed_this_run % cfg.batch_size == 0:
                flush_done()
                sleep_random(cfg.batch_rest_range, f"批次休息（每 {cfg.batch_size} 個）")

        # End For (URLs)
        
        logger.info("Run finished.")
        logger.info(f"Completed: {processed_this_run}, Skipped: {skipped_this_run}")
        if progress_callback:
            progress_callback(processed_this_run, total, "完成")
        overlay.set_footer("完成")
        if not suppress_popups:
            show_info_ui("完成", f"本次完成 {processed_this_run} 個，跳過 {skipped_this_run} 個。")

    except KeyboardInterrupt:
        flush_done(force=True)
        logger.info("\n已中止（Ctrl+C）。已保存 done_log。")
        overlay.set_footer("已停止")
        run_results["back_to_ui"] = True
        return run_results
    except Exception:
        flush_done(force=True)
        logger.exception("Unexpected error")
        overlay.set_footer("發生錯誤，請查看 Log")
        if cfg.output_dir: 
             show_error_ui("發生未預期的錯誤，請查看 logs/app.log")
        run_results["back_to_ui"] = True
        return run_results
    finally:
        flush_done(force=True)
        overlay.close()
    
    return run_results


def run_from_api(should_stop_callback, config_overrides=None, progress_callback=None, suppress_popups=False):
    """
    Entry point for API/Server to run the capture process.
    should_stop_callback: a callable that returns True if we should abort.
    config_overrides: dict of configuration options from UI
    """
    if config_overrides is None:
        config_overrides = {}

    # 1. Resolve URLs - Handle multiple files
    all_urls = []
    input_files = config_overrides.get("input_files", [])
    
    if not input_files:
        # Fallback to single urls_file if no list provided
        urls_file_raw = config_overrides.get("urls_file", DEFAULT_URLS_FILE)
        input_files = [urls_file_raw]
    
    # Actually, load_urls expects a Path. We can merge URLs here or update RunConfig.
    # RUN_CAPTURE currently expects a cfg.urls_file to exist for Word naming etc.
    # Let's use the first file as the "primary" for naming.
    primary_urls_file = Path(input_files[0]).resolve() if input_files else Path(DEFAULT_URLS_FILE).resolve()
    
    # 2. Resolve Output Dir
    if config_overrides.get("output_dir"):
         output_dir = Path(config_overrides["output_dir"]).resolve()
    else:
         output_dir = Path(default_output_dir_from_urls(primary_urls_file)).resolve()
    
    # Base config
    cfg = RunConfig(
        urls_file=primary_urls_file,
        output_dir=output_dir,
        done_log=Path(DONE_LOG).resolve(),
        warmup_enabled=WARM_UP_ENABLED,
        word_enabled=WORD_ENABLED_DEFAULT,
    )

    # 3. Handle multiple files by injecting a "merged" urls list if we had a way,
    # or just calling run_capture with a temporary combined file.
    # Simpler: Add 'input_files' support to run_capture or just pass them as overrides.
    # For now, let's keep it simple: run_capture will be modified to accept 'urls' as an optional list.
    
    # Apply overrides
    if "autoWordExport" in config_overrides:
        cfg.word_enabled = config_overrides["autoWordExport"]
    if "auto_word_export" in config_overrides:
        cfg.word_enabled = config_overrides["auto_word_export"]
    if "skip_done" in config_overrides:
        cfg.skip_done = config_overrides["skip_done"]
    if "text_check_enabled" in config_overrides: # Mapping frontend name
        cfg.text_check_enabled = config_overrides["text_check_enabled"]
    if "check_text" in config_overrides: # Another mapping
        cfg.text_check_enabled = config_overrides["check_text"]
    if "scroll_capture" in config_overrides:
        cfg.scroll_capture = config_overrides["scroll_capture"]
    if "scroll_stitch" in config_overrides:
        cfg.scroll_stitch = config_overrides["scroll_stitch"]
    if "crop_top" in config_overrides:
        cfg.crop_top_px = int(config_overrides["crop_top"])
        cfg.crop_enabled = True
    if "crop_bottom" in config_overrides:
        cfg.crop_bottom_px = int(config_overrides["crop_bottom"])
        cfg.crop_enabled = True
    if "wait_min" in config_overrides and "wait_max" in config_overrides:
        cfg.page_wait_range = (int(config_overrides["wait_min"]), int(config_overrides["wait_max"]))

    # Mapping keywords
    if "captcha_keywords" in config_overrides: cfg.captcha_keywords = config_overrides["captcha_keywords"]
    if "not_found_keywords" in config_overrides: cfg.not_found_keywords = config_overrides["not_found_keywords"]
    if "bsmi_keywords" in config_overrides: cfg.bsmi_keywords = config_overrides["bsmi_keywords"]
    if "login_keywords" in config_overrides: cfg.login_keywords = config_overrides["login_keywords"]
    if "category_pause" in config_overrides: cfg.category_pause = config_overrides["category_pause"]

    # We modify run_capture to take an optional 'input_files' or aggregated urls
    try:
        results = run_capture(
            cfg, 
            external_stop_callback=should_stop_callback, 
            progress_callback=progress_callback, 
            use_overlay=True, 
            suppress_popups=suppress_popups,
            input_files=input_files
        )
        # Note: run_capture now returns a dict of results (processed, errors, results_list)
        return results
    except Exception as e:
        logger.error(f"Error in run_from_api: {e}")
        raise




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
