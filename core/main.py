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
import importlib
import shutil
import zipfile
import io

# Global version but initialized in main()
CURRENT_VERSION = "v2.5.1"
REPO_NAME = "kevin-leeeeee/auto_screenshot"

# Paths - initialized later
BASE_DIR = None
DIST_DIR = None
EXCEL_DIR = None
SCREENSHOT_DIR = None

def setup_paths(base_path=None):
    global BASE_DIR, DIST_DIR, EXCEL_DIR, SCREENSHOT_DIR
    
    if base_path:
        BASE_DIR = Path(base_path)
    elif getattr(sys, 'frozen', False):
        # If running as executable, BASE_DIR is where the .exe is located
        BASE_DIR = Path(sys.executable).parent.absolute()
    else:
        # If running from source (as a module in core package)
        # We assume the root is the parent of 'core' directory
        BASE_DIR = Path(__file__).parent.parent.absolute()

    # Support external UI (Pluggable Architecture)
    if (BASE_DIR / "ui").exists():
        DIST_DIR = BASE_DIR / "ui"
    elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Path to internal dist files (PyInstaller magic)
        RESOURCE_DIR = Path(sys._MEIPASS)
        DIST_DIR = RESOURCE_DIR / "ui"
    else:
        # Fallback for dev mode
        DIST_DIR = BASE_DIR / "autoflow" / "dist"

    EXCEL_DIR = BASE_DIR / "excel"
    # Unified frozen logic
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
        EXCEL_DIR = bundle_dir / "excel"
        SCREENSHOT_DIR = bundle_dir / "screenshot"
    else:
        EXCEL_DIR = BASE_DIR / "excel"
        if (BASE_DIR / "screenshot").exists():
            SCREENSHOT_DIR = BASE_DIR / "screenshot"
        else:
             SCREENSHOT_DIR = BASE_DIR / "screenshot"
        
    # Validation
    validate_external_scripts()
    
    # Ensure sys.path includes the directories for external scripts
    for p in [str(EXCEL_DIR), str(SCREENSHOT_DIR)]:
        if p not in sys.path:
            sys.path.append(p)

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
            "[ERROR] 外部腳本載入失敗:",
            "",
            *[f"  - {err}" for err in errors],
            "",
            "[INFO] 解決方案:",
            "  1. 確認程式目錄結構完整",
            "  2. 重新解壓縮完整的發布包",
            f"  3. 確認以下目錄存在:",
            f"     - {EXCEL_DIR}",
            f"     - {SCREENSHOT_DIR}",
        ])
        print(error_msg, file=sys.stderr)
        return False, error_msg
    
    return True, None

