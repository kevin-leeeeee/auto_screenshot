import time
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable
from pathlib import Path

try:
    from docx import Document
except Exception:
    Document = None

from config import (
    BATCH_REST_RANGE,
    BATCH_SIZE,
    BSMI_KEYWORDS,
    CAPTCHA_KEYWORDS,
    CAPTURE_ACTIVE_WINDOW_DEFAULT,
    DONE_LOG,
    FINAL_COUNTDOWN_SECONDS,
    LOGIN_KEYWORDS,
    NOT_FOUND_KEYWORDS,
    TEXT_CHECK_ENABLED_DEFAULT,
    PAGE_WAIT_RANGE,
    PREFS_FILE,
    RECORD_OUTPUT_DEFAULT,
    SCROLL_CAPTURE_DEFAULT,
    SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT,
    WEBPAGE_BOTTOM_CROP_PX_DEFAULT,
    WEBPAGE_TOP_CROP_PX_DEFAULT,
    WORD_ENABLED_DEFAULT,
    TOOLTIP_ALPHA,
    load_prefs,
    save_prefs,
)
from utils_system import (
    clear_done_log,
    default_output_dir_from_urls,
    parse_keywords,
)

class OverlayUI:
    """
    Simple overlay window for countdown and status.
    """

    def __init__(
        self,
        on_stop: Callable[[], None] | None = None,
        should_stop: Callable[[], bool] | None = None,
        on_manual: Callable[[], None] | None = None,
        should_skip: Callable[[], bool] | None = None,
    ):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self._on_stop = on_stop
        self._should_stop = should_stop
        self._on_manual = on_manual
        self._should_skip = should_skip
        self._paused = False

        try:
            self.root.attributes("-alpha", 0.88)
        except Exception:
            pass

        self._margin = 10
        self._top = 30
        self._width = 520
        self._height = 170
        self._apply_geometry(self._width, self._height)

        frame = tk.Frame(self.root, bg="black")
        frame.pack(fill="both", expand=True)

        self.label = tk.Label(
            frame,
            text="",
            fg="white",
            bg="black",
            font=("Segoe UI", 12),
            justify="left",
            anchor="w",
            padx=12,
            pady=10,
        )
        self.label.pack(fill="both", expand=True)

        footer_row = tk.Frame(frame, bg="black")
        footer_row.pack(fill="x")

        self.footer = tk.Label(
            footer_row,
            text="",
            fg="#cccccc",
            bg="black",
            font=("Segoe UI", 10),
            anchor="w",
            padx=12,
            pady=4,
        )
        self.footer.pack(side="left", fill="x", expand=True)

        if self._on_manual:
            manual_btn = tk.Button(
                footer_row,
                text="截圖",
                command=self._on_manual,
                bg="#2f3a2f",
                fg="white",
                activebackground="#3a463a",
                activeforeground="white",
                relief="flat",
                padx=8,
                pady=2,
            )
            manual_btn.pack(side="right", padx=(0, 6), pady=4)

        self.pause_btn = tk.Button(
            footer_row,
            text="暫停",
            command=self._toggle_pause,
            bg="#2f2f3a",
            fg="white",
            activebackground="#3a3a46",
            activeforeground="white",
            relief="flat",
            padx=8,
            pady=2,
        )
        self.pause_btn.pack(side="right", padx=6, pady=4)

        if self._on_stop:
            btn = tk.Button(
                footer_row,
                text="停止",
                command=self._on_stop,
                bg="#333333",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=2,
            )
            btn.pack(side="right", padx=8, pady=4)

        self.root.withdraw()
        self._resize_to_content()
        self.root.update()

    def _toggle_pause(self):
        self._paused = not self._paused
        self.pause_btn.configure(text="繼續" if self._paused else "暫停")

    def set_paused(self, paused: bool):
        self._paused = paused
        self.pause_btn.configure(text="繼續" if self._paused else "暫停")

    def wait_if_paused(self) -> str | None:
        while self._paused:
            if self._should_stop and self._should_stop():
                return "stop"
            if self._should_skip and self._should_skip():
                return "skip"
            self.set_footer("已暫停，請按繼續")
            self.root.update()
            time.sleep(0.2)
        return None

    def _apply_geometry(self, width: int, height: int) -> None:
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(width, max(200, screen_w - self._margin * 2))
        height = min(height, max(120, screen_h - self._top - self._margin))
        x = max(self._margin, screen_w - width - self._margin)
        y = self._top
        self.root.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")
        self._width = width
        self._height = height

    def _resize_to_content(self, allow_shrink: bool = False) -> None:
        self.root.update_idletasks()
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        target_w = max(520, req_w)
        target_h = max(170, req_h)
        if not allow_shrink:
            target_w = max(target_w, self._width)
            target_h = max(target_h, self._height)
        if target_w != self._width or target_h != self._height:
            self._apply_geometry(target_w, target_h)

    def countdown_with_status(self, base_lines: list[str], total_seconds: int, final_seconds: int) -> str:
        if total_seconds <= 0:
            return "done"
        if final_seconds < 0:
            final_seconds = 0
        if final_seconds > total_seconds:
            final_seconds = total_seconds

        self.root.deiconify()
        self.root.lift()
        self.root.update()

        for t in range(total_seconds, 0, -1):
            pause_result = self.wait_if_paused()
            if pause_result == "stop":
                self.root.withdraw()
                self.root.update()
                return "stop"
            if pause_result == "skip":
                self.root.withdraw()
                self.root.update()
                return "skip"
            if self._should_stop and self._should_stop():
                self.root.withdraw()
                self.root.update()
                return "stop"
            if self._should_skip and self._should_skip():
                self.root.withdraw()
                self.root.update()
                return "skip"

            if t > final_seconds:
                status = f"頁面載入中，剩 {t} 秒"
            else:
                status = f"準備截圖，剩 {t} 秒"

            txt = "\n".join(base_lines + [status])
            self.label.config(text=txt)
            self._resize_to_content()
            self.root.update()
            time.sleep(1)

        self.root.withdraw()
        self.root.update()
        return "done"

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def show(self):
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.update()
        except Exception:
            pass

    def set_footer(self, text: str):
        self.footer.config(text=text)
        self.root.update()


