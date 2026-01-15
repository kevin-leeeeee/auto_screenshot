import React, { useState } from 'react';
import { AutomationConfig } from '../types';

interface ConfigurationModalProps {
  config: AutomationConfig;
  onClose: () => void;
  onSave: (config: AutomationConfig) => void;
}

const KeywordSection: React.FC<{
  title: string;
  keywords: string[];
  onRemove: (index: number) => void;
  onAdd: (val: string) => void;
  pauseEnabled?: boolean;
  onPauseToggle?: (enabled: boolean) => void;
}> = ({ title, keywords, onRemove, onAdd, pauseEnabled, onPauseToggle }) => {
  const [val, setVal] = useState('');
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-bold text-slate-700 dark:text-slate-300">{title}</label>
        {onPauseToggle && (
          <button
            onClick={() => onPauseToggle(!pauseEnabled)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md transition-all ${pauseEnabled
              ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
              : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-500'
              }`}
          >
            <span className="material-symbols-outlined text-[16px]">
              {pauseEnabled ? 'pause_circle' : 'play_circle'}
            </span>
            <span className="text-[10px] font-black uppercase tracking-wider">
              {pauseEnabled ? '偵測到時暫停' : '偵測到時繼續'}
            </span>
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg min-h-[46px]">
        {keywords.map((kw, i) => (
          <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded text-xs font-medium text-slate-600 dark:text-slate-300 shadow-sm">
            {kw}
            <button onClick={() => onRemove(i)} className="hover:text-red-500 transition-colors">
              <span className="material-symbols-outlined text-[14px]">close</span>
            </button>
          </span>
        ))}
        <input
          className="flex-1 bg-transparent border-none p-0 text-xs focus:ring-0 placeholder:text-slate-400 min-w-[80px] dark:text-white"
          placeholder="新增..."
          type="text"
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              onAdd(val);
              setVal('');
            }
          }}
        />
      </div>
    </div>
  );
};

const ConfigurationModal: React.FC<ConfigurationModalProps> = ({ config, onClose, onSave }) => {
  const [formData, setFormData] = useState<AutomationConfig>(config);
  const [newKeyword, setNewKeyword] = useState('');
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null);

  const addKeyword = () => {
    if (newKeyword.trim()) {
      if (!formData.keywords.includes(newKeyword.trim())) {
        setFormData({ ...formData, keywords: [...formData.keywords, newKeyword.trim()] });
      }
      setNewKeyword('');
    }
  };

  const onDragStart = (idx: number) => {
    setDraggedIdx(idx);
  };

  const onDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault();
    if (draggedIdx === null || draggedIdx === idx) return;

    const newKeywords = [...formData.keywords];
    const draggedItem = newKeywords[draggedIdx];
    newKeywords.splice(draggedIdx, 1);
    newKeywords.splice(idx, 0, draggedItem);

    setFormData({ ...formData, keywords: newKeywords });
    setDraggedIdx(idx);
  };

  const onDragEnd = () => {
    setDraggedIdx(null);
  };

  const removeKeyword = (index: number, field: keyof AutomationConfig = 'keywords') => {
    // @ts-ignore
    const nextList = [...formData[field]];
    nextList.splice(index, 1);
    setFormData({ ...formData, [field]: nextList });
  };

  const addKeywordToField = (field: keyof AutomationConfig, value: string) => {
    if (value.trim()) {
      // @ts-ignore
      setFormData({ ...formData, [field]: [...formData[field], value.trim()] });
    }
  };

  const getCategoryColor = (name: string) => {
    // 使用新的標籤名稱來尋找暫停狀態 (相容舊名)
    const key = name === '驗證碼' ? '拼圖與人機驗證' : (name === '不存在' ? '查無資料' : name);
    const isPaused = formData.categoryPause?.[key];
    if (isPaused) {
      return 'bg-amber-500 border-amber-600 text-white ring-2 ring-amber-500/20';
    }
    return 'bg-blue-600 border-blue-700 text-white';
  };

  const addCustomKeyword = (category: string, value: string) => {
    if (value.trim()) {
      const currentCustom = formData.customCategories || {};
      const currentList = currentCustom[category] || [];
      setFormData({
        ...formData,
        customCategories: {
          ...currentCustom,
          [category]: [...currentList, value.trim()]
        }
      });
    }
  };

  const removeCustomKeyword = (category: string, index: number) => {
    const currentCustom = formData.customCategories || {};
    const currentList = [...(currentCustom[category] || [])];
    currentList.splice(index, 1);
    setFormData({
      ...formData,
      customCategories: {
        ...currentCustom,
        [category]: currentList
      }
    });
  };

  const togglePause = (category: string, enabled: boolean) => {
    const currentPause = formData.categoryPause || {};
    setFormData({
      ...formData,
      categoryPause: {
        ...currentPause,
        [category]: enabled
      }
    });
  };

  const handleSave = () => {
    const fixedConfig = { ...formData };
    if (fixedConfig.waitPerPage.min > fixedConfig.waitPerPage.max) {
      const temp = fixedConfig.waitPerPage.min;
      fixedConfig.waitPerPage.min = fixedConfig.waitPerPage.max;
      fixedConfig.waitPerPage.max = temp;
    }
    fixedConfig.waitPerPage.min = Math.max(0, fixedConfig.waitPerPage.min);
    fixedConfig.waitPerPage.max = Math.max(1, fixedConfig.waitPerPage.max);
    fixedConfig.screenshotDelay = Math.max(0, fixedConfig.screenshotDelay);
    fixedConfig.cropTop = Math.max(0, fixedConfig.cropTop);
    fixedConfig.cropBottom = Math.max(0, fixedConfig.cropBottom);
    fixedConfig.scrollTimes = Math.max(1, Math.min(20, (fixedConfig.scrollTimes || 1)));
    fixedConfig.batchSize = Math.max(1, fixedConfig.batchSize);
    if (fixedConfig.batchRestRange.min > fixedConfig.batchRestRange.max) {
      const t = fixedConfig.batchRestRange.min;
      fixedConfig.batchRestRange.min = fixedConfig.batchRestRange.max;
      fixedConfig.batchRestRange.max = t;
    }
    onSave(fixedConfig);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 backdrop-blur-md p-4 text-slate-800 dark:text-slate-100">
      <div className="bg-white dark:bg-slate-900 w-full max-w-lg rounded-3xl shadow-2xl border border-slate-200 dark:border-white/5 overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">

        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 dark:border-white/5 flex items-center justify-between bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600/10 p-2 rounded-xl text-blue-600 shadow-lg shadow-blue-500/5">
              <span className="material-symbols-outlined text-xl">settings_input_component</span>
            </div>
            <div>
              <h2 className="text-xl font-black tracking-tight dark:text-white">進階執行設定</h2>
              <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-0.5">自定義系統自動化任務執行邏輯</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-red-500 transition-all p-1.5 hover:bg-red-500/10 rounded-xl">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Scrollable Content Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar max-h-[75vh]">

          {/* SECTION 1: 任務執行設定 */}
          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest pl-1">
              <span className="material-symbols-outlined text-sm">settings_slow_motion</span> 1. 任務執行設定
            </h3>

            <div className="grid grid-cols-2 gap-3">
              <div className="flex gap-2">
                <div
                  className="flex-1 flex items-center justify-between p-4 bg-slate-50/50 dark:bg-white/5 rounded-2xl border border-slate-200 dark:border-white/5 cursor-pointer hover:bg-white dark:hover:bg-white/10 transition-all shadow-sm"
                  onClick={() => setFormData({ ...formData, skipDone: !formData.skipDone })}
                >
                  <div className="flex flex-col">
                    <p className="text-sm font-black dark:text-slate-200">跳過已完成</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer pointer-events-none">
                    <input type="checkbox" className="sr-only peer" checked={formData.skipDone} readOnly />
                    <div className="w-10 h-5 bg-slate-200 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500 shadow-inner"></div>
                  </label>
                </div>

                <button
                  className="px-4 bg-red-500 text-white rounded-2xl text-[10px] font-black hover:bg-red-600 transition-all uppercase tracking-widest shadow-lg shadow-red-500/20 active:scale-95"
                  onClick={async () => {
                    if (confirm('確定要清除選取檔案的「已完成紀錄」嗎？')) {
                      // @ts-ignore
                      if (window.pywebview?.api) {
                        const targets = formData.inputFiles && formData.inputFiles.length > 0
                          ? formData.inputFiles.map(f => f.path || f)
                          : formData.inputFile ? [formData.inputFile] : [];

                        if (targets.length > 0) {
                          for (const path of targets) {
                            // @ts-ignore
                            await window.pywebview.api.clear_done_log(path);
                          }
                          alert('已完成清除任務');
                        } else {
                          alert('請先選擇輸入檔案');
                        }
                      }
                    }
                  }}
                >
                  清除紀錄
                </button>
              </div>

              <div
                className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                onClick={() => setFormData({ ...formData, autoWordExport: !formData.autoWordExport })}
              >
                <div className="flex flex-col">
                  <p className="text-sm font-bold">輸出 Word</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer pointer-events-none">
                  <input type="checkbox" className="sr-only peer" checked={formData.autoWordExport} readOnly />
                  <div className="w-9 h-5 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5 pl-1">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">timer</span> 頁面等待範圍 (秒)
                </label>
                <div className="flex gap-2 items-center">
                  <input
                    className="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg py-2.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                    type="number"
                    min="0"
                    placeholder="最小"
                    value={formData.waitPerPage.min}
                    onChange={(e) => setFormData({ ...formData, waitPerPage: { ...formData.waitPerPage, min: parseInt(e.target.value) || 0 } })}
                  />
                  <span className="text-slate-300 font-bold">~</span>
                  <input
                    className="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg py-2.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                    type="number"
                    min="1"
                    placeholder="最大"
                    value={formData.waitPerPage.max}
                    onChange={(e) => setFormData({ ...formData, waitPerPage: { ...formData.waitPerPage, max: parseInt(e.target.value) || 0 } })}
                  />
                </div>
              </div>
              <div className="space-y-1.5 pl-1">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">shutter_speed</span> 截圖倒數 (秒)
                </label>
                <input
                  className="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg py-2.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                  type="number"
                  min="0"
                  value={formData.screenshotDelay}
                  onChange={(e) => setFormData({ ...formData, screenshotDelay: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-slate-800 mx-1"></div>

          {/* SECTION 2: 截圖行為設定 */}
          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest pl-1">
              <span className="material-symbols-outlined text-sm">settings_motion_mode</span> 2. 截圖行為設定
            </h3>

            <div className="space-y-6">
              <div className="flex flex-col gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setFormData({ ...formData, scrollCapture: !formData.scrollCapture })}
                >
                  <div className="flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-orange-500/10 text-orange-600 flex items-center justify-center">
                      <span className="material-symbols-outlined text-lg">vertical_align_bottom</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold">啟用捲動截圖</p>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400">模擬 PageDown 以獲取隱藏區域</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer pointer-events-none">
                    <input type="checkbox" className="sr-only peer" checked={formData.scrollCapture} readOnly />
                    <div className="w-11 h-6 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
                  </label>
                </div>

                {formData.scrollCapture && (
                  <div className="flex flex-col gap-4 pt-3 border-t border-slate-200/50 dark:border-slate-700/50 animate-in fade-in slide-in-from-top-1 duration-200">
                    <div className="flex items-center justify-between">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-wider">PageDown 次數</label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min="1"
                          max="20"
                          className="w-16 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg py-1 px-2 text-xs font-bold outline-none ring-blue-500 focus:ring-1 text-center"
                          value={formData.scrollTimes}
                          onChange={(e) => setFormData({ ...formData, scrollTimes: parseInt(e.target.value) || 1 })}
                        />
                        <span className="text-[10px] text-slate-400 italic">次 (建議 1-4)</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex flex-col">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-wider">自動拼貼長圖</label>
                        <p className="text-[9px] text-slate-400">關閉時每頁間將加入空白分隔</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          className="sr-only peer"
                          checked={formData.scrollStitch}
                          onChange={() => setFormData({ ...formData, scrollStitch: !formData.scrollStitch })}
                        />
                        <div className="w-10 h-5 bg-slate-200 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"></div>
                      </label>
                    </div>
                  </div>
                )}
              </div>

              {/* Batch Rest Section */}
              <div className="flex flex-col gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setFormData({ ...formData, batchRestEnabled: !formData.batchRestEnabled })}
                >
                  <div className="flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
                      <span className="material-symbols-outlined text-lg">pace</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold">啟用批次休息</p>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400">在大批量任務中自動加入休眠間隔</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer pointer-events-none">
                    <input type="checkbox" className="sr-only peer" checked={formData.batchRestEnabled} readOnly />
                    <div className="w-11 h-6 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>

                {formData.batchRestEnabled && (
                  <div className="pt-3 border-t border-slate-200/50 dark:border-slate-700/50 space-y-4 animate-in fade-in slide-in-from-top-1 duration-200">
                    <div className="flex items-center justify-between">
                      <label className="text-[10px] font-black text-slate-400 uppercase">執行頻率</label>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium">每</span>
                        <input
                          type="number"
                          min="1"
                          className="w-16 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-md py-1 px-2 text-xs font-bold outline-none ring-blue-500 focus:ring-1 text-center"
                          value={formData.batchSize}
                          onChange={(e) => setFormData({ ...formData, batchSize: parseInt(e.target.value) || 1 })}
                        />
                        <span className="text-xs font-medium">頁後休息一次</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-[10px] font-black text-slate-400 uppercase">休息秒數</label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          className="w-16 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-md py-1 px-2 text-xs font-bold outline-none ring-blue-500 focus:ring-1 text-center"
                          value={formData.batchRestRange.min}
                          onChange={(e) => setFormData({ ...formData, batchRestRange: { ...formData.batchRestRange, min: parseInt(e.target.value) || 0 } })}
                        />
                        <span className="text-slate-300 font-bold">~</span>
                        <input
                          type="number"
                          className="w-16 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-md py-1 px-2 text-xs font-bold outline-none ring-blue-500 focus:ring-1 text-center"
                          value={formData.batchRestRange.max}
                          onChange={(e) => setFormData({ ...formData, batchRestRange: { ...formData.batchRestRange, max: parseInt(e.target.value) || 0 } })}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-4 p-4 bg-slate-50/50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex justify-between items-start gap-4">
                  {/* Left side: Controls */}
                  <div className="flex-1 space-y-6">
                    {/* Crop Toggle and Inputs */}
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <div className="size-8 rounded-lg bg-blue-500/10 text-blue-600 flex items-center justify-center">
                            <span className="material-symbols-outlined text-lg">content_cut</span>
                          </div>
                          <div>
                            <p className="text-sm font-bold">啟用邊緣裁切</p>
                            <p className="text-[10px] text-slate-500 dark:text-slate-400">移除網頁頂部/底部的干擾區域</p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={formData.cropEnabled}
                            onChange={(e) => setFormData({ ...formData, cropEnabled: e.target.checked })}
                          />
                          <div className="w-11 h-6 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>

                      {formData.cropEnabled && (
                        <div className="grid grid-cols-2 gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
                          <div className="space-y-1">
                            <span className="text-[10px] font-black text-slate-400 uppercase ml-1">頂部裁切</span>
                            <input
                              className="w-full bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg py-1.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                              type="number"
                              min="0"
                              value={formData.cropTop}
                              onChange={(e) => setFormData({ ...formData, cropTop: parseInt(e.target.value) || 0 })}
                            />
                          </div>
                          <div className="space-y-1">
                            <span className="text-[10px] font-black text-slate-400 uppercase ml-1">底部裁切</span>
                            <input
                              className="w-full bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg py-1.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                              type="number"
                              min="0"
                              value={formData.cropBottom}
                              onChange={(e) => setFormData({ ...formData, cropBottom: parseInt(e.target.value) || 0 })}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Range Mode Selection inside the same card */}
                    <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-4">
                      <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">截圖範圍模式</label>
                      <div className="relative group">
                        <select
                          style={{
                            appearance: 'none',
                            WebkitAppearance: 'none',
                            MozAppearance: 'none',
                            backgroundImage: 'none'
                          }}
                          className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-2.5 px-4 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none pr-10 cursor-pointer transition-all"
                          value={formData.range}
                          onChange={(e) => setFormData({ ...formData, range: e.target.value as any })}
                        >
                          <option value="viewport">僅限可視視窗</option>
                          <option value="fullscreen">整頁完整截圖</option>
                        </select>
                        <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-blue-600 transition-colors">
                          expand_more
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Right side: Mock Web Window Preview */}
                  <div className="flex flex-col items-center gap-2 shrink-0 pt-2">
                    <div className="relative w-24 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 shadow-sm overflow-hidden transition-all duration-300 flex flex-col"
                      style={{ height: formData.range === 'fullscreen' ? '140px' : '90px' }}>
                      {/* Browser Header */}
                      <div className="h-4 bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center px-1.5 gap-1">
                        <div className="size-1 rounded-full bg-red-400"></div>
                        <div className="size-1 rounded-full bg-amber-400"></div>
                        <div className="size-1 rounded-full bg-emerald-400"></div>
                        <div className="h-2 w-10 bg-white dark:bg-slate-900 rounded-[2px] ml-1"></div>
                      </div>

                      {/* Web Content Area */}
                      <div className="flex-1 relative flex flex-col items-center justify-center bg-slate-50/50 dark:bg-slate-800/10">
                        {/* Crop Masks */}
                        {formData.cropEnabled && (
                          <>
                            <div className="absolute top-0 left-0 right-0 bg-red-500/20 border-b border-red-500/50 z-10" style={{ height: `${Math.min((formData.cropTop || 0) / 4, 45)}%` }}></div>
                            <div className="absolute bottom-0 left-0 right-0 bg-red-500/20 border-t border-red-500/50 z-10" style={{ height: `${Math.min((formData.cropBottom || 0) / 4, 45)}%` }}></div>
                          </>
                        )}

                        {/* Simulated Content Lines */}
                        <div className="space-y-1 opacity-20 w-16">
                          <div className="h-1 bg-slate-400 rounded-full w-full"></div>
                          <div className="h-1 bg-slate-400 rounded-full w-3/4"></div>
                          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded flex items-center justify-center">
                            <span className="text-[6px] font-black tracking-tighter scale-[0.7]">圖片</span>
                          </div>
                          <div className="h-1 bg-slate-400 rounded-full w-full"></div>
                          {formData.range === 'fullscreen' && (
                            <>
                              <div className="h-1 bg-slate-400 rounded-full w-1/2"></div>
                              <div className="h-1 bg-slate-400 rounded-full w-full"></div>
                              <span className="material-symbols-outlined text-[10px] text-slate-400 animate-bounce block text-center mt-1">expand_more</span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Mock Windows Taskbar */}
                      {formData.range === 'fullscreen' && (
                        <div className="h-2 bg-slate-800 dark:bg-black border-t border-white/5 flex items-center px-1 gap-[2px] shrink-0">
                          <div className="size-[4px] rounded-[1px] bg-blue-400"></div>
                          <div className="h-[2px] w-2 bg-white/20 rounded-full ml-auto"></div>
                        </div>
                      )}
                    </div>
                    <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest">預覽</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-slate-800 mx-1"></div>

          {/* SECTION 3: 文字檢查與分類 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between pr-1">
              <h3 className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest pl-1">
                <span className="material-symbols-outlined text-sm">verified</span> 3. 文字檢查與分類
              </h3>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={formData.textCheckEnabled}
                  onChange={(e) => setFormData({ ...formData, textCheckEnabled: e.target.checked })}
                />
                <div className="w-11 h-6 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {!formData.textCheckEnabled ? (
              <div className="p-8 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-dashed border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center gap-3 grayscale opacity-60">
                <span className="material-symbols-outlined text-4xl text-slate-400">content_paste_search</span>
                <p className="text-xs font-bold text-slate-400">已關閉文字偵測功能</p>
              </div>
            ) : (
              <div className="space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
                <div className="space-y-4 pt-2">
                  <div className="space-y-2 pl-1">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">啟用偵測功能 (類別開關)</label>
                    <div className="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl min-h-[58px] transition-all">
                      {formData.keywords.map((kw, i) => (
                        <div
                          key={i}
                          draggable
                          onDragStart={() => onDragStart(i)}
                          onDragOver={(e) => onDragOver(e, i)}
                          onDragEnd={onDragEnd}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-lg text-xs font-bold shadow-sm transition-all cursor-move select-none animate-in zoom-in-95
                            ${draggedIdx === i ? 'opacity-30 scale-95 border-dashed bg-slate-100 border-slate-300 text-slate-400' : getCategoryColor(kw)}
                          `}
                          title="拖曳以調整優先順序"
                        >
                          <span className="material-symbols-outlined text-[14px] opacity-70">drag_indicator</span>
                          <span className="flex items-center gap-1">
                            <span className="opacity-60 text-[10px]">{i + 1}.</span>
                            {kw}
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeKeyword(i);
                            }}
                            className="hover:bg-white/20 p-0.5 rounded-full transition-colors ml-0.5"
                          >
                            <span className="material-symbols-outlined text-[14px]">close</span>
                          </button>
                        </div>
                      ))}

                      <div className="relative group flex items-center">
                        <input
                          className="w-24 bg-transparent border-none p-2 text-xs font-bold focus:ring-0 placeholder:text-slate-400 dark:text-white"
                          placeholder="輸入類別..."
                          type="text"
                          value={newKeyword}
                          onChange={(e) => setNewKeyword(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && addKeyword()}
                        />
                        <div className="absolute left-0 top-full mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-100 dark:border-slate-700 p-2 hidden group-focus-within:block z-20">
                          <p className="text-[10px] font-bold text-slate-400 mb-2 px-1">建議啟用類別:</p>
                          <div className="flex flex-wrap gap-1">
                            {['拼圖與人機驗證', '查無資料', 'BSMI', '登入'].filter(k => !formData.keywords.includes(k)).map(tag => (
                              <button
                                key={tag}
                                onClick={() => {
                                  if (!formData.keywords.includes(tag)) {
                                    // @ts-ignore
                                    setFormData({ ...formData, keywords: [...formData.keywords, tag] });
                                  }
                                }}
                                className="px-2 py-1 bg-slate-100 dark:bg-slate-700 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-xs rounded text-slate-600 dark:text-slate-300 transition-colors"
                              >
                                + {tag}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-6 pt-2">
                    {formData.keywords.map((kw) => {
                      if (kw === '拼圖與人機驗證' || kw === '驗證碼') {
                        return (
                          <div key={kw} className="animate-in fade-in slide-in-from-top-2 duration-300">
                            <KeywordSection
                              title="拼圖與人機驗證"
                              keywords={formData.captchaKeywords}
                              onRemove={(i) => removeKeyword(i, 'captchaKeywords')}
                              onAdd={(v) => addKeywordToField('captchaKeywords', v)}
                              pauseEnabled={formData.categoryPause?.['拼圖與人機驗證']}
                              onPauseToggle={(v) => togglePause('拼圖與人機驗證', v)}
                            />
                          </div>
                        );
                      }
                      if (kw === '登入') {
                        return (
                          <div key={kw} className="animate-in fade-in slide-in-from-top-2 duration-300">
                            <KeywordSection
                              title="登入頁偵測"
                              keywords={formData.loginKeywords}
                              onRemove={(i) => removeKeyword(i, 'loginKeywords')}
                              onAdd={(v) => addKeywordToField('loginKeywords', v)}
                              pauseEnabled={formData.categoryPause?.['登入']}
                              onPauseToggle={(v) => togglePause('登入', v)}
                            />
                          </div>
                        );
                      }
                      if (kw === '查無資料' || kw === '不存在') {
                        return (
                          <div key={kw} className="animate-in fade-in slide-in-from-top-2 duration-300">
                            <KeywordSection
                              title="查無資料偵測"
                              keywords={formData.notFoundKeywords}
                              onRemove={(i) => removeKeyword(i, 'notFoundKeywords')}
                              onAdd={(v) => addKeywordToField('notFoundKeywords', v)}
                              pauseEnabled={formData.categoryPause?.['查無資料']}
                              onPauseToggle={(v) => togglePause('查無資料', v)}
                            />
                          </div>
                        );
                      }
                      if (kw === 'BSMI') {
                        return (
                          <div key={kw} className="animate-in fade-in slide-in-from-top-2 duration-300">
                            <KeywordSection
                              title="BSMI 證書偵測"
                              keywords={formData.bsmiKeywords}
                              onRemove={(i) => removeKeyword(i, 'bsmiKeywords')}
                              onAdd={(v) => addKeywordToField('bsmiKeywords', v)}
                              pauseEnabled={formData.categoryPause?.['BSMI']}
                              onPauseToggle={(v) => togglePause('BSMI', v)}
                            />
                          </div>
                        );
                      }
                      return (
                        <div key={kw} className="animate-in fade-in slide-in-from-top-2 duration-300">
                          <KeywordSection
                            title={`自訂類別: ${kw}`}
                            keywords={formData.customCategories?.[kw] || []}
                            onRemove={(idx) => removeCustomKeyword(kw, idx)}
                            onAdd={(v) => addCustomKeyword(kw, v)}
                            pauseEnabled={formData.categoryPause?.[kw]}
                            onPauseToggle={(v) => togglePause(kw, v)}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-slate-50/50 dark:bg-white/5 border-t border-slate-100 dark:border-white/5 flex gap-4 shrink-0 backdrop-blur-sm">
          <button onClick={onClose} className="flex-1 py-3.5 px-4 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-400 font-black rounded-2xl text-xs uppercase tracking-widest hover:bg-slate-50 dark:hover:bg-white/10 transition-all active:scale-95 shadow-sm">
            取消變更
          </button>
          <button
            onClick={handleSave}
            className="flex-[2] py-3.5 px-4 bg-gradient-to-br from-blue-600 to-indigo-700 text-white font-black rounded-2xl text-xs uppercase tracking-widest hover:brightness-110 shadow-xl shadow-blue-500/25 transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
          >
            <span className="material-symbols-outlined text-lg">save</span>
            確認並儲存設定
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigurationModal;
