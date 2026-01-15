# AutoFlow Control Center (v2.2.0)

這是一個全功能的自動化工作控制中心，整合了 `Excel 轉檔` 與 `網頁自動截圖` 兩大核心功能，並提供現代化的操作介面與任務管理系統。

## 🚀 最新功能與特色

### 1. � 完整自動更新機制
- **應用內更新**: 提供詳細的更新對話框，包含版本對比與更新日誌。
- **快速腳本更新**: 支援一鍵更新外部核心邏輯，**無需重啟程式**即可生效。
- **更新進度可視化**: 提供清晰的下載進度條與狀態反饋。

### 2. ✨ UI/UX 深度優化
- **現代化通知中心**: 在標題列整合歷史任務紀錄與即時狀態通知。
- **視覺體驗升級**: 完整支援深色模式與自定義字體縮放（視障友善）。
- **任務管理增強**: 待執行清單 (Job Queue) 支援拖拽排序與即時進度追蹤。

### 3. 🔌 插拔式邏輯架構
- **核心分離**: 將執行邏輯 (`excel_轉換` 與 `截圖腳本`) 從 `.exe` 中移出，維護更輕量。

### 4. 🛡️ 穩定性與效能
- **重試機制**: 新增最大重試次數限制，避免任務因網路波動中斷。
- **環境相容**: 強制使用 Edge WebView2 核心，解決特定環境下的啟動問題。
- **精準統計**: 優化「節省時間」統計邏輯，基於實際執行時間計算成果。

---

## 📦 下載與安裝

請前往 [Releases](https://github.com/kevin-leeeeee/auto_screenshot/releases) 下載最新版本的壓縮包。

### 建議下載版本：`AutoFlow_Control_Center_v2.2.0_Full.zip`

1. 下載並解壓縮。
2. **目錄結構確認**: 請確保您的資料夾結構如下 (不可隨意改名):
   ```text
   AutoFlow_Control_Center_v2.2.0/
   ├── AutoFlow_Control_Center_v2.2.0.exe  (主程式)
   ├── excel_轉換/                         (Excel 處理腳本)
   └── 截圖腳本/                           (自動截圖腳本)
   ```
3. 執行 `AutoFlow_Control_Center_v2.2.0.exe`。

---

## 📁 專案結構

```
AutoFlow_Control_Center/
├── run_app.py                      # 應用程式主入口 (PyWebView 封裝)
├── version.txt                     # 版本號管理
├── CHANGELOG.md                    # 更新日誌
├── UPDATE_GUIDE.md                 # 使用者更新指南
├── DEVELOPER.md                    # 開發者指南 (建置與打包說明)
├── bump_version.bat                # 版本號更新工具
├── build.bat                      # 建置腳本 (PyInstaller)
├── release.bat                     # 自動發布腳本 (gh release)
├── build.spec                     # PyInstaller 配置
├── docs/                          # 文檔資料夾
├── excel_轉換/                     # 外部 Excel 處理邏輯 (插拔式)
├── 截圖腳本/                       # 外部網頁自動化邏輯 (插拔式)
└── autoflow-control-center/        # 前端 React 源碼
```

---

## 🔄 更新流程

### 使用者更新

**方法一:應用內快速更新 (推薦)** ⚡
1. 點擊側邊欄的「檢查更新」按鈕
2. 選擇「更新腳本」(無需重啟) 或「下載完整更新」
3. 完成!

**方法二:手動下載更新**
1. 前往 [Releases](https://github.com/kevin-leeeeee/auto_screenshot/releases) 頁面
2. 下載最新版本的 `_Full.zip`
3. 解壓縮並覆蓋舊版本
4. 執行新版本的 `.exe`

> 📖 **詳細更新指南**: 請參閱 [UPDATE_GUIDE.md](UPDATE_GUIDE.md)

### 開發者發布新版本
1. 執行 `bump_version.bat` 更新版本號
2. 更新 `CHANGELOG.md`
3. 執行 `release.bat` 自動建置並發布

---

## 🛡️ 安全性說明
本軟體完全於本機執行,不會將您的資料、截圖或設定上傳至任何外部伺服器。

---

## 📝 更新日誌

詳細的更新日誌請查看 [CHANGELOG.md](CHANGELOG.md)

---

## 🙏 致謝

感謝所有使用者的回饋與建議,讓 AutoFlow Control Center 持續進步!