def show_error_ui(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("錯誤", message)
    root.destroy()


def show_info_ui(title: str, message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self._tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self._tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() - 32
        tip = tk.Toplevel(self.widget)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        try:
            tip.attributes("-alpha", TOOLTIP_ALPHA)
        except Exception:
            pass
        label = tk.Label(
            tip,
            text=self.text,
            bg="#222222",
            fg="white",
            padx=8,
            pady=4,
            font=("Segoe UI", 9),
            wraplength=240,
            justify="left",
        )
        label.pack()
        tip.geometry(f"+{x}+{y}")
        self._tip = tip

    def _hide(self, _event=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None


class _SettingsUI:
    def __init__(self, default_urls_file: Path, default_output_dir: Path):
        self.root = tk.Tk()
        self.root.title("截圖設定")

        self.result = None
        self.output_manual = False
        self._ui_ready = False

        self.urls_var = tk.StringVar(value=str(default_urls_file))
        output_default = str(default_output_dir) if str(default_output_dir) else default_output_dir_from_urls(default_urls_file)
        self.output_var = tk.StringVar(value=output_default)

        self.page_min_var = tk.StringVar(value=str(PAGE_WAIT_RANGE[0]))
        self.page_max_var = tk.StringVar(value=str(PAGE_WAIT_RANGE[1]))
        self.final_var = tk.StringVar(value=str(FINAL_COUNTDOWN_SECONDS))
        self.record_output_var = tk.BooleanVar(value=RECORD_OUTPUT_DEFAULT)
        self.word_enabled_var = tk.BooleanVar(value=WORD_ENABLED_DEFAULT)
        self.text_check_enabled_var = tk.BooleanVar(value=TEXT_CHECK_ENABLED_DEFAULT)
        self.captcha_keywords_var = tk.StringVar(value=", ".join(CAPTCHA_KEYWORDS))
        self.not_found_keywords_var = tk.StringVar(value=", ".join(NOT_FOUND_KEYWORDS))
        self.bsmi_keywords_var = tk.StringVar(value=", ".join(BSMI_KEYWORDS))
        self.login_keywords_var = tk.StringVar(value=", ".join(LOGIN_KEYWORDS))
        self.keyword_settings_var = tk.BooleanVar(value=False)
        self.scroll_capture_var = tk.BooleanVar(value=SCROLL_CAPTURE_DEFAULT)
        self.capture_mode_var = tk.StringVar(value="window" if CAPTURE_ACTIVE_WINDOW_DEFAULT else "full")
        self.crop_enabled_var = tk.BooleanVar(value=False)
        self.scroll_pagedown_var = tk.StringVar(value=str(SCROLL_CAPTURE_PAGEDOWN_TIMES_DEFAULT))
        self.crop_top_var = tk.StringVar(value=str(WEBPAGE_TOP_CROP_PX_DEFAULT))
        self.crop_bottom_var = tk.StringVar(value=str(WEBPAGE_BOTTOM_CROP_PX_DEFAULT))
        self.batch_enabled_var = tk.BooleanVar(value=True)
        self.batch_size_var = tk.StringVar(value=str(BATCH_SIZE))
        self.rest_min_var = tk.StringVar(value=str(BATCH_REST_RANGE[0]))
        self.rest_max_var = tk.StringVar(value=str(BATCH_REST_RANGE[1]))

        self._apply_prefs(load_prefs(PREFS_FILE))
        self._build_ui()
        self.root.update_idletasks()
        req_w = max(560, self.root.winfo_reqwidth())
        req_h = max(460, self.root.winfo_reqheight())
        self.root.geometry(f"{req_w}x{req_h}")
        self.root.minsize(req_w, req_h)
        self.root.resizable(True, True)
        self._ui_ready = True

    def _build_ui(self):
        def add_row(row, label_text, widget):
            tk.Label(self.root, text=label_text, anchor="w").grid(row=row, column=0, sticky="w", padx=12, pady=6)
            widget.grid(row=row, column=1, sticky="we", padx=6, pady=6)

        self.root.grid_columnconfigure(1, weight=1)

        input_group = tk.LabelFrame(self.root, text="輸入設定", padx=8, pady=6)
        input_group.grid(row=0, column=0, columnspan=3, sticky="we", padx=12, pady=6)
        input_row = tk.Frame(input_group)
        input_row.pack(fill="x", pady=2)
        tk.Label(input_row, text="網址清單").pack(side="left")
        tk.Entry(input_row, textvariable=self.urls_var).pack(side="left", fill="x", expand=True, padx=8)
        tk.Button(input_row, text="瀏覽", command=self._choose_urls).pack(side="left")

        record_group = tk.LabelFrame(self.root, text="輸出設定", padx=8, pady=6)
        record_group.grid(row=2, column=0, columnspan=3, sticky="we", padx=12, pady=6)
        output_row = tk.Frame(record_group)
        output_row.pack(fill="x", pady=2)
        tk.Label(output_row, text="輸出資料夾").pack(side="left")
        tk.Entry(output_row, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=8)
        tk.Button(output_row, text="瀏覽", command=self._choose_output).pack(side="left")
        tk.Checkbutton(record_group, text="記錄輸出檔案 (done_urls.json)", variable=self.record_output_var).pack(anchor="w")
        tk.Button(record_group, text="清除所有紀錄", command=self._clear_output_records).pack(anchor="w", pady=(6, 0))
        self.word_checkbox = tk.Checkbutton(
            record_group,
            text="輸出 Word (.docx)",
            variable=self.word_enabled_var,
        )
        self.word_checkbox.pack(anchor="w", pady=(6, 0))
        Tooltip(self.word_checkbox, "每次產生新檔案，存於輸出資料夾")

        # --- Check Text Group (Renamed from OCR) ---
        ocr_group = tk.LabelFrame(self.root, text="文字檢查 (Ctrl+A)", padx=8, pady=6)
        ocr_group.grid(row=3, column=0, columnspan=3, sticky="we", padx=12, pady=6)
        
        ocr_toggle_row = tk.Frame(ocr_group)
        ocr_toggle_row.pack(anchor="w", pady=(0, 6), fill="x")
        
        ocr_toggle_inner = tk.Frame(ocr_toggle_row)
        ocr_toggle_inner.pack(anchor="w")
        
        ocr_toggle = tk.Checkbutton(ocr_toggle_inner, text="啟用文字檢查(自動暫停/跳過)", variable=self.text_check_enabled_var, command=self._toggle_text_check_controls)
        ocr_toggle.pack(side="left")
        
        self.keyword_block = tk.Frame(ocr_group)
        self.keyword_block.pack(fill="x")
        
        self.keyword_toggle = tk.Checkbutton(
            self.keyword_block,
            text="關鍵字設定",
            variable=self.keyword_settings_var,
            command=self._toggle_keyword_settings,
        )
        self.keyword_toggle.pack(anchor="w", pady=(6, 0))

        def add_kw_row(parent, label, var):
            row = tk.Frame(parent)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label).pack(side="left")
            entry = tk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=8)
            return entry

        self.keyword_frame = tk.Frame(self.keyword_block)
        self.captcha_entry = add_kw_row(self.keyword_frame, "驗證關鍵字", self.captcha_keywords_var)
        self.not_found_entry = add_kw_row(self.keyword_frame, "不存在關鍵字", self.not_found_keywords_var)
        self.bsmi_entry = add_kw_row(self.keyword_frame, "BSMI 關鍵字", self.bsmi_keywords_var)
        self.login_entry = add_kw_row(self.keyword_frame, "登入關鍵字", self.login_keywords_var)

        page_group = tk.LabelFrame(self.root, text="人性化", padx=8, pady=6)
        page_group.grid(row=4, column=0, columnspan=3, sticky="we", padx=12, pady=6)
        page_frame = tk.Frame(page_group)
        page_frame.pack(fill="x", pady=2)
        tk.Label(page_frame, text="每頁等待(秒)").pack(side="left")
        tk.Entry(page_frame, width=8, textvariable=self.page_min_var).pack(side="left", padx=8)
        tk.Label(page_frame, text="~").pack(side="left")
        tk.Entry(page_frame, width=8, textvariable=self.page_max_var).pack(side="left", padx=8)

        countdown_row = tk.Frame(page_group)
        countdown_row.pack(fill="x", pady=2)
        tk.Label(countdown_row, text="截圖倒數(秒)").pack(side="left")
        tk.Entry(countdown_row, width=10, textvariable=self.final_var).pack(side="left", padx=8)

        batch_toggle = tk.Checkbutton(
            page_group,
            text="啟用批次休息",
            variable=self.batch_enabled_var,
            command=self._toggle_batch_controls,
        )
        batch_toggle.pack(anchor="w", pady=(6, 0))

        self.batch_block = tk.Frame(page_group)
        self.batch_block.pack(fill="x")

        batch_size_row = tk.Frame(self.batch_block)
        batch_size_row.pack(fill="x", pady=4)
        tk.Label(batch_size_row, text="批次大小").pack(side="left")
        self.batch_size_entry = tk.Entry(batch_size_row, width=10, textvariable=self.batch_size_var)
        self.batch_size_entry.pack(side="left", padx=8)

        rest_frame = tk.Frame(self.batch_block)
        rest_frame.pack(fill="x", pady=4)
        tk.Label(rest_frame, text="批次休息(秒)").pack(side="left")
        self.rest_min_entry = tk.Entry(rest_frame, width=8, textvariable=self.rest_min_var)
        self.rest_min_entry.pack(side="left", padx=8)
        tk.Label(rest_frame, text="~").pack(side="left")
        self.rest_max_entry = tk.Entry(rest_frame, width=8, textvariable=self.rest_max_var)
        self.rest_max_entry.pack(side="left", padx=8)

        capture_group = tk.LabelFrame(self.root, text="截圖範圍", padx=8, pady=6)
        capture_group.grid(row=5, column=0, columnspan=3, sticky="we", padx=12, pady=6)
        capture_mode_row = tk.Frame(capture_group)
        capture_mode_row.pack(fill="x", pady=(0, 4))
        tk.Label(capture_mode_row, text="截圖模式").pack(side="left")
        tk.Radiobutton(
            capture_mode_row,
            text="全螢幕",
            value="full",
            variable=self.capture_mode_var,
            command=self._toggle_capture_controls,
        ).pack(side="left", padx=8)
        tk.Radiobutton(
            capture_mode_row,
            text="瀏覽器視窗",
            value="window",
            variable=self.capture_mode_var,
            command=self._toggle_capture_controls,
        ).pack(side="left", padx=8)
        self.scroll_block = tk.Frame(capture_group)
        self.scroll_block.pack(fill="x")
        self.scroll_toggle = tk.Checkbutton(
            self.scroll_block,
            text="捲動截圖",
            variable=self.scroll_capture_var,
            command=self._toggle_capture_controls,
        )
        self.scroll_toggle.pack(anchor="w")
        self.scroll_cfg = tk.Frame(self.scroll_block)
        self.scroll_cfg.pack(fill="x", pady=4)
        tk.Label(self.scroll_cfg, text="PageDown 次數").pack(side="left")
        self.scroll_pagedown_entry = tk.Entry(self.scroll_cfg, width=6, textvariable=self.scroll_pagedown_var)
        self.scroll_pagedown_entry.pack(side="left", padx=8)
        self.crop_block = tk.Frame(capture_group)
        self.crop_block.pack(fill="x")
        self.crop_toggle = tk.Checkbutton(
            self.crop_block,
            text="裁切",
            variable=self.crop_enabled_var,
            command=self._toggle_capture_controls,
        )
        self.crop_toggle.pack(anchor="w", pady=(4, 0))

        self.crop_cfg = tk.Frame(self.crop_block)
        self.crop_cfg.pack(fill="x", pady=4)
        tk.Label(self.crop_cfg, text="裁切上(像素)").pack(side="left")
        self.crop_top_entry = tk.Entry(self.crop_cfg, width=6, textvariable=self.crop_top_var)
        self.crop_top_entry.pack(side="left", padx=8)
        tk.Label(self.crop_cfg, text="裁切下(像素)").pack(side="left", padx=(12, 0))
        self.crop_bottom_entry = tk.Entry(self.crop_cfg, width=6, textvariable=self.crop_bottom_var)
        self.crop_bottom_entry.pack(side="left", padx=8)

        btn_row = tk.Frame(self.root)
        btn_row.grid(row=6, column=0, columnspan=3, pady=18)
        tk.Button(btn_row, text="開始", width=12, command=self._on_ok).pack(side="left", padx=10)
        tk.Button(btn_row, text="關閉", width=12, command=self._on_cancel).pack(side="left", padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self._toggle_batch_controls()
        self._toggle_capture_controls()
        self._toggle_text_check_controls()

    def _resize_window(self):
        if not self._ui_ready:
            return
        self.root.update_idletasks()
        req_w = max(560, self.root.winfo_reqwidth())
        req_h = max(460, self.root.winfo_reqheight())
        self.root.minsize(560, 460)
        self.root.geometry(f"{req_w}x{req_h}")

    def _toggle_batch_controls(self):
        enabled = self.batch_enabled_var.get()
        if enabled:
            self.batch_block.pack(fill="x")
        else:
            self.batch_block.pack_forget()
        self._resize_window()

    def _toggle_text_check_controls(self):
        if self.text_check_enabled_var.get():
            self.keyword_block.pack(fill="x")
        else:

            self.keyword_block.pack_forget()
        self._toggle_keyword_settings()
        self._resize_window()

    def _toggle_keyword_settings(self):
        enabled = self.text_check_enabled_var.get() and self.keyword_settings_var.get()
        state = "normal" if enabled else "disabled"
        if enabled:
            self.keyword_frame.pack(fill="x", pady=6)
        else:
            self.keyword_frame.pack_forget()
        self.captcha_entry.configure(state=state)
        self.not_found_entry.configure(state=state)
        self.bsmi_entry.configure(state=state)
        self.login_entry.configure(state=state)
        self._resize_window()

    def _toggle_capture_controls(self):
        if self.scroll_capture_var.get():
            self.scroll_cfg.pack(fill="x", pady=4)
        else:
            self.scroll_cfg.pack_forget()

        if self.crop_enabled_var.get():
            self.crop_cfg.pack(fill="x", pady=4)
        else:
            self.crop_cfg.pack_forget()
        self._resize_window()

    def _apply_prefs(self, prefs: dict):
        if not prefs:
            return
        if isinstance(prefs.get("urls_file"), str):
            self.urls_var.set(prefs["urls_file"])
        if isinstance(prefs.get("output_dir"), str):
            self.output_var.set(prefs["output_dir"])
            self.output_manual = prefs.get("output_manual", True)
        if isinstance(prefs.get("page_wait_range"), list) and len(prefs["page_wait_range"]) == 2:
            self.page_min_var.set(str(prefs["page_wait_range"][0]))
            self.page_max_var.set(str(prefs["page_wait_range"][1]))
        if "final_countdown" in prefs:
            self.final_var.set(str(prefs["final_countdown"]))
        if "record_output" in prefs:
            self.record_output_var.set(bool(prefs["record_output"]))
        if "word_enabled" in prefs:
            self.word_enabled_var.set(bool(prefs["word_enabled"]))
        if "ocr_enabled" in prefs:
            self.text_check_enabled_var.set(bool(prefs["ocr_enabled"]))
        elif "text_check_enabled" in prefs:
            self.text_check_enabled_var.set(bool(prefs["text_check_enabled"]))
        # tesseract_cmd load removed
        if isinstance(prefs.get("captcha_keywords"), str):
            self.captcha_keywords_var.set(prefs["captcha_keywords"])
        if isinstance(prefs.get("not_found_keywords"), str):
            self.not_found_keywords_var.set(prefs["not_found_keywords"])
        if isinstance(prefs.get("bsmi_keywords"), str):
            self.bsmi_keywords_var.set(prefs["bsmi_keywords"])
        if isinstance(prefs.get("login_keywords"), str):
            self.login_keywords_var.set(prefs["login_keywords"])
        if "keyword_settings" in prefs:
            self.keyword_settings_var.set(bool(prefs["keyword_settings"]))
        if "scroll_capture" in prefs:
            self.scroll_capture_var.set(bool(prefs["scroll_capture"]))
        if "capture_mode" in prefs and prefs["capture_mode"] in ("full", "window"):
            self.capture_mode_var.set(prefs["capture_mode"])
        elif "capture_window" in prefs:
            self.capture_mode_var.set("window" if prefs["capture_window"] else "full")
        if "crop_enabled" in prefs:
            self.crop_enabled_var.set(bool(prefs["crop_enabled"]))
        if "scroll_pagedown_times" in prefs:
            self.scroll_pagedown_var.set(str(prefs["scroll_pagedown_times"]))
        if "crop_top_px" in prefs:
            self.crop_top_var.set(str(prefs["crop_top_px"]))
        if "crop_bottom_px" in prefs:
            self.crop_bottom_var.set(str(prefs["crop_bottom_px"]))
        if "batch_enabled" in prefs:
            self.batch_enabled_var.set(bool(prefs["batch_enabled"]))
        if "batch_size" in prefs:
            self.batch_size_var.set(str(prefs["batch_size"]))
        if isinstance(prefs.get("batch_rest_range"), list) and len(prefs["batch_rest_range"]) == 2:
            self.rest_min_var.set(str(prefs["batch_rest_range"][0]))
            self.rest_max_var.set(str(prefs["batch_rest_range"][1]))

    def update_defaults(self, default_urls_file: Path, default_output_dir: Path):
        if not self.urls_var.get().strip():
            self.urls_var.set(str(default_urls_file))
        if not self.output_manual:
            output_default = str(default_output_dir) if str(default_output_dir) else default_output_dir_from_urls(default_urls_file)
            self.output_var.set(output_default)

    def _choose_urls(self):
        current = self.urls_var.get().strip()
        initialdir = None
        if not current:
            initialdir = str(Path.cwd())
        else:
            p = Path(current)
            if p.exists():
                initialdir = str(p.parent)

        path = filedialog.askopenfilename(
            title="選擇網址清單",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=initialdir,
        )
        if path:
            self.urls_var.set(path)
            if not self.output_manual:
                self.output_var.set(default_output_dir_from_urls(path))

    def _choose_output(self):
        current = self.output_var.get().strip()
        initialdir = None
        if not current:
            initialdir = str(Path.cwd())
        else:
            p = Path(current)
            if p.exists():
                initialdir = str(p)

        path = filedialog.askdirectory(title="選擇輸出資料夾", initialdir=initialdir)
        if path:
            self.output_var.set(path)
            self.output_manual = True

    def _clear_output_records(self):
        done_log = Path(DONE_LOG)
        if not done_log.exists():
            messagebox.showinfo("提示", "找不到 done_urls.json，沒有可清除的紀錄。")
            return

        if not messagebox.askyesno("確認", "要清除 done_urls.json 中的所有紀錄嗎？"):
            return

        changed = clear_done_log(done_log)
        if not changed:
            messagebox.showinfo("提示", "找不到 done_urls.json，沒有可清除的紀錄。")
            return
        messagebox.showinfo("完成", "已清除所有紀錄。")

    def _parse_int(self, name: str, var: tk.StringVar) -> int:
        raw = var.get().strip()
        if not raw:
            raise ValueError(f"{name} 不可為空")
        return int(raw)

    def _on_ok(self):
        try:
            page_min = self._parse_int("每頁等待(最小)", self.page_min_var)
            page_max = self._parse_int("每頁等待(最大)", self.page_max_var)
            final_countdown = self._parse_int("截圖倒數", self.final_var)
            record_output = self.record_output_var.get()
            word_enabled = self.word_enabled_var.get()
            text_check_enabled = self.text_check_enabled_var.get()
            # tesseract_cmd removed
            captcha_keywords = parse_keywords(self.captcha_keywords_var.get())
            not_found_keywords = parse_keywords(self.not_found_keywords_var.get())
            bsmi_keywords = parse_keywords(self.bsmi_keywords_var.get())
            login_keywords = parse_keywords(self.login_keywords_var.get())
            scroll_capture = self.scroll_capture_var.get()
            capture_mode = self.capture_mode_var.get()
            crop_enabled = self.crop_enabled_var.get()
            scroll_pagedown_times = self._parse_int("PageDown 次數", self.scroll_pagedown_var)
            crop_top_px = self._parse_int("裁切上(像素)", self.crop_top_var)
            crop_bottom_px = self._parse_int("裁切下(像素)", self.crop_bottom_var)
            batch_enabled = self.batch_enabled_var.get()
            batch_size = self._parse_int("批次大小", self.batch_size_var) if batch_enabled else 0
            rest_min = self._parse_int("批次休息(最小)", self.rest_min_var) if batch_enabled else 0
            rest_max = self._parse_int("批次休息(最大)", self.rest_max_var) if batch_enabled else 0

            # Create a temporary config to validate logic
            # Note: We need to handle dependencies like Document/PIL check separately if they are not in RunConfig validation
            if word_enabled and Document is None:
                raise ValueError("Word 輸出需要 python-docx，請先安裝")

            # Use RunConfig to validate the rest
            from config import RunConfig
            test_cfg = RunConfig(
                page_wait_range=(page_min, page_max),
                final_countdown=final_countdown,
                batch_size=batch_size,
                batch_rest_range=(rest_min, rest_max),
                scroll_pagedown_times=scroll_pagedown_times,
                crop_enabled=crop_enabled,
                crop_top_px=crop_top_px,
                crop_bottom_px=crop_bottom_px,
                scroll_capture=scroll_capture,
                text_check_enabled=text_check_enabled,
                captcha_keywords=captcha_keywords,
                not_found_keywords=not_found_keywords,
                bsmi_keywords=bsmi_keywords,
                login_keywords=login_keywords,
            )
            test_cfg.validate()

        except Exception as exc:
            messagebox.showerror("錯誤", str(exc))
            return

        self.result = {
            "urls_file": self.urls_var.get().strip(),
            "output_dir": self.output_var.get().strip(),
            "page_wait_range": (page_min, page_max),
            "final_countdown": final_countdown,
            "record_output": record_output,
            "word_enabled": word_enabled,
            "text_check_enabled": text_check_enabled,
            # "tesseract_cmd" removed
            "captcha_keywords": captcha_keywords,
            "not_found_keywords": not_found_keywords,
            "bsmi_keywords": bsmi_keywords,
            "login_keywords": login_keywords,
            "scroll_capture": scroll_capture,
            "capture_mode": capture_mode,
            "crop_enabled": crop_enabled,
            "scroll_pagedown_times": scroll_pagedown_times,
            "crop_top_px": crop_top_px,
            "crop_bottom_px": crop_bottom_px,
            "batch_size": batch_size,
            "batch_rest_range": (rest_min, rest_max),
        }
        save_prefs(
            PREFS_FILE,
            {
                "urls_file": self.urls_var.get().strip(),
                "output_dir": self.output_var.get().strip(),
                "output_manual": self.output_manual,
                "page_wait_range": [self.page_min_var.get().strip(), self.page_max_var.get().strip()],
                "final_countdown": self.final_var.get().strip(),
                "record_output": self.record_output_var.get(),
                "word_enabled": self.word_enabled_var.get(),
                # Store as both for backward compatibility or just new? Let's strictly use new key but load old
                "text_check_enabled": self.text_check_enabled_var.get(),
                # "tesseract_cmd" removed
                "captcha_keywords": self.captcha_keywords_var.get().strip(),
                "not_found_keywords": self.not_found_keywords_var.get().strip(),
                "bsmi_keywords": self.bsmi_keywords_var.get().strip(),
                "login_keywords": self.login_keywords_var.get().strip(),
                "keyword_settings": self.keyword_settings_var.get(),
                "scroll_capture": self.scroll_capture_var.get(),
                "capture_mode": self.capture_mode_var.get(),
                "crop_enabled": self.crop_enabled_var.get(),
                "scroll_pagedown_times": self.scroll_pagedown_var.get().strip(),
                "crop_top_px": self.crop_top_var.get().strip(),
                "crop_bottom_px": self.crop_bottom_var.get().strip(),
                "batch_enabled": self.batch_enabled_var.get(),
                "batch_size": self.batch_size_var.get().strip(),
                "batch_rest_range": [self.rest_min_var.get().strip(), self.rest_max_var.get().strip()],
            },
        )
        self.root.withdraw()
        self.root.quit()

    def _on_cancel(self):
        self.result = None
        self.root.withdraw()
        self.root.quit()

    def show(self) -> dict | None:
        self.result = None
        self.root.deiconify()
        self.root.lift()
        self.root.mainloop()
        return self.result


_settings_ui: _SettingsUI | None = None


def ui_collect_settings(default_urls_file: Path, default_output_dir: Path) -> dict | None:
    global _settings_ui
    if _settings_ui is None:
        _settings_ui = _SettingsUI(default_urls_file, default_output_dir)
    else:
        _settings_ui.update_defaults(default_urls_file, default_output_dir)
    return _settings_ui.show()
