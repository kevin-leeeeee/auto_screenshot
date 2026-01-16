import sys
import os
from pathlib import Path

# Ensure we can find the core module
# If running as script, curr dir is root.
# If frozen, sys.executable dir is root.
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent.absolute()
else:
    BASE_DIR = Path(__file__).parent.absolute()

sys.path.append(str(BASE_DIR))

# Dummy imports to force PyInstaller to bundle them
if False:
    import webview
    import flask
    import requests
    import PIL
    import pyautogui
    import openpyxl
    import docx
    import shutil
    import zipfile
    import importlib
    import logging
    import datetime
    import ctypes

# Launcher Logic
def launch():
    # VERY IMPORTANT for Windows Frozen Apps
    import multiprocessing
    multiprocessing.freeze_support()
    
    print(f"🚀 Starting AutoFlow Launcher from {BASE_DIR}")
    try:
        from core.main import main
        main()
    except ImportError as e:
        print(f"[ERROR] Failed to load core module: {e}")
        # Simplistic error handling for now (console)
        # In a GUI app, we might want a raw tkinter msgbox here if webview fails
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("啟動失敗 (Launch Error)", f"無法載入核心模組 (Core Module Missing):\n{e}\n\n請嘗試重新安裝或聯絡管理員。")
            root.destroy()
        except:
            pass
        input("Press Enter to exit...")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AutoFlow Control Center")
    parser.add_argument("--update", action="store_true", help="僅更新腳本與核心邏輯 (僅限開發者或命令行使用)")
    args, _ = parser.parse_known_args()

    if args.update:
        from core.main import setup_paths, Bridge
        setup_paths()
        # Bridge logic usually needs a window, but update_scripts is safe without it
        bridge = Bridge(None)
        print("🔄 正在從 GitHub 檢查並執行更新...")
        result = bridge.update_scripts()
        
        # Display details
        if "details" in result:
            for line in result["details"]:
                print(line)
        
        print(f"\n✨ 更新狀態: {result['status']}")
        print(f"📝 訊息: {result['message']}")
        if result.get("new_version"):
            print(f"📌 目前版本已更新為: {result['new_version']}")
    else:
        launch()
