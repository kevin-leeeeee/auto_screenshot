
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
          <h2 className="text-3xl font-black tracking-tight mb-1 dark:text-white">執行日誌</h2>
          <p className="text-slate-500 dark:text-slate-400">追蹤系統自動化任務的執行紀錄與狀態。</p>
        </div>
        <div className="flex items-center gap-2 bg-white dark:bg-slate-900 p-1.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${filter === 'all' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
          >
            全部
          </button>
          <button
            onClick={() => setFilter('error')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${filter === 'error' ? 'bg-red-500 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
          >
            錯誤
          </button>
          <button
            onClick={() => setFilter('info')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${filter === 'info' ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
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
            className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-all active:scale-95 group"
            title="開啟 Windows 日誌資料夾"
          >
            <span className="material-symbols-outlined text-sm group-hover:rotate-12 transition-transform">folder_open</span>
            開啟日誌目錄
          </button>
        </div>

      </div>

      <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[10px] font-black uppercase text-slate-400 tracking-widest">Live Activity</span>
            </div>
            <div className="h-4 w-px bg-slate-200 dark:bg-slate-700"></div>
            <span className="text-xs text-slate-400 font-medium">顯示最近 50 條記錄</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="p-2 text-slate-400 hover:text-blue-600 transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg"
              title="匯出紀錄 (CSV)"
            >
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
            <button
              onClick={handleClear}
              className="p-2 text-slate-400 hover:text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg"
              title="清空歷史"
            >
              <span className="material-symbols-outlined text-[20px]">delete</span>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto no-scrollbar font-mono text-sm leading-relaxed">
          <table className="w-full text-left border-collapse table-fixed">
            <thead className="sticky top-0 bg-white dark:bg-slate-900 z-10 border-b border-slate-100 dark:border-slate-800 shadow-sm">
              <tr className="text-xs font-black uppercase text-slate-400 tracking-widest">
                <th className="px-6 py-3 w-40">時間</th>
                <th className="px-6 py-3 w-28">狀態</th>
                <th className="px-6 py-3 w-1/4">任務名稱</th>
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
                    <td className="px-6 py-3 font-bold text-slate-700 dark:text-slate-300 truncate" title={log.name}>
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
