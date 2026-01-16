
import React from 'react';
import { ViewType } from '../types';

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  systemStatus?: 'idle' | 'running';
  version?: string;
  onCheckUpdate?: () => void;
  hasUpdate?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onViewChange,
  systemStatus = 'idle',
  version = 'v3.1.0',
  onCheckUpdate,
  hasUpdate = false
}) => {
  const navItems = [
    { id: 'dashboard' as ViewType, label: '儀表板', icon: 'dashboard' },
    { id: 'logs' as ViewType, label: '執行日誌', icon: 'list_alt' },
    { id: 'settings' as ViewType, label: '系統設定', icon: 'settings' },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border-r border-slate-200 dark:border-white/5 flex flex-col justify-between p-6 h-full z-20 transition-all duration-300">
      <div className="flex flex-col gap-8">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20">
            <span className="material-symbols-outlined">rocket_launch</span>
          </div>
          <div>
            <h1 className="text-lg font-black leading-none dark:text-white tracking-tight">AutoFlow</h1>
            <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-1 uppercase tracking-widest">{version}</p>
          </div>
        </div>

        <nav className="flex flex-col gap-1.5">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentView === item.id
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25 font-bold'
                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5'
                }`}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="text-sm font-bold">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="flex flex-col gap-4">
        {/* Check Update Button */}
        {onCheckUpdate && (
          <button
            onClick={onCheckUpdate}
            className="relative flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 border border-slate-200 dark:border-white/5"
          >
            <span className="material-symbols-outlined text-[20px]">system_update</span>
            <span className="text-xs font-bold">檢查更新</span>
            {hasUpdate && (
              <span className="absolute top-1 right-1 size-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.5)]"></span>
            )}
          </button>
        )}

        {/* System Status */}
        <div className="bg-slate-50 dark:bg-slate-900/60 p-4 rounded-2xl border border-slate-100 dark:border-white/5">
          <p className="text-[10px] font-black uppercase text-slate-400 mb-3 tracking-widest">系統狀態</p>
          <div className="flex items-center gap-2">
            <div className={`size-2 rounded-full ${systemStatus === 'running' ? 'bg-amber-500 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'}`}></div>
            <span className="text-[11px] font-bold dark:text-slate-400">
              {systemStatus === 'running' ? '自動截圖運行中' : '系統閒置中'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
