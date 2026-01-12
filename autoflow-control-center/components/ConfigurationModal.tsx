
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
}> = ({ title, keywords, onRemove, onAdd }) => {
  const [val, setVal] = useState('');
  return (
    <div className="space-y-2">
      <label className="text-sm font-bold text-slate-700 dark:text-slate-300">{title}</label>
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

  const addKeyword = () => {
    if (newKeyword.trim()) {
      setFormData({ ...formData, keywords: [...formData.keywords, newKeyword.trim()] });
      setNewKeyword('');
    }
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

  const handleSave = () => {
    // Fool-proof: Validate and fix values
    const fixedConfig = { ...formData };

    // 1. Ensure min <= max for wait range
    if (fixedConfig.waitPerPage.min > fixedConfig.waitPerPage.max) {
      const temp = fixedConfig.waitPerPage.min;
      fixedConfig.waitPerPage.min = fixedConfig.waitPerPage.max;
      fixedConfig.waitPerPage.max = temp;
    }

    // 2. Ensure non-negative numbers
    fixedConfig.waitPerPage.min = Math.max(0, fixedConfig.waitPerPage.min);
    fixedConfig.waitPerPage.max = Math.max(1, fixedConfig.waitPerPage.max);
    fixedConfig.screenshotDelay = Math.max(0, fixedConfig.screenshotDelay);
    fixedConfig.cropTop = Math.max(0, fixedConfig.cropTop);
    fixedConfig.cropBottom = Math.max(0, fixedConfig.cropBottom);
    fixedConfig.scrollTimes = Math.max(1, Math.min(20, (fixedConfig.scrollTimes || 1)));

    // Batch rest fixes
    fixedConfig.batchSize = Math.max(1, fixedConfig.batchSize);
    if (fixedConfig.batchRestRange.min > fixedConfig.batchRestRange.max) {
      const t = fixedConfig.batchRestRange.min;
      fixedConfig.batchRestRange.min = fixedConfig.batchRestRange.max;
      fixedConfig.batchRestRange.max = t;
    }

    onSave(fixedConfig);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 text-slate-800 dark:text-slate-100">
      <div className="bg-white dark:bg-slate-900 w-full max-w-lg rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">

        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900 sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600/10 p-2 rounded-lg text-blue-600">
              <span className="material-symbols-outlined text-xl">settings_input_component</span>
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight">截圖進階設定</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">自定義「自動截圖任務」的執行邏輯</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors p-1">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Scrollable Content Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar max-h-[75vh]">

          {/* SECTION 1: 任務執行設定 */}
          <div className="space-y-4">
            <h3 className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest pl-1">
              <span className="material-symbols-outlined text-sm">settings_slow_motion</span> PART 1. 任務執行設定
            </h3>

            <div className="grid grid-cols-2 gap-3">
              <div className="flex gap-2">
                <div
                  className="flex-1 flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  onClick={() => setFormData({ ...formData, skipDone: !formData.skipDone })}
                >
                  <div className="flex flex-col">
                    <p className="text-sm font-bold">跳過已完成</p>
                    <p className="text-[9px] text-slate-400 uppercase font-black tracking-tighter">Skip Done</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer pointer-events-none">
                    <input type="checkbox" className="sr-only peer" checked={formData.skipDone} readOnly />
                    <div className="w-9 h-5 bg-slate-300 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                </div>

                <button
                  className="px-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-xl text-[10px] font-black hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors uppercase"
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
                  <p className="text-[9px] text-slate-400 uppercase font-black tracking-tighter">Word Docx</p>
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
                    placeholder="Min"
                    value={formData.waitPerPage.min}
                    onChange={(e) => setFormData({ ...formData, waitPerPage: { ...formData.waitPerPage, min: parseInt(e.target.value) || 0 } })}
                  />
                  <span className="text-slate-300 font-bold">~</span>
                  <input
                    className="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg py-2.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                    type="number"
                    min="1"
                    placeholder="Max"
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
              <span className="material-symbols-outlined text-sm">screenshot</span> PART 2. 截圖行為設定
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
                  <div className="flex items-center gap-3 pt-2 border-t border-slate-200/50 dark:border-slate-700/50 animate-in fade-in slide-in-from-top-1 duration-200">
                    <label className="text-[10px] font-black text-slate-400 uppercase">PageDown 次數</label>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      className="w-20 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-md py-1 px-2 text-xs font-bold outline-none ring-blue-500 focus:ring-1"
                      value={formData.scrollTimes}
                      onChange={(e) => setFormData({ ...formData, scrollTimes: parseInt(e.target.value) || 1 })}
                    />
                    <p className="text-[10px] text-slate-400 italic">多次捲動可用於深度較大的網頁</p>
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

              <div className="space-y-3 p-4 bg-slate-50/50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-700">
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
                  <div className="pt-3 border-t border-slate-200/50 dark:border-slate-700/50 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex gap-4">
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-black text-slate-400 w-10 uppercase">頂部</span>
                          <input
                            className="flex-1 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg py-1.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                            type="number"
                            min="0"
                            value={formData.cropTop}
                            onChange={(e) => setFormData({ ...formData, cropTop: parseInt(e.target.value) || 0 })}
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-black text-slate-400 w-10 uppercase">底部</span>
                          <input
                            className="flex-1 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg py-1.5 px-3 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none"
                            type="number"
                            min="0"
                            value={formData.cropBottom}
                            onChange={(e) => setFormData({ ...formData, cropBottom: parseInt(e.target.value) || 0 })}
                          />
                        </div>
                      </div>
                      <div className="w-20 h-20 bg-slate-100 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 relative overflow-hidden flex items-center justify-center shrink-0">
                        <div className="absolute top-0 left-0 right-0 bg-red-500/20 border-b border-red-500/50 z-10" style={{ height: `${Math.min((formData.cropTop || 0) / 5, 45)}%` }}></div>
                        <div className="absolute bottom-0 left-0 right-0 bg-red-500/20 border-t border-red-500/50 z-10" style={{ height: `${Math.min((formData.cropBottom || 0) / 5, 45)}%` }}></div>
                        <span className="text-[8px] text-slate-400 font-black tracking-widest z-0">CONTENT</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2 pl-1">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">截圖範圍模式</label>
                <div className="relative">
                  <select
                    style={{ appearance: 'none', WebkitAppearance: 'none' }}
                    className="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 text-sm font-bold focus:ring-2 focus:ring-blue-600 outline-none pr-10"
                    value={formData.range}
                    onChange={(e) => setFormData({ ...formData, range: e.target.value as any })}
                  >
                    <option value="viewport">僅限可視視窗 (Viewport)</option>
                    <option value="fullscreen">整頁完整截圖 (Full Page)</option>
                  </select>
                  <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 select-none">unfold_more</span>
                </div>
              </div>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-slate-800 mx-1"></div>

          {/* SECTION 3: 文字檢查與分類 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between pr-1">
              <h3 className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest pl-1">
                <span className="material-symbols-outlined text-sm">verified</span> PART 3. 文字檢查與分類
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
                    <div className="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl min-h-[46px]">
                      {formData.keywords.map((kw, i) => (
                        <span key={i} className={`inline-flex items-center gap-1.5 px-2.5 py-1 border rounded-lg text-xs font-bold shadow-sm transition-all cursor-default select-none
                          ${['驗證碼', '不存在', 'BSMI', '登入'].includes(kw)
                            ? 'bg-blue-600 border-blue-600 text-white'
                            : 'bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-200'}`}
                        >
                          {kw}
                          <button onClick={() => removeKeyword(i)} className={`${['驗證碼', '不存在', 'BSMI', '登入'].includes(kw) ? 'text-blue-200 hover:text-white' : 'text-slate-400 hover:text-red-500'} transition-colors`}>
                            <span className="material-symbols-outlined text-[14px]">close</span>
                          </button>
                        </span>
                      ))}
                      <div className="relative group">
                        <input
                          className="w-24 bg-transparent border-none p-0 text-xs font-bold focus:ring-0 placeholder:text-slate-400 dark:text-white"
                          placeholder="輸入類別..."
                          type="text"
                          value={newKeyword}
                          onChange={(e) => setNewKeyword(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && addKeyword()}
                        />
                        {/* Hints */}
                        <div className="absolute left-0 top-full mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-100 dark:border-slate-700 p-2 hidden group-focus-within:block z-20">
                          <p className="text-[10px] font-bold text-slate-400 mb-2 px-1">建議啟用類別:</p>
                          <div className="flex flex-wrap gap-1">
                            {['驗證碼', '不存在', 'BSMI', '登入'].filter(k => !formData.keywords.includes(k)).map(tag => (
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
                    {formData.keywords.includes('驗證碼') && (
                      <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <KeywordSection
                          title="驗證碼攔截 (Captcha)"
                          keywords={formData.captchaKeywords}
                          onRemove={(i) => removeKeyword(i, 'captchaKeywords')}
                          onAdd={(v) => addKeywordToField('captchaKeywords', v)}
                        />
                      </div>
                    )}

                    {formData.keywords.includes('登入') && (
                      <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <KeywordSection
                          title="登入頁偵測 (Login)"
                          keywords={formData.loginKeywords}
                          onRemove={(i) => removeKeyword(i, 'loginKeywords')}
                          onAdd={(v) => addKeywordToField('loginKeywords', v)}
                        />
                      </div>
                    )}

                    {formData.keywords.includes('不存在') && (
                      <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <KeywordSection
                          title="查無資料偵測 (Not Found)"
                          keywords={formData.notFoundKeywords}
                          onRemove={(i) => removeKeyword(i, 'notFoundKeywords')}
                          onAdd={(v) => addKeywordToField('notFoundKeywords', v)}
                        />
                      </div>
                    )}

                    {formData.keywords.includes('BSMI') && (
                      <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <KeywordSection
                          title="BSMI 證書偵測"
                          keywords={formData.bsmiKeywords}
                          onRemove={(i) => removeKeyword(i, 'bsmiKeywords')}
                          onAdd={(v) => addKeywordToField('bsmiKeywords', v)}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-slate-50 dark:bg-slate-800/80 border-t border-slate-100 dark:border-slate-800 flex gap-4 shrink-0">
          <button onClick={onClose} className="flex-1 py-3 px-4 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-200 font-black rounded-xl text-sm hover:bg-slate-100 dark:hover:bg-slate-600 transition-all active:scale-95">
            取消變更
          </button>
          <button
            onClick={handleSave}
            className="flex-[2] py-3 px-4 bg-blue-600 text-white font-black rounded-xl text-sm hover:bg-blue-700 shadow-xl shadow-blue-500/20 transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
          >
            <span className="material-symbols-outlined text-lg">save</span>
            確認變更並儲存
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigurationModal;
