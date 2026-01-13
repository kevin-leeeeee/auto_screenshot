
import React, { useState, useRef, useEffect } from 'react';
import { ViewType } from '../types';

interface HeaderProps {
  onViewChange?: (view: ViewType) => void;
  onShowLogs?: (id: string) => void;
  onToggleHelp?: () => void;
  history?: any[];
}

const Header: React.FC<HeaderProps> = ({ onViewChange, onShowLogs, onToggleHelp, history = [] }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const notificationRef = useRef<HTMLDivElement>(null);
  const helpRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (helpRef.current && !helpRef.current.contains(event.target as Node)) {
        setShowHelp(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Convert history to notifications
  const notifications = history.slice().reverse().slice(0, 10).map((h, idx) => ({
    id: h.id || `hist-${idx}`,
    title: h.status === 'Completed' ? '任務成功' : (h.status === 'Error' ? '任務失敗' : '執行中'),
    message: `${h.name} - ${h.duration || ''} ${h.message ? `(${h.message})` : ''}`,
    time: h.time,
    icon: h.status === 'Completed' ? 'check_circle' : (h.status === 'Error' ? 'error' : 'schedule'),
    color: h.status === 'Completed' ? 'text-emerald-500' : (h.status === 'Error' ? 'text-red-500' : 'text-blue-500')
  }));

  const handleNotificationClick = (id: string) => {
    setShowNotifications(false);
    if (onShowLogs) onShowLogs(id);
  };

  const handleViewAllHistory = () => {
    setShowNotifications(false);
    if (onViewChange) onViewChange('logs');
  };

  return (
    <header className="h-16 flex items-center justify-between px-8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 z-50 shrink-0 transition-colors duration-300 relative">
      <div className="flex items-center gap-4 flex-1">
        {/* Search removed as requested */}
      </div>

      <div className="flex items-center gap-2">
        {/* Notifications */}
        <div className="relative" ref={notificationRef}>
          <button
            onClick={() => { setShowNotifications(!showNotifications); setShowHelp(false); }}
            className={`p-2 rounded-lg transition-all relative ${showNotifications ? 'bg-blue-600/10 text-blue-600' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
          >
            <span className="material-symbols-outlined">notifications</span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-[60]">
              <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
                <h4 className="font-bold text-sm dark:text-white">通知中心</h4>
                <button className="text-[10px] font-bold text-blue-600 uppercase tracking-wider hover:underline">全部標為已讀</button>
              </div>
              <div className="max-h-96 overflow-y-auto no-scrollbar">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => handleNotificationClick(n.id)}
                    className="p-4 border-b border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors"
                  >
                    <div className="flex gap-3">
                      <span className={`material-symbols-outlined text-xl ${n.color}`}>{n.icon}</span>
                      <div className="flex-1">
                        <p className="text-xs font-bold dark:text-white mb-0.5">{n.title}</p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-snug">{n.message}</p>
                        <p className="text-[10px] text-slate-400 mt-1">{n.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 text-center">
                <button
                  onClick={handleViewAllHistory}
                  className="text-[11px] font-bold text-slate-500 dark:text-slate-400 hover:text-blue-600 transition-colors w-full py-1"
                >
                  查看歷史通知 (前往執行日誌)
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Help */}
        <div className="relative" ref={helpRef}>
          <button
            onClick={() => {
              if (onToggleHelp) onToggleHelp();
              setShowNotifications(false);
            }}
            className="p-2 rounded-lg transition-all text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <span className="material-symbols-outlined">help_outline</span>
          </button>

        </div>
      </div>
    </header>
  );
};

export default Header;
