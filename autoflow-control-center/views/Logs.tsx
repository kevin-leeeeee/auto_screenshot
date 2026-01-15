
import React, { useState } from 'react';

interface LogsProps {
  history?: any[];
  onRefresh?: () => void;
}

const Logs: React.FC<LogsProps> = ({ history = [], onRefresh }) => {
  const [filter, setFilter] = useState<'all' | 'error' | 'warning' | 'info'>('all');

  const handleClear = async () => {
    if (!confirm("確定要清除所有執行日誌嗎？此操作不可撤銷。")) return;
    try {
      // @ts-ignore
      if (window.pywebview && window.pywebview.api) {
        // @ts-ignore
        await window.pywebview.api.clear_history();
        if (onRefresh) onRefresh();
      }
    } catch (e) {
      alert("清除失敗: " + e);
    }
  };

  const handleDownload = async () => {
    try {
      // @ts-ignore
      if (window.pywebview && window.pywebview.api) {
        // @ts-ignore
        const res = await window.pywebview.api.export_history();
        if (res.status === 'success') {
          alert(`日誌已匯出至: ${res.path}`);
        } else if (res.status === 'error') {
          alert(`匯出失敗: ${res.message}`);
        }
      }
    } catch (e) {
      alert("匯出發生錯誤: " + e);
    }
  };

  const filteredLogs = filter === 'all'
    ? history
    : history.filter(entry => {
      if (filter === 'error') return entry.status === 'Error';
      if (filter === 'info') return entry.status === 'Completed';
      return false;
    });

  const getLevelBadge = (status: string) => {
    switch (status) {
      case 'Completed': return 'bg-emerald-50 text-emerald-600 dark:bg-emerald-600/10 dark:text-emerald-400';
      case 'Error': return 'bg-red-50 text-red-600 dark:bg-red-600/10 dark:text-red-400';
      case 'running': return 'bg-blue-50 text-blue-600 dark:bg-blue-600/10 dark:text-blue-400';
      default: return 'bg-slate-100 text-slate-500';
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-[1400px] mx-auto flex flex-col h-full">
      <div className="flex items-end justify-between flex-shrink-0">
        <div>
          <h2 className="text-3xl font-black tracking-tighter mb-1 dark:text-white">執行日誌</h2>
          <p className="text-sm font-bold text-slate-500 dark:text-slate-500 uppercase tracking-widest">追蹤系統自動化任務的執行紀錄與狀態。</p>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-100/50 dark:bg-white/5 p-1 rounded-xl border border-slate-200 dark:border-white/5 shadow-inner">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${filter === 'all' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
          >
            全部
          </button>
          <button
            onClick={() => setFilter('error')}
            className={`px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${filter === 'error' ? 'bg-red-500 text-white shadow-lg shadow-red-500/25' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
          >
            錯誤
          </button>
          <button
            onClick={() => setFilter('info')}
            className={`px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${filter === 'info' ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
          >
            已完成
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={async () => {
              // @ts-ignore
              if (window.pywebview && window.pywebview.api) window.pywebview.api.open_logs_folder();
            }}
            className="flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-white/5 text-slate-600 dark:text-slate-400 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-slate-50 dark:hover:bg-white/10 border border-slate-200 dark:border-white/5 transition-all active:scale-95 group shadow-sm"
            title="開啟 Windows 日誌資料夾"
          >
            <span className="material-symbols-outlined text-sm group-hover:rotate-12 transition-transform">folder_open</span>
            開啟日誌目錄
          </button>
        </div>

      </div>

      <div className="flex-1 bg-white/80 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200 dark:border-white/5 rounded-2xl shadow-sm flex flex-col overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-white/5 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
              <span className="text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-[0.2em]">Live Activity</span>
            </div>
            <div className="h-3 w-px bg-slate-200 dark:bg-white/10"></div>
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">顯示最近 50 條記錄</span>
          </div>
          <div className="flex gap-1">
            <button
              onClick={handleDownload}
              className="p-2 text-slate-400 hover:text-blue-500 transition-all hover:bg-blue-500/10 rounded-xl"
              title="匯出紀錄 (CSV)"
            >
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
            <button
              onClick={handleClear}
              className="p-2 text-slate-400 hover:text-red-500 transition-all hover:bg-red-500/10 rounded-xl"
              title="清空歷史"
            >
              <span className="material-symbols-outlined text-[20px]">delete</span>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto no-scrollbar font-mono text-sm leading-relaxed">
          <table className="w-full text-left border-collapse table-auto">
            <thead className="sticky top-0 bg-white dark:bg-slate-900 z-10 border-b border-slate-100 dark:border-slate-800 shadow-sm">
              <tr className="text-xs font-black uppercase text-slate-400 tracking-widest">
                <th className="px-6 py-3 w-40">時間</th>
                <th className="px-6 py-3 w-28">狀態</th>
                <th className="px-6 py-3 w-1/3">任務名稱</th>
                <th className="px-6 py-3 w-28">耗時</th>
                <th className="px-6 py-3">執行訊息</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group">
                    <td className="px-6 py-3 text-slate-400">{log.time}</td>
                    <td className="px-6 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-black uppercase tracking-tight ${getLevelBadge(log.status)}`}>
                        {log.status === 'Completed' ? '成功' : log.status === 'Error' ? '錯誤' : log.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 font-bold text-slate-700 dark:text-slate-300 break-all" title={log.name}>
                      {log.name}
                    </td>
                    <td className={`px-6 py-3 ${log.status === 'Error' ? 'text-red-500' : 'text-slate-600 dark:text-slate-400'}`}>
                      {log.duration}
                    </td>
                    <td className="px-6 py-3 text-slate-500 dark:text-slate-400 break-words line-clamp-2 hover:line-clamp-none transition-all cursor-help" title={log.message}>
                      {log.message || '--'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-10 text-center text-slate-400 italic">
                    尚無執行紀錄
                  </td>
                </tr>
              )}
              {/* Dummy padding for better scrolling */}
              <tr><td colSpan={5} className="h-10"></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Logs;
