# GitHub CLI 快速設定指南

## ✅ 安裝狀態
GitHub CLI 已成功安裝!

## 📋 登入步驟

### 1. 開啟新的終端機
- 按 `Ctrl + Shift + ` ` (反引號)
- 或點擊「終端機」→「新增終端機」

### 2. 執行登入命令
```powershell
gh auth login
```

### 3. 按照提示選擇
```
? What account do you want to log into?
> GitHub.com

? What is your preferred protocol for Git operations?
> HTTPS

? How would you like to authenticate GitHub CLI?
> Login with a web browser

! First copy your one-time code: XXXX-XXXX
Press Enter to open github.com in your browser...
```

### 4. 完成授權
1. 複製顯示的一次性代碼 (例如: ABCD-1234)
2. 按 Enter 鍵
3. 瀏覽器會自動開啟 GitHub 授權頁面
4. 貼上代碼並點擊「Authorize」

### 5. 驗證登入成功
```powershell
gh auth status
```

應該會看到:
```
✓ Logged in to github.com as kevin-leeeeee
✓ Git operations for github.com configured to use https protocol.
✓ Token: *******************
```

---

## 🎯 登入完成後可以做什麼

### 測試自動發布
```powershell
# 查看當前 repository 資訊
gh repo view

# 列出所有 releases
gh release list

# 測試建立 release (先不要執行,等建置完成)
# .\release_components.bat
```

---

## ⚠️ 常見問題

### Q: 執行 gh 命令時顯示「無法辨識」
**解決**: 重新啟動終端機或 VS Code

### Q: 登入時瀏覽器沒有自動開啟
**解決**: 手動開啟 https://github.com/login/device 並輸入代碼

### Q: 忘記複製一次性代碼
**解決**: 重新執行 `gh auth login`

---

## 📝 下一步

1. ✅ 完成 GitHub CLI 登入
2. ⏳ 等待建置完成 (目前正在進行中)
3. 🚀 測試自動發布功能
