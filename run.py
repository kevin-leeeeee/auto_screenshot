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
    launch()