# Mock System State for Bridge
class Bridge:
    def __init__(self, window):
        self._window = window
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
        import os
        
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        
        if result:
            folder_path = result[0]
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
        
        # 1. Python Scripts to update
        files_to_update = [
            {
                "url": f"https://raw.githubusercontent.com/{REPO_NAME}/main/excel_轉換/convert_excel.py",
                "local_path": EXCEL_DIR / "convert_excel.py"
            },
            {
                "url": f"https://raw.githubusercontent.com/{REPO_NAME}/main/截圖腳本/main.py",
                "local_path": SCREENSHOT_DIR / "main.py"
            },
            # Update CORE LOGIC as well (Self Update)
            {
                "url": f"https://raw.githubusercontent.com/{REPO_NAME}/main/core/main.py",
                "local_path": BASE_DIR / "core" / "main.py"
            }
        ]
        
        results = []
        backups = []
        
        try:
            # Step A: Update Python Scripts & Version File
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

            # Update version.txt specifically
            version_url = f"https://raw.githubusercontent.com/{REPO_NAME}/main/version.txt"
            version_path = BASE_DIR / "version.txt"
            try:
                v_resp = requests.get(version_url, timeout=10)
                if v_resp.status_code == 200:
                    with open(version_path, "wb") as f:
                        f.write(v_resp.content)
                    
                    # Update global CURRENT_VERSION immediately
                    global CURRENT_VERSION
                    new_v = v_resp.content.decode("utf-8").strip()
                    CURRENT_VERSION = f"v{new_v}"
                    results.append(f"✅ 版本號已更新為: {CURRENT_VERSION}")
                else:
                    results.append("❌ 版本號檔案下載失敗")
            except Exception as e:
                results.append(f"❌ 版本更新異常: {str(e)}")

            # Step B: Update UI (Pluggable Architecture)
            # Try to download ui.zip from the latest release
            try:
                # Get latest release tag
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
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
                "message": "更新完成",
                "new_version": CURRENT_VERSION,
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
        import csv
        
        data = self._load_data()
        if not data["history"]:
            return {"status": "error", "message": "沒有可導出的紀錄"}
            
        file_path = self._window.create_file_dialog(
            webview.SAVE_DIALOG, 
            file_types=("CSV Files (*.csv)", "All files (*.*)"),
            save_filename="autoflow_history.csv"
        )
        
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
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG, 
            file_types=("Excel Files (*.xlsx)", "All files (*.*)")
        )
        
        if result:
            file_path = result[0]
            self._current_excel_path = file_path
            filename = os.path.basename(file_path)
            return {"status": "success", "path": file_path, "filename": filename}
        return {"status": "canceled"}

    def select_file(self, file_types=None):
        types = file_types if file_types else ("Text Files (*.txt)", "All files (*.*)")
        result = self._window.create_file_dialog(webview.OPEN_DIALOG, file_types=types)
        
        if result:
            file_path = result[0]
            filename = os.path.basename(file_path)
            return {
                "status": "success", 
                "path": file_path, 
                "filename": filename,
                "urlCount": self._count_valid_urls(file_path)
            }
        return {"status": "canceled"}

    def select_directory(self):
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        
        if result:
            dir_path = result[0]
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
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG, 
            allow_multiple=True, 
            file_types=("Text Files (*.txt)", "All files (*.*)")
        )
        
        if result:
            file_paths = result
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
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        
        if result:
            folder_path = result[0]
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
        
    def get_app_state(self):
        """Returns app state including history and setting"""
        data = self._load_data()
        
        # Add version to the state
        version_file = BASE_DIR / "version.txt"
        version = CURRENT_VERSION
        if version_file.exists():
            version = f"v{version_file.read_text().strip()}"
            
        return {
            "history": data.get("history", []),
            "settings": data.get("settings", {}),
            "stats": data.get("stats", {}),
            "version": version
        }
    
    def get_latest_screenshot_results(self):
        """Returns latest screenshot output results (including Word documents)"""
        return {
            "results": self._latest_screenshot_results,
            "status": "success"
        }

    # Screenshot Task Integration
    def start_screenshot(self, config):
        if self._task_status["status"] == "running":
            return {"status": "error", "message": "任務執行中"}
            
        self._task_status = {"processed": 0, "total": 0, "status": "running"}
        self._screenshot_stop_signal = False
        
        # Save last used files to history if needed (optional)
        
        # Run in separate thread
        thread = threading.Thread(target=self._run_screenshot_task, args=(config,))
        thread.daemon = True
        thread.start()
        
        return {"status": "success", "message": "截圖任務已啟動"}

    def stop_screenshot(self):
        if self._task_status["status"] == "running":
            self._screenshot_stop_signal = True
            return {"status": "success", "message": "正嘗試停止任務..."}
        return {"status": "error", "message": "無執行中的任務"}
        
    def _run_screenshot_task(self, config):
        # We need to bridge the config from frontend to what 'main.py' expects
        # main.py expects args or interactive input. run_from_api was designed for this.
        import screenshot.main as capture_app
        
        input_files = []
        if config.get("inputFiles"):
             input_files = [f["path"] for f in config["inputFiles"]]
             
        api_config = {
            "input_files": input_files,
            "wait_min": config.get("waitPerPage", {}).get("min", 3),
            "wait_max": config.get("waitPerPage", {}).get("max", 10),
            "screenshot_delay": config.get("screenshotDelay", 3),
            "output_dir": config.get("outputDir"),
            
            # Crop settings
            "crop_enabled": config.get("cropEnabled", True),
            "crop_top": config.get("cropTop", 0),
            "crop_bottom": config.get("cropBottom", 0),
            "range_mode": config.get("range", "viewport"), # 'viewport' or 'full'
            
            # Keywords
            "keywords": config.get("keywords", []),
            "captcha_keywords": config.get("captchaKeywords", []),
            "not_found_keywords": config.get("notFoundKeywords", []),
            "login_keywords": config.get("loginKeywords", []),
            "bsmi_keywords": config.get("bsmiKeywords", []),
            
            # Category Config (Pause behavior)
            "category_pause": config.get("categoryPause", {}),
            
            # Batch
            "batch_rest_enabled": config.get("batchRestEnabled", True),
            "batch_size": config.get("batchSize", 8),
            "batch_rest_min": config.get("batchRestRange", {}).get("min", 20),
            "batch_rest_max": config.get("batchRestRange", {}).get("max", 30),
            
            # Others
            "auto_word_export": config.get("autoWordExport", True),
            "skip_done": config.get("skipDone", False),
            "check_text": config.get("textCheckEnabled", False),
            "scroll_capture": config.get("scrollCapture", False),
            "scroll_stitch": config.get("scrollStitch", True),
            "scroll_times": config.get("scrollTimes", 4)
        }
        
        self._task_status["total"] = len(input_files)
        
        def progress_callback(processed_count, total_count, status_msg, current_file=None, errors=None):
            self._task_status["processed"] = processed_count
            self._task_status["total"] = total_count
            self._task_status["message"] = status_msg
            self._task_status["current_file"] = current_file
            if errors:
                self._task_status["errors"] = errors
            
            # Check stop signal
            return self._screenshot_stop_signal

        try:
            start_time = time.time()
            results = capture_app.run_from_api(
                should_stop_callback=lambda: self._screenshot_stop_signal,
                config_overrides=api_config,
                progress_callback=progress_callback,
                suppress_popups=True
            )
            
            # Enhance results with open folder path
            enhanced_results = []
            # Enhance results with open folder path
            enhanced_results = []
            
            # Note: We skip adding individual image files to UI results as user requested only DOCX
            # for r in results.get("results", []):
            #     ... logic removed ...
            
            # Add Word documents to results
            for word_path in results.get("word_documents", []):
                enhanced_results.append({
                    "url": "",
                    "status": "word_document",
                    "output": word_path,
                    "path": word_path,
                    "name": os.path.basename(word_path),
                    "folder": os.path.dirname(word_path)
                })
            
            self._latest_screenshot_results = enhanced_results
            
            duration_sec = time.time() - start_time
            if duration_sec < 60:
                duration = f"{duration_sec:.1f}s"
            else:
                duration = f"{int(duration_sec // 60)}m {int(duration_sec % 60)}s"
            
            # Log to history
            msg = f"完成 {results['processed']} 個檔案"
            if results.get("errors"):
                msg += f" (失敗 {len(results['errors'])})"
            
            self._add_history("自動截圖任務", "Completed", duration, msg)
            self._task_status["status"] = "idle"
            
        except Exception as e:
            self._task_status["status"] = "error"
            self._task_status["error"] = str(e)
            self._add_history("自動截圖任務", "Error", message=str(e))
        finally:
            self._task_status["status"] = "idle"
            # Ensure window focus is restored
            try:
                # Force restore using minimize -> restore hack for Windows
                if self._window:
                    self._window.minimize() 
                    self._window.restore() 
                    # self._window.set_title(self._window.title) # Refresh trigger
                    self._window.show()
                    # A small delay might help in some cases but blocking here is bad.
                    # This is usually enough for the 'flash' effect to grab focus.
            except:
                pass

