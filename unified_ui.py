import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import threading
from pathlib import Path
import sys
import datetime

# 將各子目錄路徑加入系統路徑，以便導入模組
BASE_DIR = Path(__file__).parent.absolute()
EXCEL_DIR = BASE_DIR / "excel_轉換"
SCREENSHOT_DIR = BASE_DIR / "截圖腳本"

sys.path.append(str(EXCEL_DIR))
sys.path.append(str(SCREENSHOT_DIR))

# 嘗試導入現有功能函數（如果結構允許直接調用）
try:
    from convert_excel import main as run_excel_convert, select_file as excel_select_file
except ImportError:
    run_excel_convert = None
    excel_select_file = None

try:
    # 這裡的導入可能需要根據實際 main.py 的結構調整
    # 假設我們可以用子進程啟動以避免 GUI 衝突
    pass
except ImportError:
    pass

class UnifiedDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("工作自動化控制中心 v1.0.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 設置樣式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        
        self._build_ui()

    def _build_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # 標題
        title_label = ttk.Label(main_frame, text="工作自動化控制中心", style="Header.TLabel")
        title_label.pack(pady=(0, 20))

        # --- 1. Excel 轉換區 ---
        excel_frame = ttk.LabelFrame(main_frame, text=" 資料預處理 (Excel 轉換) ", padding=10)
        excel_frame.pack(fill="x", pady=10)

        self.excel_path_var = tk.StringVar(value="尚未選取 Excel 檔案")
        excel_path_entry = ttk.Entry(excel_frame, textvariable=self.excel_path_var, state="readonly")
        excel_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_convert = ttk.Button(excel_frame, text="瀏覽並轉換", command=self.handle_excel_convert)
        btn_convert.pack(side="right")

        # --- 2. 自動截圖區 ---
        screenshot_frame = ttk.LabelFrame(main_frame, text=" 自動化截圖任務 ", padding=10)
        screenshot_frame.pack(fill="x", pady=10)

        btn_row_1 = tk.Frame(screenshot_frame)
        btn_row_1.pack(fill="x", pady=5)
        
        btn_config = ttk.Button(btn_row_1, text="開啟設定視窗", command=self.handle_open_config)
        btn_config.pack(side="left", fill="x", expand=True, padx=5)

        btn_start = ttk.Button(btn_row_1, text="啟動自動截圖", command=self.handle_start_screenshot)
        btn_start.pack(side="left", fill="x", expand=True, padx=5)

        # 進度條 (預留功能)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(screenshot_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=10)
        
        self.status_var = tk.StringVar(value="狀態：就緒")
        status_label = ttk.Label(screenshot_frame, text="狀態：就緒", textvariable=self.status_var)
        status_label.pack(anchor="w")

        # --- 3. 快速鏈結區 ---
        link_frame = ttk.LabelFrame(main_frame, text=" 工具與檔案管理 ", padding=10)
        link_frame.pack(fill="x", pady=10)

        btn_view_excel = ttk.Button(link_frame, text="開啟 Excel 產出", command=lambda: self.open_folder(EXCEL_DIR / "output"))
        btn_view_excel.pack(side="left", fill="x", expand=True, padx=5)

        btn_view_ss = ttk.Button(link_frame, text="開啟截圖資料夾", command=lambda: self.open_folder(SCREENSHOT_DIR / "screenshots_urls"))
        btn_view_ss.pack(side="left", fill="x", expand=True, padx=5)

        btn_view_log = ttk.Button(link_frame, text="查看日誌", command=self.handle_view_logs)
        btn_view_log.pack(side="left", fill="x", expand=True, padx=5)

    def handle_excel_convert(self):
        """處理 Excel 轉換邏輯"""
        # 使用子線程避免 GUI 凍結
        def task():
            try:
                # 這裡直接呼叫 convert_excel.py 的邏輯
                # 由於 convert_excel.py 原本就有 select_file GUI，我們直接利用它
                self.status_var.set("狀態：正在選擇檔案...")
                # 我們可以在此手動執行 convert_excel.py 以確保獨立性
                cmd = [sys.executable, str(EXCEL_DIR / "convert_excel.py")]
                process = subprocess.Popen(cmd, cwd=str(EXCEL_DIR))
                process.wait()
                
                self.status_var.set("狀態：Excel 轉換處理完成")
                messagebox.showinfo("完成", "Excel 轉換任務已結束。")
            except Exception as e:
                messagebox.showerror("錯誤", f"執行轉換時發生錯誤：{e}")
                self.status_var.set("狀態：發生錯誤")

        threading.Thread(target=task, daemon=True).start()

    def handle_open_config(self):
        """開啟截圖設定視窗"""
        try:
            # 啟動截圖腳本的 UI
            cmd = [sys.executable, str(SCREENSHOT_DIR / "main.py"), "--config-only"] # 假設我們增加一個參數只開設定
            # 或者直接啟動目前的 main.py，它預設是先開設定
            subprocess.Popen([sys.executable, str(SCREENSHOT_DIR / "main.py")], cwd=str(SCREENSHOT_DIR))
            self.status_var.set("狀態：設定視窗已開啟")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟設定：{e}")

    def handle_start_screenshot(self):
        """啟動自動截圖腳本"""
        # 啟動截圖腳本的邏輯 (通常是 main.py)
        # 考慮到 main.py 已經有自己的 GUI 循環，最好的整合方式是直接呼叫它
        try:
            subprocess.Popen([sys.executable, str(SCREENSHOT_DIR / "main.py")], cwd=str(SCREENSHOT_DIR))
            self.status_var.set("狀態：自動截圖任務啟動中")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法啟動截圖：{e}")

    def handle_view_logs(self):
        """查看日誌檔案"""
        log_dir = SCREENSHOT_DIR / "logs"
        if not log_dir.exists():
            messagebox.showwarning("提示", "目前尚未產生任何日誌。")
            return
        
        # 取得最新的一個 log 檔案
        logs = list(log_dir.glob("*.log"))
        if not logs:
            messagebox.showwarning("提示", "日誌資料夾為空。")
            return
            
        latest_log = max(logs, key=os.path.getmtime)
        try:
            os.startfile(latest_log)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟日誌：{e}")

    def open_folder(self, path):
        """在檔案總管中開啟路徑"""
        if not path.exists():
            messagebox.showwarning("提示", f"路徑不存在：{path}")
            return
        os.startfile(path)

if __name__ == "__main__":
    # 解決高 DPI 模糊問題
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = UnifiedDashboard(root)
    root.mainloop()
