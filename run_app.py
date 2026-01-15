import webview
import threading
import sys
import os
import json
from pathlib import Path
from flask import Flask, send_from_directory
import requests
import time
import PIL.Image
import PIL.ImageGrab
import PIL.ImageChops
import PIL.ImageStat
import pyautogui

# Version Information
CURRENT_VERSION = "v2.3.0"
REPO_NAME = "kevin-leeeeee/auto_screenshot"

# Backend script paths with validation
if getattr(sys, 'frozen', False):
    # If running as executable, BASE_DIR is where the .exe is located
    BASE_DIR = Path(sys.executable).parent.absolute()
    # Support external UI (Pluggable Architecture)
    if (BASE_DIR / "ui").exists():
        DIST_DIR = BASE_DIR / "ui"
    else:
        # Path to internal dist files (PyInstaller magic)
        RESOURCE_DIR = Path(sys._MEIPASS)
        DIST_DIR = RESOURCE_DIR / "autoflow" / "dist"
else:
    # If running from source
    BASE_DIR = Path(__file__).parent.absolute()
    if (BASE_DIR / "ui").exists():
        DIST_DIR = BASE_DIR / "ui"
    else:
        DIST_DIR = BASE_DIR / "autoflow" / "dist"

EXCEL_DIR = BASE_DIR / "excel_轉換"
# Prioritize 'screenshot_script' for source mode, '截圖腳本' for frozen mode
if (BASE_DIR / "screenshot_script").exists():
    SCREENSHOT_DIR = BASE_DIR / "screenshot_script"
else:
    SCREENSHOT_DIR = BASE_DIR / "截圖腳本"

# Validate external script directories
def validate_external_scripts():
    """驗證外部腳本目錄是否存在且包含必要檔案"""
    errors = []
    
    if not EXCEL_DIR.exists():
        errors.append(f"找不到 Excel 轉換腳本目錄: {EXCEL_DIR}")
    elif not (EXCEL_DIR / "convert_excel.py").exists():
        errors.append(f"找不到 convert_excel.py 於: {EXCEL_DIR}")
    
    if not SCREENSHOT_DIR.exists():
        errors.append(f"找不到截圖腳本目錄: {SCREENSHOT_DIR}")
    elif not (SCREENSHOT_DIR / "main.py").exists():
        errors.append(f"找不到 main.py 於: {SCREENSHOT_DIR}")
    
    if errors:
        error_msg = "\n".join([
            "❌ 外部腳本載入失敗:",
            "",
            *[f"  • {err}" for err in errors],
            "",
            "💡 解決方案:",
            "  1. 確認程式目錄結構完整",
            "  2. 重新解壓縮完整的發布包",
            f"  3. 確認以下目錄存在:",
            f"     - {EXCEL_DIR}",
            f"     - {SCREENSHOT_DIR}",
        ])
        print(error_msg, file=sys.stderr)
        return False, error_msg
    
    return True, None

# Validate before adding to sys.path
validation_ok, validation_error = validate_external_scripts()

