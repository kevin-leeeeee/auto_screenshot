
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './views/Dashboard';
import Settings from './views/Settings';
import Logs from './views/Logs';
import ConfigurationModal from './components/ConfigurationModal';
import LogModal from './components/LogModal';
import HelpModal from './components/HelpModal';
import UpdateDialog from './components/UpdateDialog';
import { ViewType, AutomationConfig, DisplaySettings, TaskStatus } from './types';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isLogOpen, setIsLogOpen] = useState(false);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [updateInfo, setUpdateInfo] = useState<any>(null);
  const [appVersion, setAppVersion] = useState('v3.1.0');
  const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
  const [isUpdatingScripts, setIsUpdatingScripts] = useState(false);

  const [config, setConfig] = useState<AutomationConfig>({
    waitPerPage: { min: 3, max: 10 },
    screenshotDelay: 3,
    cropEnabled: true,
    cropTop: 0,
    cropBottom: 0,
    range: 'viewport',
    batchRestEnabled: true,
    batchSize: 8,
    batchRestRange: { min: 20, max: 30 },
    keywords: ['登入', '拼圖與人機驗證', '查無資料', 'BSMI'],
    autoWordExport: true,
    skipDone: false,
    textCheckEnabled: false,
    scrollCapture: false,
    scrollStitch: true,
    scrollTimes: 4,
    customCategories: {},
    categoryPause: {
      '拼圖與人機驗證': true,
      '登入': true,
      '查無資料': false,
      'BSMI': false
    },
    // Defaults from config.py and playwright settings
    captchaKeywords: [
      "驗證碼", "人機驗證", "我不是機器人", "captcha", "verify", "請驗證您是人類",
      "安全驗證", "驗證資訊失敗", "拼圖", "puzzle", "robot", "automated", "rate limit",
      "verification", "滑動圖塊", "完成驗證", "安全性驗證"
    ],
    notFoundKeywords: [
      "商品不存在", "已下架", "找不到商品", "商品已刪除", "商品已下架"
    ],
    loginKeywords: [
      "登入", "登錄", "sign in", "log in", "login",
      "會員登入", "帳號", "密碼"
    ],
    bsmiKeywords: [
      "bsmi", "b s m i", "商品檢驗標識"
    ],
    inputFile: undefined,
    inputFileDisplay: undefined,
    outputDir: undefined,
    outputDirDisplay: undefined,
    inputFiles: [],
  });

  const [displaySettings, setDisplaySettings] = useState<DisplaySettings>({
    theme: 'light',
    fontSize: 2,
  });

  const [taskStatus, setTaskStatus] = useState<TaskStatus>({ processed: 0, total: 0, status: 'idle' });
  const [history, setHistory] = useState<any[]>([]); // Lifted history state
  const [toasts, setToasts] = useState<any[]>([]);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const lastErrorCount = React.useRef(0);

  // Apply display settings
  useEffect(() => {
    const root = window.document.documentElement;
    if (displaySettings.theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    /**
     * 混合字體縮放邏輯 (修正版)：
     * 1. 適度調整根字體 (baseSize) 以提供佈局容器基本的生長空間，防止重疊。
     * 2. 大幅縮放文字標籤與類別 (--text-scale) 達成視障友善需求。
     */
    const baseSizeMap: Record<number, string> = {
      1: '14px',
      2: '15px',
      3: '16px',
      4: '17px',
      5: '17.5px',
      6: '18px',
      7: '18.5px',
    };
    const scaleMap: Record<number, number> = {
      1: 0.85,
      2: 1.0,  // Standard
      3: 1.3,  // Medium
      4: 1.7,  // Large
      5: 2.2,  // XL
      6: 2.8,  // 2XL
      7: 3.5,  // MAX
    };

    const scaleFactor = scaleMap[displaySettings.fontSize] || 1.0;
    root.style.fontSize = baseSizeMap[displaySettings.fontSize] || '15px';
    root.style.setProperty('--text-scale', scaleFactor.toString());

    // 注入動態樣式
    const styleId = 'dynamic-font-scaling';
    let styleEl = document.getElementById(styleId);
    if (!styleEl) {
      styleEl = document.createElement('style');
      styleEl.id = styleId;
      document.head.appendChild(styleEl);
    }

    styleEl.innerHTML = `
      :root { --ts: var(--text-scale, 1); }
      
      /* 全面覆寫文字標籤與類別，並強化行高防止重疊 */
      h1, h2, h3, h4, h5, h6, p, span, div, button, label, input, textarea {
        line-height: 1.4 !important;
      }

      /* 修正 Tailwind 的中括號選擇器逃逸字元 */
      .text-\\[9px\\]  { font-size: calc(9px  * var(--ts)) !important; }
      .text-\\[10px\\] { font-size: calc(10px * var(--ts)) !important; }
      .text-\\[11px\\] { font-size: calc(11px * var(--ts)) !important; }
      .text-\\[12px\\] { font-size: calc(12px * var(--ts)) !important; }
      .text-\\[13px\\] { font-size: calc(13px * var(--ts)) !important; }
      .text-\\[20px\\] { font-size: calc(20px * var(--ts)) !important; }
      .text-\\[14px\\] { font-size: calc(14px * var(--ts)) !important; }
      
      .text-xs     { font-size: calc(0.75rem * var(--ts)) !important; }
      .text-sm     { font-size: calc(0.875rem * var(--ts)) !important; }
      .text-base   { font-size: calc(1rem   * var(--ts)) !important; }
      .text-lg     { font-size: calc(1.125rem * var(--ts)) !important; }
      .text-xl     { font-size: calc(1.25rem * var(--ts)) !important; }
      .text-2xl    { font-size: calc(1.5rem  * var(--ts)) !important; }
      .text-3xl    { font-size: calc(1.875rem * var(--ts)) !important; }
      .text-4xl    { font-size: calc(2.25rem * var(--ts)) !important; }
      
      /* 針對沒帶類別的標題補強 */
      h2 { font-size: calc(1.5rem * var(--ts)) !important; }
      h3 { font-size: calc(1.25rem * var(--ts)) !important; }

      .material-symbols-outlined { 
        font-size: inherit !important; 
        vertical-align: middle;
      }
    `;
  }, [displaySettings]);

  // Load settings on startup
  useEffect(() => {
    const loadSettings = async () => {
      // @ts-ignore
      if (window.pywebview?.api) {
        // @ts-ignore
        const state = await window.pywebview.api.get_app_state();
        if (state.version) setAppVersion(state.version);

        // 載入設定

        if (state.settings) {
          if (state.settings.config) {
            // Force '登入' to be enabled by default as per user request, even if missing in saved config
            const loadedConfig = { ...state.settings.config };
            if (loadedConfig.keywords) {
              // Migrate old names
              loadedConfig.keywords = loadedConfig.keywords.map((k: string) => {
                if (k === '驗證碼') return '拼圖與人機驗證';
                if (k === '不存在') return '查無資料';
                return k;
              });

              // Ensure '登入' is at first position if not present or moved
              if (!loadedConfig.keywords.includes('登入')) {
                loadedConfig.keywords = ['登入', ...loadedConfig.keywords];
              } else {
                // Ensure '登入' is moved to the front if it's elsewhere
                const otherKws = loadedConfig.keywords.filter((k: string) => k !== '登入');
                loadedConfig.keywords = ['登入', ...otherKws];
              }

              // Ensure other defaults exist
              if (!loadedConfig.keywords.includes('拼圖與人機驗證')) loadedConfig.keywords.push('拼圖與人機驗證');
              if (!loadedConfig.keywords.includes('查無資料')) loadedConfig.keywords.push('查無資料');
              if (!loadedConfig.keywords.includes('BSMI')) loadedConfig.keywords.push('BSMI');
            } else {
              loadedConfig.keywords = ['登入', '拼圖與人機驗證', '查無資料', 'BSMI'];
            }

            // Ensure categoryPause exists and migrate keys
            if (loadedConfig.categoryPause) {
              const oldPause = loadedConfig.categoryPause;
              const newPause: any = {};
              Object.keys(oldPause).forEach(k => {
                let newKey = k;
                if (k === '驗證碼') newKey = '拼圖與人機驗證';
                if (k === '不存在') newKey = '查無資料';
                newPause[newKey] = oldPause[k];
              });
              loadedConfig.categoryPause = newPause;
            } else {
              loadedConfig.categoryPause = {
                '拼圖與人機驗證': true,
                '登入': true,
                '查無資料': false,
                'BSMI': false
              };
            }
            setConfig(prev => ({ ...prev, ...loadedConfig }));
          }
          if (state.settings.display) setDisplaySettings(prev => ({ ...prev, ...state.settings.display }));
        }

        // Check for updates
        // @ts-ignore
        const update = await window.pywebview.api.check_update();
        if (update && update.has_update) {
          setUpdateInfo(update);
        }
      }
    };
    // Wait for pywebview to be ready with retries
    let retryCount = 0;
    const maxRetries = 20; // 10 seconds total
    const retryInterval = setInterval(() => {
      // @ts-ignore
      if (window.pywebview?.api) {
        loadSettings();
        clearInterval(retryInterval);
      } else if (retryCount >= maxRetries) {
        console.error("Pywebview API failing to load after 10s");
        clearInterval(retryInterval);
      }
      retryCount++;
    }, 500);

    // Polling task status
    const interval = setInterval(async () => {
      // @ts-ignore
      // @ts-ignore
      if (window.pywebview?.api) {
        // @ts-ignore
        const status = await window.pywebview.api.get_task_status();
        if (status) {
          setTaskStatus(status);

          // Check for new errors
          const currentErrors = status.errors || [];
          if (currentErrors.length > lastErrorCount.current) {
            // New error detected!
            const newError = currentErrors[currentErrors.length - 1];
            const toastId = Date.now();
            setToasts(prev => [...prev, { id: toastId, ...newError }]);

            // Auto remove toast after 6 seconds
            setTimeout(() => {
              setToasts(prev => prev.filter(t => t.id !== toastId));
            }, 6000);

            lastErrorCount.current = currentErrors.length;
          }

          // Reset error count if status becomes idle and errors are cleared in backend (optional)
          if (status.status === 'idle' && currentErrors.length === 0) {
            lastErrorCount.current = 0;
          }
        }

        // Poll app state for history (every 2s might be heavy, maybe separate interval? 
        // optimize: only fetch if view is logs or header needs it. But header always needs it for notifications.
        // Let's optimize by fetching history separately or assuming get_app_state is fast enough)
        // @ts-ignore
        const appState = await window.pywebview.api.get_app_state();
        if (appState && appState.history) {
          setHistory(appState.history);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Save settings when they change
  useEffect(() => {
    const saveSettings = async () => {
      // @ts-ignore
      if (window.pywebview?.api) {
        // @ts-ignore
        await window.pywebview.api.save_settings({
          config,
          display: displaySettings
        });
      }
    };
    saveSettings();
  }, [config, displaySettings]);

  const handleSaveConfig = (newConfig: AutomationConfig) => {
    setConfig(newConfig);
    setIsConfigOpen(false);
  };

  const handleUpdateConfig = (updates: Partial<AutomationConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const handleShowLogs = (taskId: string) => {
    setActiveTaskId(taskId);
    setIsLogOpen(true);
  };

  // HTML5 Drag & Drop handlers (Removed)

  const handleCheckUpdate = async () => {
    // @ts-ignore
    if (window.pywebview?.api) {
      // @ts-ignore
      const update = await window.pywebview.api.check_update();
      if (update) {
        setUpdateInfo(update);
        setIsUpdateDialogOpen(true);
      }
    }
  };

  const handleUpdateScripts = async () => {
    setIsUpdatingScripts(true);
    // @ts-ignore
    if (window.pywebview?.api) {
      // @ts-ignore
      const res = await window.pywebview.api.update_scripts();
      setIsUpdatingScripts(false);
      if (res.status === 'success' || res.status === 'partial') {
        alert('核心邏輯已成功更新！無需重啟即可生效。');
        if (res.new_version) setAppVersion(res.new_version);
        setUpdateInfo(null);
      } else {
        alert('更新失敗: ' + res.message);
      }
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#f6f6f8] dark:bg-slate-950 transition-colors duration-300 font-sans">
      {/* Sidebar Component */}
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        version={appVersion}
        systemStatus={taskStatus.status}
        onCheckUpdate={handleCheckUpdate}
        hasUpdate={updateInfo?.has_update || false}
      />

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <Header
          onViewChange={setCurrentView}
          onShowLogs={handleShowLogs}
          onToggleHelp={() => setIsHelpOpen(true)}
          history={history}
        />

        <div className="flex-1 overflow-y-auto no-scrollbar">
          {currentView === 'dashboard' && (
            <Dashboard
              onOpenConfig={() => setIsConfigOpen(true)}
              onShowLogs={handleShowLogs}
              config={config}
              onUpdateConfig={handleUpdateConfig}
              taskStatus={taskStatus}
            />
          )}
          {currentView === 'logs' && <Logs history={history} onRefresh={() => { }} />}
          {currentView === 'settings' && (
            <Settings
              displaySettings={displaySettings}
              setDisplaySettings={setDisplaySettings}
            />
          )}
        </div>

        {/* Modals */}
        {isConfigOpen && (
          <ConfigurationModal
            config={config}
            onClose={() => setIsConfigOpen(false)}
            onSave={handleSaveConfig}
          />
        )}

        {isLogOpen && (
          <LogModal
            taskId={activeTaskId || ''}
            onClose={() => setIsLogOpen(false)}
          />
        )}

        <HelpModal
          isOpen={isHelpOpen}
          onClose={() => setIsHelpOpen(false)}
        />

        {/* Update Dialog */}
        {isUpdateDialogOpen && updateInfo && (
          <UpdateDialog
            updateInfo={updateInfo}
            onClose={() => setIsUpdateDialogOpen(false)}
          />
        )}

        {/* Floating Toast Notifications (Bottom Left) */}
        <div className="absolute bottom-6 left-6 z-[100] flex flex-col gap-3 pointer-events-none">
          {toasts.map((toast) => (
            <div
              key={toast.id}
              className="w-72 bg-white dark:bg-slate-900 border-l-4 border-red-500 shadow-2xl rounded-xl p-4 flex gap-3 animate-in slide-in-from-left-full duration-300 pointer-events-auto group"
            >
              <div className="size-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 shrink-0">
                <span className="material-symbols-outlined">report</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start">
                  <p className="text-[11px] font-black text-red-600 uppercase tracking-tighter">任務執行失敗</p>
                  <button
                    onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
                    className="text-slate-300 hover:text-slate-500 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[14px]">close</span>
                  </button>
                </div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-1 truncate">{toast.file}</p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">{toast.msg || '發生未知錯誤'}</p>
              </div>
            </div>
          ))}

          {/* Update Notification Toast */}
          {updateInfo?.has_update && !isUpdateDialogOpen && (
            <div className="w-80 bg-white dark:bg-slate-900 border-l-4 border-emerald-500 shadow-2xl rounded-xl p-4 flex gap-3 animate-in slide-in-from-left-full duration-500 pointer-events-auto ring-1 ring-emerald-500/10">
              <div className="size-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 shrink-0">
                <span className="material-symbols-outlined">auto_awesome</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start">
                  <p className="text-[11px] font-black text-emerald-600 uppercase tracking-tighter animate-pulse">✨ 發現新版本</p>
                  <button
                    onClick={() => setUpdateInfo(null)}
                    className="text-slate-300 hover:text-slate-500 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[14px]">close</span>
                  </button>
                </div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-1">
                  版本 {updateInfo.latest_version} 已發布！
                </p>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => {
                      // @ts-ignore
                      if (window.pywebview?.api) {
                        // @ts-ignore
                        window.pywebview.api.open_browser(updateInfo.release_url);
                      }
                    }}
                    className="text-[10px] bg-emerald-600 text-white px-3 py-1.5 rounded-lg font-bold hover:bg-emerald-700 transition-colors flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-xs">download</span>
                    下載主程式
                  </button>
                  <button
                    onClick={handleUpdateScripts}
                    disabled={isUpdatingScripts}
                    className="text-[10px] bg-slate-900 dark:bg-slate-700 text-white px-3 py-1.5 rounded-lg font-bold hover:bg-slate-800 transition-colors flex items-center gap-1 disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-xs animate-spin-slow">
                      {isUpdatingScripts ? 'sync' : 'auto_fix'}
                    </span>
                    {isUpdatingScripts ? '更新中...' : '僅更新核心邏輯'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Right Quick Action Panel Removed in v2.3.0 */}
    </div>
  );
};

export default App;
