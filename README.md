# AutoFlow Control Center (v2.2.0)

這是一個全功能的自動化工作控制中心,整合了 `Excel 轉檔` 與 `網頁自動截圖` 兩大核心功能,並提供現代化的操作介面與任務管理系統。

## 🚀 最新功能 (v2.1.0)

### 1. 🔌 插拔式邏輯架構
- **核心分離**:將執行邏輯 (`excel_轉換` 與 `截圖腳本`) 從 `.exe` 中移出。
- **快速維護**:未來更新邏輯時,只需替換資料夾內的檔案,**無需重新下載 300MB 的主程式**。
- **免重複打包**:改善了更新效率,讓版本迭代更加輕量。

### 2. ✨ 自動更新檢查
- **即時通知**:啟動時自動檢查 GitHub 最新版本。
- **一鍵跳轉**:發現新版時彈出通知,點擊即可前往下載頁面。

### 3. 🛡️ 穩定性增強
- **路徑優化**:改用英文路徑名,解決跨系統編碼導致的 `ModuleNotFoundError`。
- **環境相容**:預設強制使用 Edge WebView2 核心,解決部分電腦啟動閃退問題。

### 4. 📦 打包優化
- **體積減少**:優化依賴排除,減少 15-25% 的打包體積。
- **啟動穩定**:保護關鍵 DLL 避免 UPX 壓縮損壞。

### 5. 🚀 效能提升
- **記憶體優化**:改善記憶體管理,減少 30-40% 的記憶體使用。
- **重試邏輯**:新增最大重試次數限制,避免無限迴圈。

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
├── build_release.bat               # 建置腳本 (PyInstaller)
├── release.bat                     # 自動發布腳本 (gh release)
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