# Ensure sys.path includes the directories for external scripts
for p in [str(EXCEL_DIR), str(SCREENSHOT_DIR)]:
    if p not in sys.path:
        sys.path.append(p)

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
        self._update_check_cache: dict = {}  # Cache for update checks
        self._init_data()

    def check_update(self):
        """Check for updates from GitHub Releases API with caching"""
        # import requests <- already at top
        # import time     <- already at top
        
        # Check cache (valid for 1 hour)
        cache_key = "last_update_check"
        cache_ttl = 3600  # 1 hour in seconds
        
        if cache_key in self._update_check_cache:
            cached_time, cached_result = self._update_check_cache[cache_key]
            if time.time() - cached_time < cache_ttl:
                return cached_result
        
        try:
            repo = REPO_NAME.strip()
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "")
                
                # Extract changelog from release body
                changelog = data.get("body", "")
                
                # Get download URL for Full.zip
                download_url = ""
                assets = data.get("assets", [])
                for asset in assets:
                    if "_Full.zip" in asset.get("name", ""):
                        download_url = asset.get("browser_download_url", "")
                        break
                
                result = {
                    "has_update": latest_version and latest_version != CURRENT_VERSION,
                    "latest_version": latest_version,
                    "current_version": CURRENT_VERSION,
                    "release_url": data.get("html_url", ""),
                    "download_url": download_url,
                    "changelog": changelog,
                    "published_at": data.get("published_at", ""),
                    "release_name": data.get("name", latest_version)
                }
            
                # Cache the result
                self._update_check_cache[cache_key] = (time.time(), result)
                return result
            
            elif response.status_code == 404:
                result = {
                    "has_update": False, 
                    "current_version": CURRENT_VERSION,
                    "error": "找不到發布資訊"
                }
            else:
                result = {
                    "has_update": False,
                    "current_version": CURRENT_VERSION,
                    "error": f"GitHub API 回應錯誤 (HTTP {response.status_code})"
                }
            
            # Cache the result
            self._update_check_cache[cache_key] = (time.time(), result)
            return result
            
        except requests.exceptions.Timeout:
            return {
                "has_update": False,
                "error": "連線逾時,請檢查網路連線",
                "current_version": CURRENT_VERSION
            }
        except requests.exceptions.ConnectionError:
            return {
                "has_update": False,
                "error": "無法連線到 GitHub,請檢查網路連線",
                "current_version": CURRENT_VERSION
            }
        except Exception as e:
            print(f"Update check failed: {e}")
            return {
                "has_update": False,
                "error": f"檢查更新時發生錯誤: {str(e)}",
                "current_version": CURRENT_VERSION
            }

    def clear_latest_results(self):
        """清除目前的執行結果紀錄"""
        self._latest_screenshot_results = []
        self._latest_screenshot_folder = None
        self._latest_output_folder = None
        self._task_status = {
            "processed": 0, 
            "total": 0, 
            "status": "idle"
        }
        return {"status": "success"}

    def select_multiple_folders(self):
        """改為單次選取資料夾，符合使用者『有需要再按』的要求"""
        import tkinter as tk
        from tkinter import filedialog
        import os
        
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder_path = filedialog.askdirectory(title="選擇網址資料夾")
        root.destroy()
        
        if folder_path:
            folder_item = {
                "path": folder_path,
                "name": os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path,
                "isDir": True
            }
            return {"status": "success", "folders": [folder_item]}
        return {"status": "canceled"}

    def check_component_updates(self):
        """檢查各元件是否有更新 (分離式更新)"""
        import requests
        
        try:
            # 下載最新的 manifest.json
            url = f"https://github.com/{REPO_NAME}/releases/latest/download/manifest.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return {"has_update": False, "error": "無法取得更新資訊"}
            
            manifest = response.json()
            
            # 讀取本地版本資訊
            local_manifest = self._load_local_manifest()
            
            updates_needed = []
            total_size = 0
            
            # 檢查核心程式
            if "core" in manifest.get("components", {}):
                core_info = manifest["components"]["core"]
                local_core_version = local_manifest.get("core_version", "unknown")
                
                if core_info["version"] != local_core_version:
                    updates_needed.append({
                        "component": "core",
                        "name": "核心程式",
                        "current": local_core_version,
                        "latest": core_info["version"],
                        "size": core_info["size"],
                        "download_url": core_info["download_url"],
                        "sha256": core_info["sha256"]
                    })
                    total_size += core_info["size"]
            
            # 檢查外部腳本
            if "scripts" in manifest.get("components", {}):
                scripts_info = manifest["components"]["scripts"]
                local_scripts_version = local_manifest.get("scripts_version", "unknown")
                
                if scripts_info["version"] != local_scripts_version:
                    updates_needed.append({
                        "component": "scripts",
                        "name": "外部腳本",
                        "current": local_scripts_version,
                        "latest": scripts_info["version"],
                        "size": scripts_info["size"],
                        "download_url": scripts_info["download_url"],
                        "sha256": scripts_info["sha256"]
                    })
                    total_size += scripts_info["size"]
            
            return {
                "has_update": len(updates_needed) > 0,
                "updates": updates_needed,
                "total_size": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "changelog": manifest.get("changelog", ""),
                "version": manifest.get("version", "unknown")
            }
        
        except Exception as e:
            print(f"Component update check failed: {e}")
            return {"has_update": False, "error": str(e)}
    
    def _load_local_manifest(self):
        """載入本地版本資訊"""
        manifest_file = BASE_DIR / "local_manifest.json"
        
        if manifest_file.exists():
            try:
                import json
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # 如果沒有本地 manifest,從版本檔案讀取
        core_version_file = BASE_DIR / "core_version.txt"
        scripts_version_file = BASE_DIR / "scripts_version.txt"
        
        return {
            "core_version": core_version_file.read_text().strip() if core_version_file.exists() else "unknown",
            "scripts_version": scripts_version_file.read_text().strip() if scripts_version_file.exists() else "unknown"
        }
    
    def _save_local_manifest(self, manifest_data):
        """儲存本地版本資訊"""
        manifest_file = BASE_DIR / "local_manifest.json"
        import json
        
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    def update_scripts(self):
        """Download latest script files and UI from GitHub"""
        import requests
        import importlib
        import shutil
        import hashlib
        import zipfile
        import io
        
        # 1. Python Scripts to update
        files_to_update = [
            {
                "url": f"https://raw.githubusercontent.com/{REPO_NAME}/main/excel_轉換/convert_excel.py",
                "local_path": EXCEL_DIR / "convert_excel.py"
            },
            {
                "url": f"https://raw.githubusercontent.com/{REPO_NAME}/main/截圖腳本/main.py",
                "local_path": SCREENSHOT_DIR / "main.py"
            }
        ]
        
        results = []
        backups = []
        
        try:
            # Step A: Update Python Scripts
            for item in files_to_update:
                file_path = item["local_path"]
                file_name = file_path.name
                try:
                    resp = requests.get(item["url"], timeout=10)
                    if resp.status_code == 200:
                        if file_path.exists():
                            backup_path = file_path.with_suffix(f".py.bak.{int(time.time())}")
                            shutil.copy2(file_path, backup_path)
                            backups.append((file_path, backup_path))
                        
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(resp.content)
                        results.append(f"✅ 腳本更新成功: {file_name}")
                    else:
                        results.append(f"❌ 腳本下載失敗: {file_name}")
                except Exception as e:
                    results.append(f"❌ 腳本更新異常: {file_name} ({str(e)})")

            # Step B: Update UI (Pluggable Architecture)
            # Try to download ui.zip from the latest release
            try:
                # Get latest release tag
                api_url = f"https://api.github.com/repos/{REPO_NAME}/releases/latest"
                rel_resp = requests.get(api_url, timeout=5)
                if rel_resp.status_code == 200:
                    assets = rel_resp.json().get('assets', [])
                    ui_zip_asset = next((a for a in assets if a['name'] == 'ui.zip'), None)
                    
                    if ui_zip_asset:
                        ui_url = ui_zip_asset['browser_download_url']
                        results.append("🔍 發現介面更新包 (ui.zip)，正在下載...")
                        
                        zip_resp = requests.get(ui_url, timeout=30)
                        if zip_resp.status_code == 200:
                            # Use DIST_DIR determined at startup
                            ui_target = DIST_DIR 
                            
                            # Backup current UI
                            if ui_target.exists():
                                ui_bak = ui_target.parent / f"ui_bak_{int(time.time())}"
                                try:
                                    shutil.move(str(ui_target), str(ui_bak))
                                    backups.append((ui_target, ui_bak))
                                except:
                                    pass # Might be in use
                            
                            # Extract ZIP
                            with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as z:
                                ui_target.mkdir(parents=True, exist_ok=True)
                                z.extractall(ui_target)
                            results.append("✨ 介面 (UI) 已更新成功！(重啟後生效)")
                        else:
                            results.append("❌ 介面更新包下載失敗")
                    else:
                        results.append("ℹ️ 本次更新不含介面變動")
            except Exception as e:
                results.append(f"⚠️ 介面更新偵測失敗: {str(e)}")

            # Step C: Reload modules
            try:
                import convert_excel
                importlib.reload(convert_excel)
                results.append("🔄 核心邏輯已即時重新載入")
            except:
                pass
                
            return {
                "status": "success" if any("✅" in r or "✨" in r for r in results) else "partial",
                "details": results
            }
            
        except Exception as e:
            # Rollback on critical failure
            if backups:
                results.append(f"⚠️ 嘗試回滾...")
                for original_path, backup_path in backups:
                    try:
                        shutil.copy2(backup_path, original_path)
                        results.append(f"↩️ 已回滾: {original_path.name}")
                    except Exception as rollback_error:
                        results.append(f"❌ 回滾失敗: {original_path.name} ({rollback_error})")
            
            return {
                "status": "error",
                "message": f"更新過程發生嚴重錯誤: {str(e)}",
                "details": results
            }

    def _init_data(self):
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


    def run_excel_convert(self, start_date=None, end_date=None):
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
            output_dir_path = convert_excel.main(self._current_excel_path, start_date, end_date)
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

    def download_full_update(self, save_path=None):
        """
        下載完整更新包到指定位置
        Returns: {status, path, message, size_mb}
        """
        import requests
        
        try:
            # First check for updates to get download URL
            update_info = self.check_update()
            
            if not update_info.get("has_update"):
                return {
                    "status": "no_update",
                    "message": "目前已是最新版本"
                }
            
            download_url = update_info.get("download_url")
            if not download_url:
                return {
                    "status": "error",
                    "message": "找不到下載連結,請手動前往 GitHub Releases 下載"
                }
            
            # Determine save path
            if not save_path:
                downloads_dir = BASE_DIR / "downloads"
                downloads_dir.mkdir(exist_ok=True)
                latest_version = update_info.get("latest_version", "latest")
                save_path = downloads_dir / f"AutoFlow_Control_Center_{latest_version}_Full.zip"
            else:
                save_path = Path(save_path)
            
            # Download with progress tracking
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Could emit progress here if needed
            
            size_mb = total_size / (1024 * 1024)
            
            return {
                "status": "success",
                "path": str(save_path),
                "message": f"下載完成! 檔案已儲存至: {save_path.name}",
                "size_mb": round(size_mb, 2),
                "version": update_info.get("latest_version")
            }
            
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "下載逾時,請檢查網路連線或稍後再試"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "網路連線失敗,請檢查網路設定"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"下載失敗: {str(e)}"
            }

    def open_downloads_folder(self):
        """開啟下載資料夾"""
        downloads_dir = BASE_DIR / "downloads"
        if not downloads_dir.exists():
            downloads_dir.mkdir()
        os.startfile(downloads_dir)
        return {"status": "success", "path": str(downloads_dir)}

    def get_update_info(self):
        """
        取得完整的更新資訊,包含版本比較和可用更新
        """
        update_check = self.check_update()
        
        # Add local version details
        result = {
            **update_check,
            "current_version_full": CURRENT_VERSION,
            "base_dir": str(BASE_DIR),
            "has_scripts": EXCEL_DIR.exists() and SCREENSHOT_DIR.exists()
        }
        
        return result


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
            return os.path.abspath(os.path.join(str(SCREENSHOT_DIR), folder_name))
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
            "version": CURRENT_VERSION,
            "stats": data.get("stats", {}),
            "history": data.get("history", []),
            "settings": data.get("settings", {}), # Return saved settings
            "latest_excel_folder": self._latest_output_folder,
            "latest_screenshot_folder": self._latest_screenshot_folder,
            "latest_screenshot_results": self._latest_screenshot_results,
            "queueCollapsed": data.get("queueCollapsed", False)  # 回傳待執行清單收合狀態
        }

    def set_queue_collapsed(self, collapsed):
        """儲存待執行清單收合狀態"""
        try:
            data = self._load_data()
            data["queueCollapsed"] = collapsed
            self._save_data(data)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

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
                if "scrollStitch" in config: api_config["scroll_stitch"] = config["scrollStitch"]
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
                
                if "customCategories" in config:
                    api_config["custom_categories"] = config["customCategories"]
                
                if "categoryPause" in config:
                    api_config["category_pause"] = config["categoryPause"]
                
                if "keywords" in config:
                    api_config["keywords"] = config["keywords"]


            
            def progress_callback(processed, total):
                self._task_status["processed"] = processed
                self._task_status["total"] = total
            
            # Clear previous results before starting a new batch
            self._latest_screenshot_results = []
            
            def task():
                import time
                import os
                import traceback
                try:
                    import main as screenshot_main
                except Exception as e:
                    print(f"FAILED to import screenshot main: {e}")
                    traceback.print_exc()
                    self._task_status["status"] = "error"
                    return
                
                total_files = len(input_files)
                # Store original CWD
                original_cwd = os.getcwd()
                script_dir = str(SCREENSHOT_DIR)
                
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
                            
                            # CRITICAL: Convert to absolute path immediately after getting out_dir
                            # This ensures correct path resolution in both source and frozen (exe) modes
                            if out_dir:
                                out_dir = os.path.abspath(out_dir)
                            
                            if out_dir and os.path.exists(out_dir):
                                self._latest_screenshot_folder = out_dir
                                # Scan for Word files and the folder itself
                                import glob
                                word_files = glob.glob(os.path.join(out_dir, "*.docx"))
                                results = []
                                for wf in word_files:
                                    # Only include files created *after* we started this specific task
                                    # Use a 2-second buffer to handle slight filesystem timestamp variations
                                    if os.path.getmtime(wf) >= start_time - 2:
                                        results.append({"name": os.path.basename(wf), "path": wf, "type": "file"})
                                
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
    # Validate external scripts before starting
    if not validation_ok:
        print("\n" + "="*60)
        print(validation_error)
        print("="*60)
        print("\n按任意鍵退出...")
        try:
            import msvcrt
            msvcrt.getch()
        except:
            input()
        sys.exit(1)
    
    if not DIST_DIR.exists():
        print("Error: 'dist' folder not found. Please run 'npm run build' inside autoflow first.")
        sys.exit(1)

    # Start light server in background
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    print("--- Autoflow 控制中心正在啟動 ---")
    print("目前正在開啟桌面視窗,請稍候...")

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
    
    # Detect if running in PyInstaller bundle
    import sys
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - force edgechromium to avoid pythonnet issues
        try:
            webview.start(gui='edgechromium')
        except Exception as e:
            print(f"Edge Chromium failed: {e}")
            # Try edgehtml as fallback
            try:
                webview.start(gui='edgehtml')
            except Exception as e2:
                print(f"Edge HTML failed: {e2}")
                # Last resort: default
                webview.start()
    else:
        # Running from source - try edgechromium first
        try:
            webview.start(gui='edgechromium')
        except Exception:
            webview.start()

