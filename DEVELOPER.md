# AutoFlow Control Center 開發者指南

本文件提供給維護者或開發者，說明如何建置、打包與發布 AutoFlow Control Center。

---

## 🛠️ 開發工具與環境

### 環境需求
- Python 3.12+ (建議使用 Conda 或 venv 管理環境)
- Node.js 18+ (用於前端 React 建置)
- GitHub CLI (用於自動化發布發布至 Releases)

### 推薦開發流程
1. **前端**: 進入 `autoflow` 目錄，執行 `npm run dev` 啟動開發伺服器。
2. **後端**: 執行 `python run.py` 啟動主程式（預設會連結至本地開發伺服器或編譯後的 dist）。

---

## 📦 打包與發布

### 快捷指令

#### 發布流程
1. 更新版本號: 修改 `version.txt`
2. 更新日誌: 修改 `CHANGELOG.md`
3. 提交 Git 變更
```powershell
git add .
git commit -m "Bump version to vX.X.X"
```
4. 建置並發布
執行 `build.bat` 生成執行檔後，手動上傳至 GitHub Releases。

---

## 📁 專案關鍵檔案說明

- `run.py`: 核心入口，負責 PyWebView 與 Python API 橋接。
- `AutoFlow.spec`: PyInstaller 打包設定檔。
- `excel/` & `screenshot/`: 插拔式邏輯目錄，會被複製到 Release 同級目錄下。
- `autoflow/`: React 前端源碼目錄。

---

## 🛡️ 安全性與開發規範

- 邏輯檔案請保持在外部資料夾中，以便快速熱更新。
- 所有的路徑處理請務必考量 Windows 環境下的編碼問題（盡量使用 `Path` 物件）。
- 更新 UI 前端後，需確保執行 `npm run build` 生成的靜態檔案已被正確包含。
