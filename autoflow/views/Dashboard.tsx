
import React, { useRef, useState, useEffect } from 'react';
import { AutomationConfig, Task, TaskStatus } from '../types';

interface DashboardProps {
  onOpenConfig: () => void;
  onShowLogs: (taskId: string) => void;
  config: AutomationConfig;
  onUpdateConfig: (updates: Partial<AutomationConfig>) => void;
  taskStatus: TaskStatus;
}

const Dashboard: React.FC<DashboardProps> = ({
  onOpenConfig,
  onShowLogs,
  config,
  onUpdateConfig,
  taskStatus
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [outputFiles, setOutputFiles] = useState<{ name: string, path: string }[]>([]);
  const [outputFolder, setOutputFolder] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ start: string, end: string }>({ start: '', end: '' });
  const [isStartingTask, setIsStartingTask] = useState(false);
  const [defaultOutputDir, setDefaultOutputDir] = useState<string>('');
  const [isOutputListCollapsed, setIsOutputListCollapsed] = useState(false);
  const [selectedOutputFiles, setSelectedOutputFiles] = useState<Set<number>>(new Set());

  // Screenshot State
  const [screenshotStatus, setScreenshotStatus] = useState<{ processed: number, total: number, status: string }>({ processed: 0, total: 0, status: 'idle' });
  const [appState, setAppState] = useState<any>({ stats: {}, history: [] });

  const handleMoveToScreenshot = (path: string, name: string, urlCount?: number) => {
    // 累加模式：將新檔案加入現有的輸入清單
    const existingFiles = config.inputFiles || [];
    const newFile = { path, name, urlCount };

    // 檢查是否已存在（避免重複）
    const isDuplicate = existingFiles.some(f => f.path === path);
    if (isDuplicate) {
      alert(`「${name}」已在自動截圖清單中。`);
      return;
    }

    onUpdateConfig({
      inputFiles: [...existingFiles, newFile]
    });
    alert(`已將「${name}」加入自動截圖的輸入網址清單。`);
    const screenshotSection = document.getElementById('screenshot-card');
    if (screenshotSection) screenshotSection.scrollIntoView({ behavior: 'smooth' });
  };

  const handleMoveSelectedToScreenshot = () => {
    if (selectedOutputFiles.size === 0) {
      alert('請先選擇要移動的檔案');
      return;
    }
    const selectedFiles = Array.from(selectedOutputFiles)
      .map(idx => outputFiles[idx])
      .filter(f => f);

    // 累加模式：將新檔案加入現有的輸入清單
    const existingFiles = config.inputFiles || [];
    const newFiles = selectedFiles.map(f => ({
      path: f.path,
      name: f.name,
      urlCount: (f as any).urlCount
    }));

    // 過濾已存在的檔案
    const existingPaths = new Set(existingFiles.map(f => f.path));
    const filesToAdd = newFiles.filter(f => !existingPaths.has(f.path));

    if (filesToAdd.length === 0) {
      alert('選取的檔案已全部在自動截圖清單中。');
      return;
    }

    onUpdateConfig({
      inputFiles: [...existingFiles, ...filesToAdd]
    });

    alert(`已將 ${filesToAdd.length} 個檔案加入自動截圖的輸入網址清單。`);
    setSelectedOutputFiles(new Set());
    const screenshotSection = document.getElementById('screenshot-card');
    if (screenshotSection) screenshotSection.scrollIntoView({ behavior: 'smooth' });
  };

  const handleMoveAllToScreenshot = () => {
    if (outputFiles.length === 0) {
      alert('沒有可移動的檔案');
      return;
    }

    // 累加模式：將新檔案加入現有的輸入清單
    const existingFiles = config.inputFiles || [];
    const newFiles = outputFiles.map(f => ({
      path: f.path,
      name: f.name,
      urlCount: (f as any).urlCount
    }));

    // 過濾已存在的檔案
    const existingPaths = new Set(existingFiles.map(f => f.path));
    const filesToAdd = newFiles.filter(f => !existingPaths.has(f.path));

    if (filesToAdd.length === 0) {
      alert('所有檔案已全部在自動截圖清單中。');
      return;
    }

    onUpdateConfig({
      inputFiles: [...existingFiles, ...filesToAdd]
    });

    alert(`已將全部 ${filesToAdd.length} 個檔案加入自動截圖的輸入網址清單。`);
    setSelectedOutputFiles(new Set());
    const screenshotSection = document.getElementById('screenshot-card');
    if (screenshotSection) screenshotSection.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleFileSelection = (idx: number) => {
    const newSelection = new Set(selectedOutputFiles);
    if (newSelection.has(idx)) {
      newSelection.delete(idx);
    } else {
      newSelection.add(idx);
    }
    setSelectedOutputFiles(newSelection);
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
        const res = await window.pywebview.api.run_excel_convert(dateRange.start, dateRange.end);
        if (res.status === 'success') {
          setOutputFiles(res.output_files || []);
          setOutputFolder(res.output_folder);
          alert(res.message);
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
    // Removed in v2.3.0
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
      const res = await window.pywebview.api.select_directory();
      if (res.status === 'success' && res.path) {
        const currentFiles = config.inputFiles || [];
        const newFolder = { path: res.path, name: `[資料夾] ${res.dirname}`, isDir: true };

        if (!currentFiles.some((cf: any) => cf.path === newFolder.path)) {
          onUpdateConfig({
            inputFiles: [...currentFiles, newFolder]
          });
          // alert(`已加入來源資料夾: ${res.dirname}`); // Optional alert
        } else {
          alert(`資料夾 '${res.dirname}' 已存在於清單中`);
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

  const handleResetAll = async () => {
    if (confirm("確定要清空目前的輸入檔案與輸出結果嗎？")) {
      // @ts-ignore
      if (window.pywebview && window.pywebview.api) {
        // @ts-ignore
        await window.pywebview.api.clear_latest_results();
      }
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

  const handleRemoveFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };


  return (
    <div className="p-8 space-y-8 max-w-[1400px] mx-auto transition-all">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black tracking-tight mb-1 dark:text-white">工作自動化控制中心</h2>
          <p className="text-slate-500 dark:text-slate-400">管理您的 Excel 數據處理與網頁自動化工具。</p>
        </div>

        {/* Header Stats */}
        <div className="flex items-center bg-slate-50/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm px-1">
          <div className="flex">
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-0.5">累計轉換</span>
              <span className="text-lg font-black text-emerald-500 leading-none">{appState.stats.total_conversions || 0}</span>
            </div>
            <div className="w-px h-8 bg-slate-200/50 dark:bg-white/5 self-center"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-0.5">執行任務</span>
              <span className="text-lg font-black text-slate-800 dark:text-slate-200 leading-none">{appState.stats.total_tasks || 0}</span>
            </div>
            <div className="w-px h-8 bg-slate-200/50 dark:bg-white/5 self-center"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-0.5">成功率</span>
              <span className="text-lg font-black text-blue-500 leading-none">{appState.stats.total_conversions > 0 ? (appState.stats.success_rate || "100%") : "-"}</span>
            </div>
            <div className="w-px h-8 bg-slate-200/50 dark:bg-white/5 self-center"></div>
            <div className="flex flex-col items-center px-4 py-2">
              <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-0.5">實時計時</span>
              <span className="text-lg font-black text-indigo-500 leading-none">{appState.stats.time_saved || "0s"}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        {/* Column 1: Excel & Date Filter */}
        <div className="flex flex-col gap-6 xl:col-span-2">
          <div className="bg-white/80 dark:bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-white/5 p-6 shadow-sm flex flex-col gap-6 hover:shadow-xl hover:shadow-blue-500/5 transition-all h-full">

            {/* 1. Excel Selection */}
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/10">
                    <span className="material-symbols-outlined">table_chart</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-800 dark:text-slate-200 tracking-tight">Excel 轉 TXT</h3>
                    <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">拖放式檔案處理</p>
                  </div>
                </div>
              </div>

              <input type="file" ref={fileInputRef} className="hidden" accept=".xlsx,.xls,.csv" onChange={handleFileChange} />

              {uploadedFile ? (
                <div className="flex flex-col items-center justify-center gap-3 py-6 px-6 rounded-xl border-2 border-emerald-500/30 bg-emerald-50/20 dark:bg-emerald-500/5 transition-all group relative">
                  <div className="size-10 rounded-full bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                    <span className="material-symbols-outlined text-2xl">description</span>
                  </div>
                  <div className="text-center w-full px-2">
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">{uploadedFile.name}</p>
                    <p className="text-[10px] text-slate-400 mt-1 uppercase">{(uploadedFile.size / 1024).toFixed(1)} KB • Excel 試算表</p>
                  </div>
                  <button onClick={handleRemoveFile} className="px-3 py-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded text-xs font-bold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all shadow-sm">
                    移除檔案
                  </button>
                </div>
              ) : (
                <div onClick={handleUploadClick} className="flex flex-col items-center justify-center gap-2 py-6 px-6 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30 group cursor-pointer hover:border-blue-600/50 transition-all">
                  <div className="size-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-blue-600 group-hover:bg-blue-600/10 transition-colors">
                    <span className="material-symbols-outlined text-2xl">upload_file</span>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-bold dark:text-slate-200">選擇 Excel 檔案</p>
                    <p className="text-[10px] text-slate-400 mt-1">支援 .xlsx, .xls</p>
                  </div>
                </div>
              )}
            </div>

            <div className="w-full h-px bg-slate-100 dark:bg-slate-800 my-1"></div>

            {/* 2. Date Filter */}
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="size-8 rounded-lg bg-indigo-500/10 text-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/10">
                  <span className="material-symbols-outlined text-lg">date_range</span>
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-200 text-sm tracking-tight">日期篩選 (選填)</h3>
                  <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">僅轉換此區間內的資料</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <style>{`
                  /* 1. 強制全域設定: 淺色模式下所有日期相關元件一律黑色 */
                  input[type="date"],
                  input[type="date"]::-webkit-datetime-edit,
                  input[type="date"]::-webkit-datetime-edit-fields-wrapper,
                  input[type="date"]::-webkit-datetime-edit-text,
                  input[type="date"]::-webkit-datetime-edit-year-field,
                  input[type="date"]::-webkit-datetime-edit-month-field,
                  input[type="date"]::-webkit-datetime-edit-day-field {
                    color: black !important;
                  }

                  /* 2. 選取狀態（藍色背景）下也強制黑色 */
                  input[type="date"]::-webkit-datetime-edit-year-field:focus,
                  input[type="date"]::-webkit-datetime-edit-month-field:focus,
                  input[type="date"]::-webkit-datetime-edit-day-field:focus {
                    background-color: #3b82f6 !important;
                    color: black !important;
                  }

                  /* 3. 深色模式覆寫: 全部白色 */
                  .dark input[type="date"],
                  .dark input[type="date"]::-webkit-datetime-edit,
                  .dark input[type="date"]::-webkit-datetime-edit-fields-wrapper,
                  .dark input[type="date"]::-webkit-datetime-edit-text,
                  .dark input[type="date"]::-webkit-datetime-edit-year-field,
                  .dark input[type="date"]::-webkit-datetime-edit-month-field,
                  .dark input[type="date"]::-webkit-datetime-edit-day-field {
                    color: white !important;
                  }
                  
                  /* 4. 深色模式選取狀態: 白色 */
                  .dark input[type="date"]::-webkit-datetime-edit-year-field:focus,
                  .dark input[type="date"]::-webkit-datetime-edit-month-field:focus,
                  .dark input[type="date"]::-webkit-datetime-edit-day-field:focus {
                     color: white !important;
                  }

                  /* 5. 圖示濾鏡 */
                  input[type="date"]::-webkit-calendar-picker-indicator {
                    cursor: pointer;
                    opacity: 0.6;
                    filter: invert(0) !important; /* 強制黑色圖示 */
                  }
                  .dark input[type="date"]::-webkit-calendar-picker-indicator {
                    filter: invert(1) !important; /* 強制白色圖示 */
                  }
                `}</style>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">開始日期</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all relative"
                    value={dateRange.start}
                    onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">結束日期</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all relative"
                    value={dateRange.end}
                    onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                  />
                </div>
              </div>

              {dateRange.start && dateRange.end && new Date(dateRange.start) > new Date(dateRange.end) && (
                <div className="mx-1 flex items-center gap-1.5 text-red-500 animate-in fade-in slide-in-from-top-1 duration-200">
                  <span className="material-symbols-outlined text-sm font-bold">error</span>
                  <p className="text-[10px] font-bold uppercase tracking-tight">開始日期不能晚於結束日期</p>
                </div>
              )}

              <button
                onClick={handleConvert}
                disabled={!uploadedFile || (!!dateRange.start && !!dateRange.end && new Date(dateRange.start) > new Date(dateRange.end))}
                className="w-full py-3 bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-xl text-sm font-black uppercase tracking-widest hover:brightness-110 hover:shadow-lg hover:shadow-emerald-500/20 transition-all shadow-md disabled:opacity-30 disabled:cursor-not-allowed active:scale-[0.98]"
              >
                開始轉換
              </button>
            </div>

            <div className="w-full h-px bg-slate-100 dark:bg-slate-800 my-1"></div>

            {/* 3. Output List */}
            <div className="flex flex-col gap-2 flex-1 min-h-[100px]">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm text-slate-400">history</span>
                  <span className="font-bold text-xs">輸出清單 {outputFiles.length > 0 && `(${outputFiles.length})`}</span>
                  {selectedOutputFiles.size > 0 && (
                    <span className="text-[10px] font-bold text-blue-600 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-full">
                      已選 {selectedOutputFiles.size}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  {outputFiles.length > 0 && (
                    <>
                      {selectedOutputFiles.size > 0 && (
                        <button
                          onClick={handleMoveSelectedToScreenshot}
                          className="px-2 py-1 bg-blue-600 text-white rounded text-[10px] font-black hover:bg-blue-700 transition-all"
                          title="將選取的檔案移至自動截圖"
                        >
                          移至下一步
                        </button>
                      )}
                      <button
                        onClick={handleMoveAllToScreenshot}
                        className="px-2 py-1 bg-emerald-600 text-white rounded text-[10px] font-black hover:bg-emerald-700 transition-all"
                        title="將全部檔案移至自動截圖"
                      >
                        全部移至下一步
                      </button>
                    </>
                  )}
                  {outputFiles.length > 0 && (
                    <button
                      onClick={() => { if (window.pywebview?.api && outputFolder) window.pywebview.api.open_folder(outputFolder); }}
                      className="p-1 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded flex items-center justify-center text-blue-600 transition-colors"
                      title="開啟輸出資料夾"
                    >
                      <span className="material-symbols-outlined text-[16px]">folder_open</span>
                    </button>
                  )}
                  <button
                    onClick={() => setIsOutputListCollapsed(!isOutputListCollapsed)}
                    className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded flex items-center justify-center text-slate-400 transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">{isOutputListCollapsed ? 'expand_more' : 'expand_less'}</span>
                  </button>
                </div>
              </div>

              {!isOutputListCollapsed && (
                <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar max-h-[200px]">
                  {outputFiles.length > 0 ? outputFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg group hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
                      <input
                        type="checkbox"
                        checked={selectedOutputFiles.has(idx)}
                        onChange={() => toggleFileSelection(idx)}
                        className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                      />
                      <span
                        className="flex-1 truncate text-blue-600 font-medium cursor-pointer hover:underline text-xs"
                        onClick={() => { if (window.pywebview?.api) window.pywebview.api.open_file(file.path); }}
                      >
                        {file.name}
                      </span>
                      <button
                        onClick={() => handleMoveToScreenshot(file.path, file.name, (file as any).urlCount)}
                        className="opacity-0 group-hover:opacity-100 px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-bold hover:bg-blue-700 transition-all"
                      >
                        移至下一步
                      </button>
                    </div>
                  )) : (
                    <div className="text-center py-4 text-slate-400 italic text-xs">
                      {uploadedFile ? '正在等待轉換...' : '暫無紀錄'}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Column 2: Auto Screenshot */}
        <div id="screenshot-card" className="bg-white/80 dark:bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-white/5 p-6 shadow-sm flex flex-col gap-6 hover:shadow-xl hover:shadow-blue-500/5 transition-all xl:col-span-3">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="size-10 rounded-xl bg-blue-600/10 text-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/10">
                  <span className="material-symbols-outlined">language</span>
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-200 tracking-tight">自動截圖</h3>
                  <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">網頁自動化任務</p>
                </div>
              </div>
              <button onClick={onOpenConfig} className="p-2 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-500 hover:text-blue-500 transition-all hover:bg-blue-500/10 active:scale-90">
                <span className="material-symbols-outlined text-sm">settings</span>
              </button>
            </div>

            <div className="flex flex-col gap-4 bg-slate-50/50 dark:bg-slate-800/30 p-4 rounded-xl border border-slate-100 dark:border-slate-800/50">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex flex-1 gap-2">
                  <button
                    onClick={handleStartScreenshot}
                    disabled={!config.inputFiles?.length || isStartingTask || taskStatus.status === 'running'}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white text-[10px] font-black uppercase tracking-widest hover:brightness-110 hover:shadow-lg hover:shadow-blue-500/30 transition-all flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-sm">{isStartingTask || taskStatus.status === 'running' ? 'sync' : 'play_arrow'}</span>
                    {taskStatus.status === 'running' ? '正在執行' : isStartingTask ? '啟動中...' : '立即開始'}
                  </button>
                </div>
                <div className="h-4 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>
                <div className="flex gap-2">
                  <button onClick={handleResetAll} className="px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 text-[10px] font-black uppercase tracking-wider flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">restart_alt</span>
                    清空
                  </button>
                  <button
                    onClick={handleStopScreenshot}
                    disabled={taskStatus.status !== 'running'}
                    className={`px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-wider ${taskStatus.status === 'running' ? 'bg-red-600/10 text-red-600 hover:bg-red-600 hover:text-white' : 'bg-slate-100 text-slate-300 dark:bg-slate-800'}`}
                  >
                    停止
                  </button>
                </div>
              </div>

              {/* Progress Bar Integrated In Card */}
              {taskStatus.status === 'running' && (
                <div className="mt-2 p-4 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl space-y-3 border border-blue-100/50 dark:border-blue-900/30 animate-in fade-in zoom-in duration-300">
                  <div className="flex justify-between items-end">
                    <div className="flex flex-col">
                      <p className="text-[9px] font-black text-blue-600 uppercase tracking-tighter">任務進度</p>
                      <p className="text-[11px] font-bold text-slate-600 dark:text-slate-300">
                        {taskStatus.current_file || '處理中'} ({taskStatus.processed}/{taskStatus.total})
                      </p>
                    </div>
                    <div className="flex flex-col items-end">
                      <p className="text-[9px] font-black text-indigo-500 uppercase tracking-tighter">預估剩餘</p>
                      <p className="text-xs font-mono font-bold text-slate-600 dark:text-indigo-300">
                        {(() => {
                          const remaining = taskStatus.total - taskStatus.processed;
                          if (remaining <= 0) return '即將完成';
                          const avgWait = (config.waitPerPage.min + config.waitPerPage.max) / 2;
                          const totalSeconds = remaining * (avgWait + config.screenshotDelay + 4.5);
                          const minutes = Math.floor(totalSeconds / 60);
                          return minutes > 0 ? `${minutes} 分鐘` : '少於 1 分鐘';
                        })()}
                      </p>
                    </div>
                  </div>
                  <div className="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.4)] transition-all duration-500 ease-out relative"
                      style={{ width: `${taskStatus.total > 0 ? (taskStatus.processed / taskStatus.total) * 100 : 0}%` }}
                    >
                      <div className="absolute inset-0 bg-white/20 animate-pulse" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">網址清單</p>
              {config.inputFiles?.length ? (
                <div className="space-y-2">
                  {config.inputFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 rounded-xl border border-blue-500/30 bg-blue-50/20 dark:bg-blue-500/5 group">
                      <span className="material-symbols-outlined text-lg text-blue-600">description</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{file.name}</p>
                        <button onClick={() => handleScreenshotRemoveFile(idx)} className="text-[9px] text-red-500 font-bold hover:underline">移除</button>
                      </div>
                    </div>
                  ))}
                  <div className="flex flex-col gap-2">
                    <button onClick={handleScreenshotFileSelect} className="w-full p-3 border border-dashed border-slate-200 rounded-xl text-[10px] font-black text-slate-400 hover:text-blue-600 flex items-center justify-center gap-2">
                      <span className="material-symbols-outlined text-[16px]">add_circle</span>新增網址檔案
                    </button>
                    <button onClick={handleScreenshotFolderSelect} className="w-full p-3 border border-dashed border-slate-200 rounded-xl text-[10px] font-black text-slate-400 hover:text-emerald-600 flex items-center justify-center gap-2">
                      <span className="material-symbols-outlined text-[16px]">folder_open</span>加入網址資料夾
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  <div onClick={handleScreenshotFileSelect} className="flex items-center gap-4 p-5 rounded-2xl border border-dashed border-slate-200 dark:border-white/10 cursor-pointer hover:bg-blue-500/5 hover:border-blue-500/50 transition-all group relative overflow-hidden">
                    <div className="size-10 rounded-xl bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform shrink-0">
                      <span className="material-symbols-outlined">add_circle</span>
                    </div>
                    <div>
                      <p className="text-sm font-black dark:text-slate-300">選擇網址檔案</p>
                      <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-0.5 uppercase tracking-widest">支援常見試算表與文字檔</p>
                    </div>
                  </div>
                  <div onClick={handleScreenshotFolderSelect} className="flex items-center gap-4 p-5 rounded-2xl border border-dashed border-slate-200 dark:border-white/10 cursor-pointer hover:bg-emerald-500/5 hover:border-emerald-500/50 transition-all group relative overflow-hidden">
                    <div className="size-10 rounded-xl bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform shrink-0">
                      <span className="material-symbols-outlined">folder_open</span>
                    </div>
                    <div>
                      <p className="text-sm font-black dark:text-slate-300">加入網址資料夾</p>
                      <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-0.5 uppercase tracking-widest">批量新增多個來源</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-1">輸出資料夾</p>
              {config.outputDir ? (
                <div className="flex items-center gap-3 p-3 bg-white/50 dark:bg-white/5 rounded-2xl border border-emerald-500/20 group backdrop-blur-sm">
                  <div className="size-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                    <span className="material-symbols-outlined text-lg">folder</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black truncate text-slate-700 dark:text-slate-200">{config.outputDirDisplay}</p>
                    <p className="text-[9px] text-slate-400 truncate font-mono opacity-80">{shortenPath(config.outputDir, 35)}</p>
                  </div>
                  <button onClick={handleScreenshotRemoveDir} className="p-1 text-slate-300 hover:text-red-500 transition-colors"><span className="material-symbols-outlined text-sm">close</span></button>
                </div>
              ) : (
                <div onClick={handleScreenshotDirSelect} className="flex flex-col gap-2 p-5 rounded-2xl border border-dashed border-slate-200 dark:border-white/10 cursor-pointer hover:border-blue-500/50 hover:bg-blue-500/5 transition-all group">
                  <div className="flex items-center gap-4">
                    <div className="size-10 rounded-xl bg-slate-100 dark:bg-white/5 flex items-center justify-center text-slate-400 group-hover:text-blue-500 transition-all shrink-0">
                      <span className="material-symbols-outlined">create_new_folder</span>
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-sm font-black text-slate-700 dark:text-slate-300">設定存檔路徑</p>
                      <p className="text-[10px] text-slate-400 font-mono break-all leading-tight opacity-70">
                        {defaultOutputDir ? shortenPath(defaultOutputDir, 40) : '（請先選擇網址檔案）'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-3 py-5 px-6 bg-slate-50/50 dark:bg-white/5 rounded-2xl border border-slate-100 dark:border-white/5">
            <div className="flex justify-between text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">
              <span>任務進度</span>
              <span className="text-blue-500">{screenshotStatus.processed} / {screenshotStatus.total}</span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-white/10 rounded-full h-2 overflow-hidden shadow-inner">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                style={{ width: `${screenshotStatus.total > 0 ? (screenshotStatus.processed / screenshotStatus.total) * 100 : 0}%` }}
              ></div>
            </div>
            <div className="text-center text-[10px] font-black uppercase tracking-widest text-slate-400">
              {screenshotStatus.status === 'running' ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="size-1.5 bg-blue-500 rounded-full animate-ping"></span>
                  執行中...
                </span>
              ) : (screenshotStatus.processed > 0 && screenshotStatus.processed === screenshotStatus.total ? '任務已全數完成' : '正等待工作排程')}
            </div>
          </div>

          <div className="space-y-4 border-t border-slate-100 dark:border-slate-800 pt-5">
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">最新輸出</span>
                {appState.latest_screenshot_results?.length > 0 && (
                  <button
                    onClick={() => { if (window.pywebview?.api) window.pywebview.api.open_folder(appState.latest_screenshot_folder || config.outputDir); }}
                    className="p-1 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded flex items-center justify-center text-blue-600 transition-colors"
                    title="開啟輸出資料夾"
                  >
                    <span className="material-symbols-outlined text-[16px]">folder_open</span>
                  </button>
                )}
              </div>
              <div className="space-y-2 overflow-y-auto custom-scrollbar max-h-[160px]">
                {appState.latest_screenshot_results?.length ? appState.latest_screenshot_results.map((res: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-white rounded-lg shadow-sm">
                    <span className="truncate text-[11px] font-medium text-slate-700 cursor-pointer hover:underline" onClick={() => { if (window.pywebview?.api) window.pywebview.api.open_file(res.path); }}>{res.name}</span>
                    <span className="text-[9px] text-slate-400 ml-2 shrink-0">文件</span>
                  </div>
                )) : <div className="text-center py-4 text-[10px] text-slate-400 italic">{screenshotStatus.status === 'running' ? '正在生成...' : '暫無執行輸出'}</div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
};

export default Dashboard;
