# AutoFlow Control Center (v2.0.0)

這是一個全功能的自動化工作控制中心，整合了 `Excel 轉檔` 與 `網頁自動截圖` 兩大核心功能，並提供現代化的操作介面與任務管理系統。

## 🚀 最新功能 (v2.0.0)

### 1. 整合控制台
- **單一入口**：不再需要分別開啟不同的執行檔，所有功能皆整合於同一介面。
- **現代化 UI**：採用深色模式支援 (Dark Mode)、流暢的動畫與響應式佈局。

### 2. 任務排程 (Job Queue)
- **批量處理**：支援一次加入多個 Excel 檔案至待執行清單。
- **拖曳排序**：可直接拖曳調整任務執行順序。
- **橫向收合**：右側面板可水平收起，最大化工作區域。

### 3. 通知中心
- **即時回饋**：內建通知中心，即時顯示任務成功、失敗與詳細訊息。
- **歷史紀錄**：自動保存執行歷史，方便回溯追蹤。

### 4. 進階設定
- **標籤式管理**：直覺的關鍵詞標籤開關 (驗證碼、登入、查無資料等)。
- **持久化儲存**：自動記憶您的偏好設定與介面配置。

---

## 📦 下載與安裝

請前往 [Releases](https://github.com/kevin-leeeeee/auto_screenshot/releases) 下載最新版本的壓縮包。

1. 下載 `AutoFlow_Control_Center_v2.0.0.zip`。
2. 解壓縮至任意資料夾。
3. 執行資料夾內的 `AutoFlow_Control_Center.exe`。

---

## 🛠️ 開發者指南 (Building from Source)

若您希望自行修改或建置專案，請依照以下步驟：

### 環境需求
- Python 3.10+
- Node.js 18+ (用於前端建置)

### 1. 安裝依賴
```bash
# Python
pip install -r requirements.txt
# (若無 requirements.txt，主要依賴為: Flask, pywebview, openpyxl, python-docx, pyautogui, Pillow)

# Frontend
cd autoflow-control-center
npm install
```

### 2. 建置前端
```bash
cd autoflow-control-center
npm run build
```

### 3. 打包應用程式
返回根目錄並執行 PyInstaller：
```bash
cd ..
pyinstaller autoflow.spec --clean --noconfirm
```
打包完成後，執行檔將位於 `dist/AutoFlow_Control_Center/` 目錄中。

---

## 📁 專案結構

- `run_app.py`: 應用程式主入口 (Flask + PyWebView)。
- `autoflow-control-center/`: 前端 React 專案源碼。
- `excel_轉換/`: Excel 處理核心邏輯。
- `截圖腳本/`: 網頁自動化核心邏輯。
- `app_data.json`: 儲存應用程式的統計數據與設定。

---

## 🛡️ 安全性說明
本軟體完全於本機執行，不會將您的 Excel 檔案、截圖或設定上傳至任何外部伺服器。
