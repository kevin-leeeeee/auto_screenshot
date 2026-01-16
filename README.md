# AutoFlow Control Center (v3.3.1)

這是一個具備「插拔式架構」的自動化工作平台，專為追求極致維護效率而設計。

## 🏆 v3.3.1 核心特色：插拔式架構 (Pluggable Architecture)
從本版本起，主程式 (.exe) 已成為一個穩定的執行平台，所有的業務邏輯與介面皆已解耦：
- **零重載更新**: 修正 UI、Excel 腳本或截圖邏輯時，只需替換檔案，**無需重新下載整個發布包**。
- **極致輕量**: 核心邏輯更新僅需數百 KB，取代以往數百 MB 的重複下載。

---

## 📦 下載與安裝

請前往 [Releases](https://github.com/kevin-leeeeee/auto_screenshot/releases) 下載最新版本的壓縮包。

### 建議下載版本：`AutoFlow_v3.0.0_Full.zip`

1. 下載並解壓縮。
2. **目錄結構確認**: 請確保您的資料夾結構如下 (不可隨意改名):
   ```text
   AutoFlow/
   ├── AutoFlow.exe          (主程式平台)
   ├── core/                 (導引邏輯)
   ├── _internal/            (包含 ui, excel, screenshot 子目錄)
   └── version.txt           (版本號)
   ```
3. 執行 `AutoFlow.exe`。

---

## 📁 專案結構

```
AutoFlow_Control_Center/
├── run.py                          # 應用程式主入口 (PyWebView 封裝)
├── version.txt                     # 版本號管理
├── CHANGELOG.md                    # 更新日誌
├── DEVELOPER.md                    # 開發者指南 (建置與打包說明)
├── build.bat                       # 建置腳本 (PyInstaller)
├── AutoFlow.spec                   # PyInstaller 配置
├── excel/                          # 外部 Excel 處理邏輯 (插拔式)
├── screenshot/                     # 外部網頁自動化邏輯 (插拔式)
└── autoflow/                       # 前端 React 源碼
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



### 開發者發布新版本
### 開發者發布新版本
1. 更新 `version.txt` 與 `CHANGELOG.md`
2. 執行 `build.bat` 進行建置
3. 詳情請參閱 [DEVELOPER.md](DEVELOPER.md)

---

## 🛡️ 安全性說明
本軟體完全於本機執行,不會將您的資料、截圖或設定上傳至任何外部伺服器。

---

## 📝 更新日誌

詳細的更新日誌請查看 [CHANGELOG.md](CHANGELOG.md)

---

## 🙏 致謝

感謝所有使用者的回饋與建議,讓 AutoFlow Control Center 持續進步!
