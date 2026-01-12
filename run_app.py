import webview
import threading
import sys
import os
from pathlib import Path
from flask import Flask, send_from_directory

# Backend script paths
BASE_DIR = Path(__file__).parent.absolute()
EXCEL_DIR = BASE_DIR / "excel_轉換"
SCREENSHOT_DIR = BASE_DIR / "截圖腳本"
DIST_DIR = BASE_DIR / "autoflow-control-center" / "dist"

sys.path.append(str(EXCEL_DIR))
sys.path.append(str(SCREENSHOT_DIR))

# Mock System State for Bridge
class Bridge:
    def __init__(self):
        self._window = None
        self._screenshot_stop_signal: bool = False
        self._current_excel_path: str | None = None
        self._task_status: dict = {
            "processed": 0, 
            "total": 0, 
            "status": "idle" # idle, running, error
        }
        self._latest_output_folder: str | None = None
        self._latest_screenshot_folder: str | None = None
        self._latest_screenshot_results: list = []
        self._data_file: Path = BASE_DIR / "app_data.json"
        self._init_data()

    def _init_data(self):
        import json
        if not self._data_file.exists():
            initial_data = {
                "stats": {
                    "total_conversions": 0,
                    "total_tasks": 0,
                    "success_rate": "100%",
                    "time_saved": "0h"
                },
                "history": []
            }
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=4, ensure_ascii=False)

    def _load_data(self):
        import json
        default_stats = {
            "total_conversions": 0,
            "total_tasks": 0,
            "success_rate": "100%",
            "time_saved": "0h"
        }
        try:
            if self._data_file.exists():
                with open(self._data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "stats" not in data: data["stats"] = default_stats
                    if "history" not in data: data["history"] = []
                    # Ensure all stats keys exist
                    for k, v in default_stats.items():
                        if k not in data["stats"]: data["stats"][k] = v
                    return data
        except:
            pass
        return {"stats": default_stats, "history": []}

    def _save_data(self, data):
        import json
        with open(self._data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def clear_history(self):
        data = self._load_data()
        data["history"] = []
        data["stats"] = {
            "total_conversions": 0,
            "total_tasks": 0,
            "success_rate": "100%",
            "time_saved": "0s",
            "total_seconds": 0.0
        }
        self._save_data(data)
        return {"status": "success", "message": "歷史紀錄與統計數據已清除"}

    def export_history(self):
        import tkinter as tk
        from tkinter import filedialog
        import csv
        
        data = self._load_data()
        if not data["history"]:
            return {"status": "error", "message": "沒有可導出的紀錄"}
            
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"autoflow_history.csv"
        )
        root.destroy()
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "name", "status", "duration", "time", "message"])
                    writer.writeheader()
                    writer.writerows(data["history"])
                return {"status": "success", "path": file_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "canceled"}

    def _add_history(self, name, status, duration="--", message=""):
        import datetime
        import uuid
        data = self._load_data()
        entry = {
            "id": f"#AF-{uuid.uuid4().hex[:5].upper()}",
            "name": name,
            "status": status,
            "duration": duration,
            "time": datetime.datetime.now().strftime("%I:%M %p"),
            "message": message
        }
        data["history"].insert(0, entry)
        data["history"] = data["history"][:100] # Increased to 100
        
        # Update stats
        data["stats"]["total_tasks"] += 1
        if status == "Completed":
            if "Excel" in name:
                data["stats"]["total_conversions"] += 1
            
            # Real time saved calculation
            try:
                # Parse duration (e.g., "14.2s")
                seconds = float(duration.replace("s", ""))
                if "total_seconds" not in data["stats"]:
                    data["stats"]["total_seconds"] = 0.0
                data["stats"]["total_seconds"] += seconds
                
                total_s = data["stats"]["total_seconds"]
                if total_s < 60:
                    data["stats"]["time_saved"] = f"{total_s:.1f}s"
                elif total_s < 3600:
                    data["stats"]["time_saved"] = f"{int(total_s // 60)}m {int(total_s % 60)}s"
                else:
                    data["stats"]["time_saved"] = f"{int(total_s // 3600)}h {int((total_s % 3600) // 60)}m"
            except:
                pass
        
        # Calculate success rate
        successes = len([h for h in data["history"] if h["status"] == "Completed"])
        total = len(data["history"])
        data["stats"]["success_rate"] = f"{(successes / total * 100):.0f}%" if total > 0 else "100%"
        
        self._save_data(data)



    def select_excel_file(self):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        root.destroy()
        
        if file_path:
            self._current_excel_path = file_path
            filename = os.path.basename(file_path)
            return {"status": "success", "path": file_path, "filename": filename}
        return {"status": "canceled"}

    def select_file(self, file_types=None):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        
        types = file_types if file_types else [("Text Files", "*.txt"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=types)
        root.destroy()
        
        if file_path:
            filename = os.path.basename(file_path)
            return {
                "status": "success", 
                "path": file_path, 
                "filename": filename,
                "urlCount": self._count_valid_urls(file_path)
            }
        return {"status": "canceled"}

    def select_directory(self):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        dir_path = filedialog.askdirectory()
        root.destroy()
        
        if dir_path:
            dirname = os.path.basename(dir_path) if os.path.basename(dir_path) else dir_path
            return {"status": "success", "path": dir_path, "dirname": dirname}
        return {"status": "canceled"}

    def get_task_status(self):
        return self._task_status


    def run_excel_convert(self):
        try:
            if not self._current_excel_path:
                res = self.select_excel_file()
                if res["status"] == "canceled":
                    return {"status": "canceled", "message": "請先選擇檔案"}
            
            import convert_excel
            import glob
            import time
            
            start_time = time.time()
            # The script now raises ValueError for issues and returns the output_dir on success
            output_dir_path = convert_excel.main(self._current_excel_path)
            duration = f"{time.time() - start_time:.1f}s"
            
            if output_dir_path and os.path.exists(output_dir_path):
                files = glob.glob(os.path.join(output_dir_path, "*.txt"))
                if files:
                    output_files = []
                    for f in files:
                        output_files.append({
                            "name": os.path.basename(f),
                            "path": f,
                            "urlCount": self._count_valid_urls(f)
                        })
                    
                    # Sort by name for consistency
                    output_files.sort(key=lambda x: x["name"])
                    
                    self._latest_output_folder = output_dir_path
                    self._add_history(f"Excel 轉換 ({os.path.basename(self._current_excel_path)})", "Completed", duration)
                    return {
                        "status": "success", 
                        "message": "Excel 轉換完成！",
                        "output_files": output_files,
                        "output_folder": output_dir_path
                    }

            self._add_history(f"Excel 轉換 ({os.path.basename(self._current_excel_path)})", "Completed", duration)
            return {"status": "success", "message": "Excel 轉換完成！", "output_files": []}
        except ValueError as e:
            # Catch specific conversion errors
            self._add_history("Excel 轉換任務", "Error")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self._add_history("Excel 轉換任務", "Error")
            return {"status": "error", "message": f"未預期的轉換失敗: {str(e)}"}

    def open_file(self, path):
        if os.path.exists(path):
            os.startfile(path)
            return True
        return False

    def open_folder(self, path):
        if os.path.exists(path):
            os.startfile(path)
            return True
        return False

    def open_logs_folder(self):
        log_dir = BASE_DIR / "logs"
        if not log_dir.exists():
            log_dir.mkdir()
        os.startfile(log_dir)
        return True

    def get_default_output_dir(self, urls_file_path):
        """Calculates what the default output dir would be for a given txt file."""
        if not urls_file_path:
            return ""
        try:
            from 截圖腳本.utils_system import default_output_dir_from_urls
            # Need to handle the path properly since utils_system might expect a string or Path
            folder_name = default_output_dir_from_urls(urls_file_path)
            # Default is usually relative to the script or a specific base
            # In our setup, main.py calculates it relative to its own location if not careful
            # But here we want the absolute path for display
            base_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.abspath(os.path.join(base_dir, "截圖腳本", folder_name))
        except Exception:
            return ""

    def _count_valid_urls(self, file_path):
        """Counts non-empty lines that don't start with #."""
        count = 0
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if s and not s.startswith("#"):
                            count += 1
        except Exception:
            pass
        return count

    def select_multiple_files(self):
        """Allows selection of multiple .txt files."""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(
            title="選擇網址清單 (可多選)",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        root.destroy()
        
        if file_paths:
            # Return list of objects with urlCount
            return {
                "status": "success", 
                "files": [
                    {
                        "path": p, 
                        "name": os.path.basename(p), 
                        "urlCount": self._count_valid_urls(p)
                    } for p in file_paths
                ]
            }
        return {"status": "canceled"}

    def select_input_folder(self):
        """Allows selection of a folder containing .txt files."""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="選擇包含 TXT 的資料夾")
        root.destroy()
        
        if folder_path:
            return {
                "status": "success",
                "path": folder_path,
                "name": os.path.basename(folder_path)
            }
        return {"status": "canceled"}

    def save_settings(self, settings):
        data = self._load_data()
        data["settings"] = settings
        self._save_data(data)
        return {"status": "success"}

    def clear_done_log(self, input_file_path):
        """
        Clears the specific done log associated with the input file.
        Convention: done log is usually 'done.json' or can be derived.
        However, the main script largely uses a global DONE_LOG or specific one.
        If we want to clear the record for a specific input file, we might need to know which done log it uses.
        By default main.py uses 'done.json' (global).
        If we want to support per-task done logs, main.py logic needs check.
        But usually users want to clear the GLOBAL done log or remove entries for that file?
        Actually the user request says: "跳過已完成需要搭配'刪除已完成紀錄' 避免無法重跑".
        If they want to re-run a specific file, we should probably remove entries related to that file from done.json?
        Or simply delete 'done.json'?
        Let's implement a 'reset_all_records' for now, or if possible, filter.
        Since done.json is a set of URLs, if we want to "reset" for a specific file, we'd need to know which URLs are in that file.
        Let's read the input file, get URLs, and remove them from done.json.
        """
        try:
            if not input_file_path or not os.path.exists(input_file_path):
                return {"status": "error", "message": "找不到輸入檔案"}
            
            # 1. Read input file to get URLs
            target_urls = set()
            with open(input_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u and not u.startswith("#"):
                         target_urls.add(u)
            
            # 2. Load done.json
            data = self._load_data() # This loads app_data.json, NOT done.json from main.py
            # We need to access the done.json used by main.py
            # Default is defined in config.py or passed via args.
            # We assume standard location: BASE_DIR / "截圖腳本" / "done.json"
            done_log_path = BASE_DIR / "截圖腳本" / "done.json"
            
            if not done_log_path.exists():
                 return {"status": "success", "message": "無已完成紀錄"}

            import json
            with open(done_log_path, "r", encoding="utf-8") as f:
                done_data = json.load(f)
            
            # done_data structure: { "done": [url1, ...], "outputs": {...}, "classes": {...} }
            
            original_count = len(done_data.get("done", []))
            
            # Filter
            done_data["done"] = [u for u in done_data.get("done", []) if u not in target_urls]
            
            # Also clean outputs/classes if needed (optional but good)
            if "outputs" in done_data:
                for u in target_urls:
                    done_data["outputs"].pop(u, None)
            if "classes" in done_data:
                for u in target_urls:
                     done_data["classes"].pop(u, None)
            
            new_count = len(done_data["done"])
            removed = original_count - new_count
            
            with open(done_log_path, "w", encoding="utf-8") as f:
                json.dump(done_data, f, indent=4, ensure_ascii=False)
                
            return {"status": "success", "message": f"已清除 {removed} 筆相關紀錄"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_app_state(self):
        data = self._load_data()
        return {
            "stats": data.get("stats", {}),
            "history": data.get("history", []),
            "settings": data.get("settings", {}), # Return saved settings
            "latest_excel_folder": self._latest_output_folder,
            "latest_screenshot_folder": self._latest_screenshot_folder,
            "latest_screenshot_results": self._latest_screenshot_results
        }

    # ... (select_media code if needed) ...

    def start_screenshot(self, config=None):
        try:
            self._screenshot_stop_signal = False
            
            # Input Files Processing
            raw_inputs = []
            if config:
                if "inputFiles" in config and isinstance(config["inputFiles"], list):
                     raw_inputs = config["inputFiles"]
                elif "inputFile" in config and config["inputFile"]:
                     raw_inputs = [config["inputFile"]]
            
            input_files = []
            for item in raw_inputs:
                path = item["path"] if isinstance(item, dict) else item
                abs_path = os.path.abspath(path) # Ensure absolute path
                if os.path.isdir(abs_path):
                    from pathlib import Path
                    # Keep absolute paths during expansion
                    found_paths = sorted([str(p.absolute()) for p in Path(abs_path).glob("*.txt")])
                    for fp in found_paths:
                        input_files.append({
                            "path": fp,
                            "name": os.path.basename(fp),
                            "urlCount": self._count_valid_urls(fp)
                        })
                else:
                    input_files.append({
                        "path": abs_path,
                        "name": os.path.basename(abs_path),
                        "urlCount": item.get("urlCount", self._count_valid_urls(abs_path)) if isinstance(item, dict) else self._count_valid_urls(abs_path)
                    })

            if not input_files:
                return {"status": "error", "message": "未找到有效的輸入檔案 (.txt)"}

            self._task_status = {
                "processed": 0, 
                "total": 0, 
                "status": "running",
                "current_file": 1,
                "total_files": len(input_files),
                "errors": [] # List of {file, msg} for notification
            }
            
            # Map config params to snake_case for backend
            # Note: main.py run_from_api expects these overrides
            api_config = {}
            if config:
                api_config.update(config)
                # Ensure snake_case mappings
                if "outputDir" in config: api_config["output_dir"] = config["outputDir"]
                if "skipDone" in config: api_config["skip_done"] = config["skipDone"]
                if "textCheckEnabled" in config: api_config["text_check_enabled"] = config["textCheckEnabled"]
                if "scrollCapture" in config: api_config["scroll_capture"] = config["scrollCapture"]
                if "scrollTimes" in config: api_config["scroll_pagedown_times"] = config["scrollTimes"]
                
                # Crop Toggle Logic
                if config.get("cropEnabled", True):
                    if "cropTop" in config: api_config["crop_top_px"] = config["cropTop"]
                    if "cropBottom" in config: api_config["crop_bottom_px"] = config["cropBottom"]
                else:
                    api_config["crop_top_px"] = 0
                    api_config["crop_bottom_px"] = 0
                
                # Batch Rest Toggle Logic
                if config.get("batchRestEnabled", True):
                    if "batchSize" in config: api_config["batch_size"] = config["batchSize"]
                    if "batchRestRange" in config:
                        br = config["batchRestRange"]
                        api_config["batch_rest_range"] = (br.get("min", 20), br.get("max", 30))
                else:
                    api_config["batch_size"] = 0 # 0 means disabled in main.py
                
                if "waitPerPage" in config: 
                     # Handle min/max range
                     w = config["waitPerPage"]
                     if isinstance(w, dict):
                         api_config["page_wait_range"] = (w.get("min", 5), w.get("max", 10))
                     else:
                         api_config["page_wait_range"] = (int(w), int(w))
            
            def progress_callback(processed, total):
                self._task_status["processed"] = processed
                self._task_status["total"] = total
            
            # Clear previous results before starting a new batch
            self._latest_screenshot_results = []
            
            def task():
                import time
                import os
                import main as screenshot_main
                
                total_files = len(input_files)
                # Store original CWD
                original_cwd = os.getcwd()
                script_dir = os.path.join(BASE_DIR, "截圖腳本")
                
                try:
                    # Switch to script dir so main.py finds its relative files
                    os.chdir(script_dir)
                    
                    for idx, file_info in enumerate(input_files):
                        if self._screenshot_stop_signal:
                            break
                        
                        file_path = file_info["path"]
                        # Ensure absolute path before we chdir
                        abs_file_path = os.path.abspath(file_path)
                        
                        self._task_status["current_file"] = idx + 1
                        start_time = time.time()
                        filename = os.path.basename(abs_file_path)
                        
                        try:
                            # Update api_config for this specific file
                            current_config = api_config.copy()
                            current_config["urls_file"] = abs_file_path # main.py uses this to load URLs
                            
                            out_dir = screenshot_main.run_from_api(
                                lambda: self._screenshot_stop_signal, 
                                config_overrides=current_config,
                                progress_callback=progress_callback
                            )
                            
                            if out_dir and os.path.exists(out_dir):
                                self._latest_screenshot_folder = out_dir
                                # Scan for Word files and the folder itself
                                import glob
                                word_files = glob.glob(os.path.join(out_dir, "*.docx"))
                                results = []
                                for wf in word_files:
                                    results.append({"name": os.path.basename(wf), "path": wf, "type": "file"})
                                # Add the folder itself as a result too?
                                # Results will be displayed in UI
                                self._latest_screenshot_results.extend(results)

                            # Record history
                            duration = f"{time.time() - start_time:.1f}s"
                            self._add_history(f"任務 ({idx+1}/{total_files}): {filename}", "Completed", duration)
                            
                        except Exception as e:
                            err_msg = str(e)
                            print(f"Error processing {filename}: {err_msg}")
                            self._add_history(f"任務失敗: {filename}", "Error", message=err_msg)
                            self._task_status["errors"].append({"file": filename, "msg": err_msg})
                finally:
                    # Always restore CWD
                    os.chdir(original_cwd)
                    self._task_status["status"] = "idle"
                    self._task_status["processed"] = 0
                    self._task_status["total"] = 0
                    
                    # After all tasks finish, restore window to front
                    try:
                        import webview
                        # In pywebview, self._window should be available if passed to Bridge
                        if hasattr(self, '_window') and self._window:
                            self._window.restore()
                            self._window.show() # Ensure it's visible
                    except:
                        pass

            
            threading.Thread(target=task, daemon=True).start()
            return {"status": "success", "message": f"已排定 {len(input_files)} 個任務！"}
        except Exception as e:
            return {"status": "error", "message": f"啟動失敗: {str(e)}"}

    def stop_screenshot(self):
        self._screenshot_stop_signal = True
        return {"status": "stopping", "message": "正在停止..."}

# Setup Flask to serve the React 'dist' folder
server = Flask(__name__, static_folder=str(DIST_DIR))

@server.route("/")
def serve_index():
    return send_from_directory(str(DIST_DIR), "index.html")

@server.route("/<path:path>")
def serve_assets(path):
    return send_from_directory(str(DIST_DIR), path)

# Hide Flask logs for a cleaner terminal
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def run_flask():
    server.run(port=5858, debug=False, threaded=True)

if __name__ == "__main__":
    if not DIST_DIR.exists():
        print("Error: 'dist' folder not found. Please run 'npm run build' inside autoflow-control-center first.")
        sys.exit(1)

    # Start light server in background
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    print("--- Autoflow 控制中心正在啟動 ---")
    print("目前正在開啟桌面視窗，請稍候...")

    # Launch PyWebView window
    bridge = Bridge()
    window = webview.create_window(
        "Autoflow 控制中心", 
        "http://localhost:5858", 
        js_api=bridge,
        width=1200,
        height=800,
        background_color='#f6f6f8'
    )
    bridge._window = window
    
    # Force Edge Chromium for best compatibility on Windows
    try:
        webview.start(gui='edgechromium')
    except Exception:
        # Fallback to default if Edge is unavailable
        webview.start()