app = Flask(__name__, static_folder=str(DIST_DIR))

# Fallback for when static_folder init arg is not fully dynamic?
# Actually Flask needs the path at init. Since DIST_DIR is calculated in setup_paths,
# we need to be careful.
# SOLUTION: We will init Flask INSIDE main() after path setup.

server = None
def start_server():
    global app, server
    app = Flask(__name__, static_folder=str(DIST_DIR))

    @app.route("/")
    def index():
        return send_from_directory(str(DIST_DIR), "index.html")

    @app.route("/<path:path>")
    def assets(path):
        return send_from_directory(str(DIST_DIR), path)
    
    # Run flask in a separate thread without blocking
    # Werkzeug server is blocking, so threading is needed.
    # Production uses PyWebView's built-in HTTP server usually, 
    # but 'webview.start' with paths can also serve static files.
    # However, for API endpoints or custom logic (if any), Flask is good.
    # But here we heavily rely on Bridge.
    # We can actually skip Flask if we just want to serve a static folder.
    # Pywebview supports pointing to a local file or local server.
    # Let's keep Flask for potential future API extensions or just use it as a robust file server.
    
    app.run(port=5000)

def main():
    setup_paths()
    
    # Initialize version
    version_file = BASE_DIR / "version.txt"
    if version_file.exists():
        global CURRENT_VERSION
        CURRENT_VERSION = f"v{version_file.read_text().strip()}"
    
    # Setup Flask server to serve the React frontend
    app = Flask(__name__, static_folder=str(DIST_DIR), static_url_path='')
    
    @app.route('/')
    def index():
        return send_from_directory(str(DIST_DIR), 'index.html')
    
    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(str(DIST_DIR), path)
        
    port = 5000
    # Start Flask in a background thread
    t = threading.Thread(target=lambda: app.run(port=port, threaded=True), daemon=True)
    t.start()
    
    # Give the server a moment to start
    time.sleep(0.5)
    
    # Create Bridge and link to Window
    bridge = Bridge(None)
    window = webview.create_window(
        f"AutoFlow Control Center {CURRENT_VERSION}",
        url=f'http://127.0.0.1:{port}',
        js_api=bridge,
        width=1200,
        height=800,
        resizable=True,
        min_size=(1024, 768)
    )
    bridge._window = window
    
    # Start webview in production mode (debug=False)
    webview.start(debug=False)

if __name__ == "__main__":
    main()
