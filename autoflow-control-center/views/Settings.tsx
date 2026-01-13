
import React from 'react';
import { DisplaySettings } from '../types';

interface SettingsProps {
  displaySettings: DisplaySettings;
  setDisplaySettings: (settings: DisplaySettings) => void;
}

const Settings: React.FC<SettingsProps> = ({ displaySettings, setDisplaySettings }) => {
  const fontSizeLabels = ['小 (S)', '中 (M)', '大 (L)', '特大 (XL)', '超大 (2XL)', '巨大 (3XL)', '無障礙超大 (MAX)'];

  const handleThemeChange = (theme: 'light' | 'dark') => {
    setDisplaySettings({ ...displaySettings, theme });
  };

  const handleFontSizeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDisplaySettings({ ...displaySettings, fontSize: parseInt(e.target.value) });
  };

  return (
    <div
      style={{ padding: '32px', gap: '24px' }}
      className="max-w-[1200px] mx-auto flex flex-col min-h-full"
    >
      <div className="flex-shrink-0" style={{ marginBottom: '24px' }}>
        <h2 className="text-3xl font-black tracking-tight mb-1 dark:text-white">系統設定</h2>
        <p className="text-slate-500 dark:text-slate-400">管理您的應用程式偏好與視覺呈現效果。</p>
      </div>

      <div className="flex-1 flex flex-col md:flex-row min-h-0" style={{ gap: '32px' }}>
        {/* 左側導航 */}
        <div style={{ width: '280px', gap: '8px' }} className="flex flex-col shrink-0">
          <button
            style={{ padding: '16px' }}
            className="flex items-center gap-4 bg-white dark:bg-slate-900 border-2 border-blue-600 rounded-xl text-left shadow-sm transition-all group"
          >
            <div className="size-10 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined">visibility</span>
            </div>
            <div>
              <p className="text-sm font-bold dark:text-white">顯示設定</p>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-tight">外觀與字體大小</p>
            </div>
          </button>
        </div>

        {/* 右側內容區塊 */}
        <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col transition-colors duration-300">
          <div style={{ padding: '16px 32px' }} className="border-b border-slate-100 dark:border-slate-800 flex-shrink-0">
            <h3 className="text-xl font-black mb-1 dark:text-white">個人化顯示</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">調整字體大小以符合您的閱讀習慣，我們特別為長輩提供了特大尺寸選項。</p>
          </div>

          <div
            className="flex-1 flex flex-col"
            style={{ padding: '24px 32px', gap: '32px' }}
          >
            {/* 主題選擇區 */}
            <div style={{ gap: '16px' }} className="flex flex-col">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 block">主題模式</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  onClick={() => handleThemeChange('light')}
                  style={{ padding: '16px' }}
                  className={`border-2 rounded-xl bg-white dark:bg-slate-800 text-left relative transition-all ${displaySettings.theme === 'light' ? 'border-blue-600 ring-4 ring-blue-600/5 shadow-md' : 'border-slate-200 dark:border-slate-700'
                    }`}
                >
                  <div className={`flex items-center gap-3 mb-2 ${displaySettings.theme === 'light' ? 'text-blue-600' : 'text-slate-500'}`}>
                    <span className="material-symbols-outlined">light_mode</span>
                    <span className="text-sm font-bold">淺色模式</span>
                  </div>
                  {displaySettings.theme === 'light' && (
                    <div className="absolute top-2 right-2 text-blue-600">
                      <span className="material-symbols-outlined">check_circle</span>
                    </div>
                  )}
                </button>
                <button
                  onClick={() => handleThemeChange('dark')}
                  style={{ padding: '16px' }}
                  className={`border-2 rounded-xl bg-slate-900 text-left relative transition-all ${displaySettings.theme === 'dark' ? 'border-blue-600 ring-4 ring-blue-600/5 shadow-md' : 'border-slate-800'
                    }`}
                >
                  <div className={`flex items-center gap-3 mb-2 ${displaySettings.theme === 'dark' ? 'text-blue-400' : 'text-slate-500'}`}>
                    <span className="material-symbols-outlined">dark_mode</span>
                    <span className="text-sm font-bold">深色模式</span>
                  </div>
                  {displaySettings.theme === 'dark' && (
                    <div className="absolute top-2 right-2 text-blue-400">
                      <span className="material-symbols-outlined">check_circle</span>
                    </div>
                  )}
                </button>
              </div>
            </div>

            {/* 字體選擇區 (Dropdown) */}
            <div style={{ gap: '20px' }} className="flex flex-col">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-bold text-slate-700 dark:text-slate-300">系統字體大小</label>
                <div className="relative">
                  <select
                    style={{
                      appearance: 'none',
                      WebkitAppearance: 'none',
                      MozAppearance: 'none',
                      backgroundImage: 'none'
                    }}
                    className="w-full appearance-none bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                    value={displaySettings.fontSize}
                    onChange={(e) => setDisplaySettings({ ...displaySettings, fontSize: parseInt(e.target.value) })}
                  >
                    {fontSizeLabels.map((label, index) => (
                      <option key={index} value={index + 1}>
                        {label}
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                    <span className="material-symbols-outlined text-[20px]">expand_more</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 預覽區域 */}
            <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
              <div
                style={{ padding: '24px', minHeight: '140px' }}
                className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl space-y-4"
              >
                <h4 className="font-black text-slate-800 dark:text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-blue-600">visibility</span>
                  介面預覽
                </h4>
                <p className="text-slate-500 dark:text-slate-400 leading-relaxed">
                  調整字體大小後，系統將自動套用到所有的按鈕、選單與文字內容。
                  選擇適合您的設定，讓操作體驗更加舒適流暢。
                </p>
                <div className="flex gap-2">
                  <div className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm font-bold shadow-md">按鈕範例</div>
                  <div className="px-3 py-1 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-sm font-bold rounded-lg shadow-sm dark:text-slate-200">選單預覽</div>
                </div>
              </div>
            </div>
          </div>

          {/* 底部按鈕區 */}
          <div
            style={{ padding: '16px 32px' }}
            className="bg-slate-50 dark:bg-slate-800/80 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row justify-end gap-3 flex-shrink-0"
          >
            <button
              onClick={() => setDisplaySettings({ theme: 'light', fontSize: 2 })}
              className="px-6 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all shadow-sm active:scale-95"
            >
              重置
            </button>
            <button className="px-10 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-black shadow-xl shadow-blue-500/20 hover:bg-blue-700 transition-all active:scale-[0.98]">
              儲存變更
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
