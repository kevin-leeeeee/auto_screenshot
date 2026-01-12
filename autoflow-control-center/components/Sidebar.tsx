
import React from 'react';
import { ViewType } from '../types';

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  systemStatus?: 'idle' | 'running';
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange, systemStatus = 'idle' }) => {
  const navItems = [
    { id: 'dashboard' as ViewType, label: '儀表板', icon: 'dashboard' },
    { id: 'logs' as ViewType, label: '執行日誌', icon: 'list_alt' },
    { id: 'settings' as ViewType, label: '系統設定', icon: 'settings' },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between p-6 h-full z-20 transition-colors duration-300">
      <div className="flex flex-col gap-8">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <span className="material-symbols-outlined">rocket_launch</span>
          </div>
          <div>
            <h1 className="text-lg font-bold leading-none dark:text-white">AutoFlow</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">v2.0.0</p>
          </div>
        </div>

        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${currentView === item.id
                ? 'bg-blue-600/10 text-blue-600 font-bold dark:bg-blue-600/20'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="flex flex-col gap-4">
        <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-semibold uppercase text-slate-400 mb-2">系統狀態</p>
          <div className="flex items-center gap-2">
            <div className={`size-2 rounded-full ${systemStatus === 'running' ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`}></div>
            <span className="text-xs font-medium dark:text-slate-300">
              {systemStatus === 'running' ? '自動截圖運行中' : '系統閒置中'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
