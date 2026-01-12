
import React, { useRef, useState, useEffect } from 'react';
import { AutomationConfig, Task, TaskStatus } from '../types';

interface DashboardProps {
  onOpenConfig: () => void;
  onShowLogs: (taskId: string) => void;
  config: AutomationConfig;
  onUpdateConfig: (updates: Partial<AutomationConfig>) => void;
  jobQueue: any[];
  setJobQueue: (queue: any[]) => void;
}

const Dashboard: React.FC<DashboardProps> = ({
  onOpenConfig,
  onShowLogs,
  config,
  onUpdateConfig,
  jobQueue,
  setJobQueue
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [outputFiles, setOutputFiles] = useState<{ name: string, path: string }[]>([]);
  const [outputFolder, setOutputFolder] = useState<string | null>(null);
  const [isStartingTask, setIsStartingTask] = useState(false);
  const [defaultOutputDir, setDefaultOutputDir] = useState<string>('');
  const [isOutputListCollapsed, setIsOutputListCollapsed] = useState(false);

  // Screenshot State
  const [screenshotStatus, setScreenshotStatus] = useState<{ processed: number, total: number, status: string }>({ processed: 0, total: 0, status: 'idle' });
  const [appState, setAppState] = useState<any>({ stats: {}, history: [] });
  const screenshotFileInputRef = useRef<HTMLInputElement>(null);

  const handleMoveToScreenshot = (path: string, name: string, urlCount?: number) => {
    onUpdateConfig({
      inputFiles: [{ path, name, urlCount }]
    });
    alert(`已將「${name}」設定為自動截圖的輸入網址清單。`);
    const screenshotSection = document.getElementById('screenshot-card');
    if (screenshotSection) screenshotSection.scrollIntoView({ behavior: 'smooth' });
  };



  const handleUploadClick = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      // @ts-ignore
      const res = await window.pywebview.api.select_excel_file();
      if (res.status === 'success') {
        // Create a dummy File object for UI display
        setUploadedFile({ name: res.filename } as File);
        // Alert user
        console.log("File selected via bridge:", res.path);
      }
      return;
    }
    fileInputRef.current?.click();
  };

  // Polling State
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // @ts-ignore
        if (window.pywebview && window.pywebview.api) {
          // @ts-ignore
          const status = await window.pywebview.api.get_task_status();
          if (status) setScreenshotStatus(status);

          // @ts-ignore
          const state = await window.pywebview.api.get_app_state();
          if (state) setAppState(state);
        } else {
          // Fallback for dev mode
          const res = await fetch('http://localhost:8000/api/status');
          const data = await res.json();
          console.log("System Status:", data);
        }
      } catch (e) {
        console.error("Failed to poll status", e);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Update default output dir when input file changes
  useEffect(() => {
    const updateDefaultDir = async () => {
      // @ts-ignore
      if (window.pywebview && window.pywebview.api && config.inputFiles?.[0]?.path) {
        // @ts-ignore
        const res = await window.pywebview.api.get_default_output_dir(config.inputFiles[0].path);
        if (res) setDefaultOutputDir(res);
      } else {
        setDefaultOutputDir('');
      }
    };
    updateDefaultDir();
  }, [config.inputFiles]);


  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);

      // Check if we are in pywebview environment
      // @ts-ignore
      if (window.pywebview && window.pywebview.api) {
        console.log("Running in PyWebView session");
      }

      // Fallback/Legacy upload
      const formData = new FormData();
      formData.append('file', file);
      try {
        await fetch('http://localhost:8000/api/upload', {
          method: 'POST',
          body: formData,
        });
      } catch (e) {
        // Silently fail if server not present, as expected in local webview mode
      }
    }
  };

  const handleConvert = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      try {
        // @ts-ignore
        const res = await window.pywebview.api.run_excel_convert();
        if (res.status === 'success') {
          setOutputFiles(res.output_files || []);
          setOutputFolder(res.output_folder);
          alert("轉換完成！");
        } else {
          alert(res.message);
        }
      } catch (e) {
        alert("轉換出錯: " + e);
      }
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/convert', { method: 'POST' });
      const data = await res.json();
      alert("轉換任務狀態: " + data.status);
    } catch (e) {
      alert("啟動轉換失敗: " + e);
    }
  };

  const handleStartScreenshot = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      setIsStartingTask(true);
      try {
        // @ts-ignore
        const res = await window.pywebview.api.start_screenshot(config);
        if (res.status === 'success') {
          // Success feedback
          console.log("Task started:", res.message);
        } else {
          alert("啟動失敗: " + res.message);
        }
      } catch (e) {
        alert("啟動出錯: " + e);
      } finally {
        setIsStartingTask(false);
      }
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/screenshot/start', { method: 'POST' });
      const data = await res.json();
      alert("截圖任務狀態: " + data.status);
    } catch (e) {
      alert("啟動截圖失敗: " + e);
    }
  };

  const handleAddToQueue = () => {
    if (!config.inputFiles || config.inputFiles.length === 0) {
      alert("請先選擇輸入檔案");
      return;
    }
    const newQueue = [...jobQueue];
    // Add items that are not already in queue
    let addedCount = 0;
    config.inputFiles.forEach(file => {
      if (!newQueue.some(q => q.path === file.path)) {
        newQueue.push(file);
        addedCount++;
      }
    });

    setJobQueue(newQueue);
    // Clear selection in Dashboard after scheduling
    onUpdateConfig({ inputFiles: [] });
    alert(`已將 ${addedCount} 個項目加入工作佇列`);
  };

  const handleStopScreenshot = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      // @ts-ignore
      await window.pywebview.api.stop_screenshot();
      alert("已發送停止信號");
      return;
    }

    try {
      await fetch('http://localhost:8000/api/screenshot/stop', { method: 'POST' });
      alert("已發送停止信號");
    } catch (e) {
      alert("停止失敗: " + e);
    }
  };

  const handleScreenshotFileSelect = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      // @ts-ignore
      const res = await window.pywebview.api.select_multiple_files();
      if (res.status === 'success' && res.files) {
        // Append new files to existing list
        const currentFiles = config.inputFiles || [];
        const newFiles = res.files.filter((nf: any) => !currentFiles.some((cf: any) => cf.path === nf.path));
        onUpdateConfig({
          inputFiles: [...currentFiles, ...newFiles]
        });
        alert(`已加入 ${newFiles.length} 個檔案`);
      }
    } else {
      alert("此功能僅在桌面應用程式中可用");
    }
  };

  const handleScreenshotFolderSelect = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      // @ts-ignore
      const res = await window.pywebview.api.select_input_folder();
      if (res.status === 'success') {
        const currentFiles = config.inputFiles || [];
        // Add folder as a meta-item, backend will expand it
        const folderItem = { path: res.path, name: `[資料夾] ${res.name}`, isDir: true };
        if (!currentFiles.some((cf: any) => cf.path === res.path)) {
          onUpdateConfig({
            inputFiles: [...currentFiles, folderItem]
          });
          alert(`已加入資料夾: ${res.name} (將掃描其中 TXT)`);
        }
      }
    } else {
      alert("此功能僅在桌面應用程式中可用");
    }
  };

  const handleScreenshotRemoveFile = (index: number) => {
    const currentFiles = [...(config.inputFiles || [])];
    currentFiles.splice(index, 1);
    onUpdateConfig({
      inputFiles: currentFiles
    });
  };

  const handleScreenshotDirSelect = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      // @ts-ignore
      const res = await window.pywebview.api.select_directory();
      if (res.status === 'success') {
        onUpdateConfig({
          outputDir: res.path,
          outputDirDisplay: res.dirname
        });
        alert(`已選擇輸出資料夾: ${res.dirname}`);
      }
    } else {
      alert("此功能僅在桌面應用程式中可用");
    }
  };

  const handleResetAll = () => {
    if (confirm("確定要清空目前的輸入檔案與輸出結果嗎？")) {
      setUploadedFile(null);
      setOutputFiles([]);
      setOutputFolder('');
      onUpdateConfig({
        inputFiles: [],
        outputDir: undefined,
        outputDirDisplay: undefined
      });
    }
  };

  const shortenPath = (path: string, maxLength: number = 25) => {
    if (!path) return '';
    if (path.length <= maxLength) return path;
    return '...' + path.slice(-(maxLength - 3));
  };

  const handleScreenshotRemoveDir = (e: React.MouseEvent) => {
    e.stopPropagation();
    onUpdateConfig({
      outputDir: undefined,
      outputDirDisplay: undefined
    });
  };

  const handleScreenshotUploadClick = () => {
    handleScreenshotFileSelect();
  };
  const handleRemoveFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };


  return (
    <div className="p-8 space-y-8 max-w-[1400px] mx-auto transition-all">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black tracking-tight mb-1 dark:text-white">工作自動化控制中心</h2>
          <p className="text-slate-500 dark:text-slate-400">管理您的 Excel 數據處理與網頁自動化工具。</p>
        </div>

        {/* Header Stats */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm pr-2">
          <div className="flex items-center gap-0">
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-0.5">累計轉換</span>
              <span className="text-lg font-black text-emerald-600 leading-none">{appState.stats.total_conversions || 0}</span>
            </div>
            <div className="w-px h-8 bg-slate-100 dark:bg-slate-800"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-0.5">執行任務</span>
              <span className="text-lg font-black text-slate-800 dark:text-white leading-none">{appState.stats.total_tasks || 0}</span>
            </div>
            <div className="w-px h-8 bg-slate-100 dark:bg-slate-800"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-0.5">成功率</span>
              <span className="text-lg font-black text-blue-600 leading-none">{appState.stats.success_rate || "100%"}</span>
            </div>
            <div className="w-px h-8 bg-slate-100 dark:bg-slate-800"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-0.5">實時計時</span>
              <span className="text-lg font-black text-indigo-600 leading-none">{appState.stats.time_saved || "0s"}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Card: Excel to TXT */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col gap-6 hover:shadow-md transition-all xl:col-span-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                <span className="material-symbols-outlined">table_chart</span>
              </div>
              <div>
                <h3 className="font-bold text-slate-800 dark:text-white">Excel 轉 TXT</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">拖放式檔案處理</p>
              </div>
            </div>
            <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${uploadedFile ? 'bg-blue-600/10 text-blue-600' : 'bg-emerald-500/10 text-emerald-500'}`}>
              {uploadedFile ? '已上傳' : '就緒'}
            </span>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
          />

          {uploadedFile ? (
            <div
              className="flex flex-col items-center justify-center gap-3 py-10 px-6 rounded-xl border-2 border-emerald-500/30 bg-emerald-50/20 dark:bg-emerald-500/5 transition-all group relative"
            >
              <div className="size-14 rounded-full bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <span className="material-symbols-outlined text-3xl">description</span>
              </div>
              <div className="text-center w-full px-2">
                <p className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">{uploadedFile.name}</p>
                <p className="text-[10px] text-slate-400 mt-1 uppercase">{(uploadedFile.size / 1024).toFixed(1)} KB • Excel 試算表</p>
              </div>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={handleRemoveFile}
                  className="px-4 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-bold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all shadow-sm"
                >
                  移除檔案
                </button>
                <button
                  onClick={handleConvert}
                  className="px-4 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-bold hover:bg-emerald-600 transition-all shadow-md"
                >
                  開始轉換
                </button>
                <button
                  onClick={handleUploadClick}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700 transition-all shadow-md"
                >
                  更換
                </button>
              </div>
            </div>
          ) : (
            <div
              onClick={handleUploadClick}
              className="flex flex-col items-center justify-center gap-4 py-10 px-6 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 group cursor-pointer hover:border-blue-600/50 transition-all"
            >
              <div className="size-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-blue-600 group-hover:bg-blue-600/10 transition-colors">
                <span className="material-symbols-outlined text-3xl">upload_file</span>
              </div>
              <div className="text-center">
                <p className="text-sm font-bold dark:text-slate-200">選擇 Excel 檔案</p>
                <p className="text-xs text-slate-400 max-w-[200px] mt-1">點擊或拖放 Excel (.xlsx, .xls) 或 CSV 檔案</p>
              </div>
              <button className="mt-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-bold hover:shadow-md transition-all dark:text-slate-300">
                瀏覽檔案
              </button>
            </div>
          )}

          <div className="flex flex-col text-xs font-medium text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-4 gap-2">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-sm text-slate-400">history</span>
                <span className="font-bold">輸出清單 {outputFiles.length > 0 && `(${outputFiles.length})`}</span>
              </div>
              <div className="flex items-center gap-2">
                {outputFolder && (
                  <button
                    onClick={() => {
                      // @ts-ignore
                      if (window.pywebview && window.pywebview.api) window.pywebview.api.open_folder(outputFolder);
                    }}
                    className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded flex items-center justify-center text-slate-400 hover:text-blue-600 transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">folder_open</span>
                  </button>
                )}
                <button
                  onClick={() => setIsOutputListCollapsed(!isOutputListCollapsed)}
                  className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded flex items-center justify-center text-slate-400 transition-colors"
                  title={isOutputListCollapsed ? '展開' : '收合'}
                >
                  <span className="material-symbols-outlined text-sm">
                    {isOutputListCollapsed ? 'expand_more' : 'expand_less'}
                  </span>
                </button>
              </div>
            </div>

            {!isOutputListCollapsed && (
              <div className="max-h-40 overflow-y-auto space-y-2 pr-1 custom-scrollbar animate-in fade-in slide-in-from-top-1 duration-200">
                {outputFiles.length > 0 ? (
                  outputFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg group">
                      <span
                        className="truncate text-blue-600 font-medium cursor-pointer hover:underline max-w-[150px]"
                        title={file.name}
                        onClick={() => {
                          // @ts-ignore
                          if (window.pywebview && window.pywebview.api) window.pywebview.api.open_file(file.path);
                        }}
                      >
                        {file.name}
                      </span>
                      <button
                        onClick={() => handleMoveToScreenshot(file.path, file.name, (file as any).urlCount)}
                        className="opacity-0 group-hover:opacity-100 px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-bold hover:bg-blue-700 transition-all whitespace-nowrap"
                      >
                        下一步
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-slate-400 animate-pulse italic">
                    {uploadedFile ? '正在等待轉換...' : '暫無待處理檔案'}
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-between items-center text-[10px] text-slate-400 mt-1 uppercase tracking-wider">
              <span>{outputFiles.length > 0 ? '處理完成' : (uploadedFile ? '準備就緒' : '--')}</span>
              {outputFiles.length > 0 && <span>可捲動查看更多</span>}
            </div>
          </div>
        </div>





        {/* Card: 自動截圖 (Merged Control & Config) */}
        <div id="screenshot-card" className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col gap-6 hover:shadow-md transition-all xl:col-span-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center">
                <span className="material-symbols-outlined">language</span>
              </div>
              <div>
                <h3 className="font-bold text-slate-800 dark:text-white">自動截圖</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">網頁自動化任務</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={onOpenConfig}
                className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-blue-600 transition-colors"
                title="進階設定"
              >
                <span className="material-symbols-outlined text-sm">settings</span>
              </button>
              <div className="flex gap-1.5">
                <button
                  onClick={handleStartScreenshot}
                  disabled={!config.inputFiles || config.inputFiles.length === 0 || isStartingTask}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 text-white text-[10px] font-black uppercase tracking-wider hover:bg-emerald-700 transition-all disabled:opacity-50 disabled:hover:scale-100 active:scale-95 shadow-lg shadow-emerald-500/20 flex items-center gap-2"
                >
                  {isStartingTask ? (
                    <span className="material-symbols-outlined animate-spin text-sm">sync</span>
                  ) : (
                    <span className="material-symbols-outlined text-sm">play_arrow</span>
                  )}
                  {isStartingTask ? '啟動中...' : '啟動任務'}
                </button>
                <button
                  onClick={handleAddToQueue}
                  disabled={!config.inputFiles || config.inputFiles.length === 0}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-white dark:text-slate-900 text-white text-[10px] font-black uppercase tracking-wider hover:bg-slate-800 transition-all disabled:opacity-50 disabled:hover:scale-100 active:scale-95"
                >
                  排定任務
                </button>
                <button
                  onClick={handleResetAll}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 text-[10px] font-black uppercase tracking-wider hover:bg-slate-50 dark:hover:bg-slate-800 transition-all active:scale-95"
                >
                  <span className="flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-sm">restart_alt</span>
                    清除內容
                  </span>
                </button>
                <button
                  onClick={handleStopScreenshot}
                  disabled={screenshotStatus.status !== 'running'}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 ${screenshotStatus.status === 'running'
                    ? 'bg-red-600/10 text-red-600 hover:bg-red-600 hover:text-white'
                    : 'bg-slate-100 text-slate-300 cursor-not-allowed'
                    }`}
                >
                  停止
                </button>
              </div>
            </div>
          </div>

          {/* Removed old single file input */}
          {/* <input
            type="file"
            ref={screenshotFileInputRef}
            className="hidden"
            accept=".txt"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                alert("請使用「選擇檔案」按鈕以選取完整路徑。");
              }
            }}
          /> */}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Input File Section */}
            <div className="space-y-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">網址清單</p>
              {config.inputFiles && config.inputFiles.length > 0 ? (
                <div className="space-y-2">
                  {config.inputFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 p-3 rounded-xl border border-blue-500/30 bg-blue-50/20 dark:bg-blue-500/5 group relative"
                    >
                      <div className="size-8 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 shrink-0">
                        <span className="material-symbols-outlined text-lg">description</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{file.name}</p>
                        <button
                          onClick={() => handleScreenshotRemoveFile(index)}
                          className="text-[9px] text-red-500 font-bold hover:underline"
                        >
                          移除
                        </button>
                      </div>
                      {/* Edit button for individual file might not be needed for multiple files, or could re-open selection */}
                    </div>
                  ))}
                  <div className="flex justify-start gap-2">
                    <button
                      onClick={handleScreenshotFileSelect}
                      className="flex items-center justify-center gap-2 p-3 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 cursor-pointer hover:border-blue-600/50 transition-all text-[10px] font-black text-slate-400 hover:text-blue-600 uppercase"
                    >
                      <span className="material-symbols-outlined text-[16px]">add_circle</span>
                      新增檔案
                    </button>
                    <button
                      onClick={handleScreenshotFolderSelect}
                      className="flex items-center justify-center gap-2 p-3 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 cursor-pointer hover:border-emerald-600/50 transition-all text-[10px] font-black text-slate-400 hover:text-emerald-600 uppercase"
                    >
                      <span className="material-symbols-outlined text-[16px]">folder_open</span>
                      選取資料夾
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div
                    onClick={handleScreenshotFileSelect}
                    className="flex items-center gap-3 p-4 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-all border-spacing-4 group"
                  >
                    <div className="size-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-all">
                      <span className="material-symbols-outlined">add_circle</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold dark:text-white">選擇多個檔案</p>
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Select TXT Files</p>
                    </div>
                  </div>

                  <div
                    onClick={handleScreenshotFolderSelect}
                    className="flex items-center gap-3 p-4 rounded-xl border border-dashed border-emerald-500/20 dark:border-emerald-500/10 bg-emerald-50/20 dark:bg-emerald-500/5 cursor-pointer hover:bg-emerald-50 dark:hover:bg-emerald-500/10 transition-all border-spacing-4 group"
                  >
                    <div className="size-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-all">
                      <span className="material-symbols-outlined">folder_open</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold dark:text-white">選擇整份資料夾</p>
                      <p className="text-[10px] text-emerald-500/70 uppercase font-bold tracking-widest">Select Folder</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Output Dir Section */}
            <div className="space-y-2 flex flex-col h-full">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">輸出資料夾</p>
              <div className="flex-1 min-h-[140px] flex flex-col gap-3 p-2">
                {config.outputDir ? (
                  <div className="flex items-center gap-3 p-3 bg-white dark:bg-slate-900 rounded-xl border border-emerald-500/20 shadow-sm group">
                    <div className="size-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center text-emerald-600 shrink-0">
                      <span className="material-symbols-outlined">folder</span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{config.outputDirDisplay}</p>
                      <p className="text-[10px] text-slate-400 truncate font-mono">{shortenPath(config.outputDir, 35)}</p>
                    </div>
                    <button onClick={handleScreenshotRemoveDir} className="p-1.5 text-slate-300 hover:text-red-500 transition-colors">
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={handleScreenshotDirSelect}
                    className="flex flex-col gap-2 p-4 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/20 dark:bg-slate-800/20 cursor-pointer group hover:border-blue-600/50 transition-all"
                  >
                    <div className="flex items-start gap-4">
                      <div className="size-10 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-blue-600 transition-colors">
                        <span className="material-symbols-outlined text-2xl">create_new_folder</span>
                      </div>
                      <div className="space-y-2">
                        <p className="text-[13px] font-bold text-slate-600 dark:text-slate-300 group-hover:text-blue-600 transition-colors leading-relaxed whitespace-pre-line">
                          選擇輸出資料夾{"\n"}
                          或使用預設
                        </p>
                        <div className="pt-1">
                          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">預設地址</p>
                          <p className="text-[10px] text-slate-400 font-mono break-all leading-tight mt-1 opacity-70 group-hover:opacity-100 transition-opacity">
                            {defaultOutputDir ? shortenPath(defaultOutputDir, 50) : '（請先選擇輸入檔案）'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Content moved to bottom bar per user request */}
              </div>
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="flex flex-col gap-2 py-4 px-2 bg-slate-50/50 dark:bg-slate-800/30 rounded-xl">
            <div className="flex justify-between text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest px-1">
              <span>任務進度</span>
              <span>{screenshotStatus.processed} / {screenshotStatus.total}</span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${screenshotStatus.total > 0 ? (screenshotStatus.processed / screenshotStatus.total) * 100 : 0}%` }}
              ></div>
            </div>
            <div className="text-center text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              {screenshotStatus.status === 'running' ? '執行中...' : (screenshotStatus.processed > 0 && screenshotStatus.processed === screenshotStatus.total ? '已完成' : '等待啟動')}
            </div>
          </div>

          <div className="space-y-4 border-t border-slate-100 dark:border-slate-800 pt-5">
            {/* Latest Output Section */}
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-100 dark:border-slate-800 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">最新輸出</span>
                <button
                  onClick={() => {
                    // @ts-ignore
                    if (window.pywebview && window.pywebview.api) {
                      const path = appState.latest_screenshot_folder || config.outputDir || config.output_dir;
                      if (path) {
                        // @ts-ignore
                        window.pywebview.api.open_folder(path);
                      } else {
                        alert("尚未執行任務或找不到資料夾");
                      }
                    }
                  }}
                  className="text-[10px] font-bold text-blue-600 hover:underline cursor-pointer"
                >
                  開啟資料夾
                </button>
              </div>

              {/* Latest Results Listing Integrated here */}
              <div className="space-y-2 overflow-y-auto custom-scrollbar max-h-[160px]">
                {appState.latest_screenshot_results && appState.latest_screenshot_results.length > 0 ? (
                  appState.latest_screenshot_results.map((res: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-white dark:bg-slate-900 rounded-lg shadow-sm group">
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <span className="material-symbols-outlined text-xs text-blue-500">description</span>
                        <span
                          className="truncate text-[11px] font-medium text-slate-700 dark:text-slate-300 cursor-pointer hover:text-blue-600 hover:underline"
                          title={res.name}
                          onClick={() => {
                            // @ts-ignore
                            if (window.pywebview && window.pywebview.api) window.pywebview.api.open_file(res.path);
                          }}
                        >
                          {res.name}
                        </span>
                      </div>
                      <span className="text-[9px] text-slate-400 ml-2 shrink-0">DOCX</span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-[10px] text-slate-400 italic font-medium">
                    {screenshotStatus.status === 'running' ? '正在生成輸出...' : '暫無執行輸出'}
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>


      </div>

    </div>
  );
};

export default Dashboard;
