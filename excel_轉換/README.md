# Excel 轉文字檔分類工具 (Excel to TXT Converter)

這是一個專門用於整理 Excel 案件資料的工具。它能讀取 Excel 中的公文文號、檢舉人資訊及網址，並根據檢舉人身份自動將資料分群、去重，最後輸出格式化的文字檔。

## 🌟 核心功能

- **自動分群**：根據「檢舉人」或「檢舉人信箱」自動判斷，將同一位檢舉人的多筆案件歸類在同一個文字檔中。
- **格式化輸出**：
  - 公文文號前自動加上 `#` 字串（例如：`#1130000123`）。
  - 文號與網址成對排列，中間以空行分隔。
- **自動命名**：生成的文字檔會以該群組的第一筆公文文號命名，方便與後續截圖流程對接。
- **GUI 介面**：提供檔案選取視窗，無需手動修改路徑，直接選取 Excel 檔案即可執行。
- **時間戳記分類**：輸出的檔案會依執行時間存放在 `output/YYYYMMDD_HHMMSS/` 資料夾中。

## 🚀 快速開始

### 方式一：直接執行 Python 腳本
1. 確保已安裝 Python 3.10+
2. 安裝必要套件：
   ```bash
   pip install pandas openpyxl
   ```
3. 執行程式：
   ```bash
   python convert_excel.py
   ```

### 方式二：使用編譯好的執行檔 (.exe)
1. 進入 `dist/` 資料夾（若已打包）。
2. 直接執行 `convert_excel.exe`。

## 📦 打包成 .exe 說明

本專案使用 PyInstaller 進行打包，以確保在沒有 Python 環境的電腦上也能執行：

1. 安裝 PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 執行打包指令：
   ```bash
   pyinstaller --noconsole --onefile convert_excel.py
   ```
   *(註：`--noconsole` 可隱藏背景黑框，`--onefile` 會將所有依賴打包成單一檔案)*

## 📂 資料夾說明
- `convert_excel.py`: 核心程式碼。
- `output/`: 轉換後的文字檔儲存位置（預設會被 Git 忽略）。
- `dist/`: 打包後的執行檔產出位置。
