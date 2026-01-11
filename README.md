# 自動截圖與分類工具 (Auto Screenshot Tool)

[English Version Below](#english-version)

一個基於 Python 的自動化網頁截圖、文字分析與分類工具，具備圖形化介面 (GUI) 以及 Word 匯出功能。

---

## 🇹🇼 中文說明 (Chinese Version)

### 🌟 核心功能
- **自動化截圖**：支援全網頁或特定視窗截圖，可自定義滾動次數與剪裁區域。
- **人性化模擬**：具備隨機等待時間與倒數計時功能，模擬真人操作。
- **文字分類 (剪貼簿機制)**：透過全選複製方式讀取頁面文字，自動判定「Login/驗證碼」、「商品存在」或「無效連結」。
- **批次處理**：支援大量 URL 自動化執行，可設定批次休息時間以規避檢測。
- **Word / JSON 匯出**：自動將截圖與對應 URL 整理至 Word 文檔，並記錄執行狀態於 JSON 檔案。
- **狀態紀錄**：具備去重功能，自動跳過已完成的網址。

### 🚀 快速開始
1. **執行 UI 介面** (推薦)：
   ```bash
   python main.py
   ```
2. **命令列執行**：
   ```bash
   python main.py urls.txt
   ```

### 🛠️ 環境需求
- Python 3.10+
- 依賴套件：
  ```bash
  pip install pyautogui pillow python-docx pygetwindow playwright
  ```

### 📦 打包成 .exe
本專案支援使用 PyInstaller 打包成獨立執行檔：
1. 建立虛擬環境：`python -m venv .venv`
2. 安裝依賴：`.venv/Scripts/pip install -r requirements.txt` (如有)
3. 執行打包：`.venv/Scripts/pyinstaller -y screenshot_tool.spec`
4. 產出路徑：`dist/screenshot_tool/screenshot_tool.exe`

---

<a name="english-version"></a>

## 🇺🇸 English Version

An automated web screenshot, text analysis, and classification tool based on Python, featuring a GUI and Word export capabilities.

### 🌟 Key Features
- **Automated Capture**: Supports full-page or window-based screenshots with configurable scrolling and cropping.
- **Humanized Simulation**: Includes random delay times and countdown overlays to mimic real user behavior.
- **Text Classification**: Reads page text via Select-All/Copy mechanism to automatically detect captchas, valid products, or invalid links.
- **Batch Processing**: Handles multiple URLs automatically with configurable batch sizes and rest periods to avoid detection.
- **Word / JSON Export**: Compiles screenshots and URLs into Word documents and tracks completion status in JSON files.
- **Record Management**: Automatically skips previously processed URLs for efficiency.

### 🚀 Quick Start
1. **Launch GUI** (Recommended):
   ```bash
   python main.py
   ```
2. **CLI Mode**:
   ```bash
   python main.py urls.txt
   ```

### 🛠️ Dependencies
- Python 3.10+
- Required Packages:
  `pyautogui`, `pillow`, `python-docx`, `pygetwindow`, `playwright`

### 📦 Packaging
Build as a standalone executable using PyInstaller:
1. `python -m venv .venv`
2. `.venv/Scripts/pip install -r requirements.txt`
3. `.venv/Scripts/pyinstaller -y screenshot_tool.spec`
4. Result: `dist/screenshot_tool/screenshot_tool.exe`
