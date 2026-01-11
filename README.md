# 工作自動化工具集 (Work Automation Toolbox)

這是一個整合多項工作自動化腳本的儲存庫，旨在透過 Python 腳本簡化日常重複性任務，提升工作效率。

## 🚀 下載與執行 (Download & Run)

如果您不需要修改程式碼，可以直接從 [GitHub Releases](https://github.com/kevin-leeeeee/auto_screenshot/releases) 下載編譯好的 `.exe` 執行檔：

1.  前往 **[Releases 頁面](https://github.com/kevin-leeeeee/auto_screenshot/releases)**。
2.  下載最新版本的 `screenshot_tool.exe` 或 `convert_excel.exe`。
3.  **注意**：執行時若被 Windows Defender 攔截，請點選「其他資訊」並選擇「仍要執行」。

---

## 📁 專案結構 (Project Structure)

本儲存庫包含以下獨立的工具模組：

### 1. [截圖腳本](./截圖腳本/) (Auto Screenshot Tool)
- **用途**：自動化網頁截圖、文字分析與分類、匯出 Word 報表。
- **核心技術**：Playwright, PyAutoGUI, python-docx, Tkinter (GUI)。
- **詳細說明**：詳見 [截圖腳本/README.md](./截圖腳本/README.md)。

### 2. [excel_轉換](./excel_轉換/) (Excel to TXT Converter)
- **用途**：將 Excel 案件清單轉換為格式化的文字檔，支援根據檢舉人資訊自動分類與分檔。
- **核心技術**：Pandas, Openpyxl, Tkinter (GUI), PyInstaller。
- **詳細說明**：詳見 [excel_轉換/README.md](./excel_轉換/README.md)。

---

## 🛠️ 共用開發說明

### 環境需求
- Python 3.10+
- 建議使用虛擬環境 (Virtual Environment) 以避免套件衝突。

### 快速開始
1. 複製此儲存庫：
   ```bash
   git clone https://github.com/kevin-leeeeee/auto_screenshot.git
   ```
2. 進入對應的工具目錄，依照各目錄下的 `README.md` 進行安裝與執行。

---

## 🛡️ 安全性承諾
本專案所有腳本皆為開源透明，不包含任何後端連線、數據收集或惡意代碼。所有資料處理均在您的本機電腦上執行。
