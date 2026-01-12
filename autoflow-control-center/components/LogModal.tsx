
import React from 'react';

interface LogModalProps {
  taskId: string;
  onClose: () => void;
}

const LogModal: React.FC<LogModalProps> = ({ taskId, onClose }) => {
  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-8 duration-300">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white sticky top-0">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center">
              <span className="material-symbols-outlined">error</span>
            </div>
            <div>
              <h2 className="text-xl font-black text-slate-800">任務執行錯誤</h2>
              <p className="text-xs text-slate-500 font-medium tracking-tight">任務 ID: {taskId} • 發生於 2023-11-24 10:42:15</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full text-slate-400 transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="p-6 bg-slate-50 flex-1 overflow-hidden flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-slate-700 flex items-center gap-2">
              <span className="material-symbols-outlined text-base text-slate-400">terminal</span>
              系統日誌輸出 (Standard Output / Error)
            </span>
            <div className="flex gap-2">
              <button className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-2 transition-all shadow-sm">
                <span className="material-symbols-outlined text-sm">content_copy</span>
                複製日誌
              </button>
              <button className="px-3 py-1.5 bg-slate-200/50 border border-slate-300 rounded-lg text-xs font-bold text-slate-400 flex items-center gap-2 transition-all">
                <span className="material-symbols-outlined text-sm">delete_sweep</span>
                清除舊紀錄
              </button>
            </div>
          </div>

          <div className="flex-1 bg-slate-900 rounded-xl p-6 font-mono text-sm leading-relaxed overflow-y-auto custom-scrollbar shadow-inner border border-slate-800 text-slate-300">
            <p className="text-slate-500">[10:42:01] 正在初始化 Python 環境...</p>
            <p className="text-slate-500">[10:42:02] 載入核心模組: autoflow.engine.reports</p>
            <p className="text-slate-500">[10:42:05] 連接至遠端資料庫 192.168.1.104... 成功</p>
            <p className="text-slate-500">[10:42:08] 開始執行 SQL 查詢：SELECT * FROM finance_q4_2023</p>
            <p className="text-slate-500">[10:42:12] 正在生成 Excel 緩衝區...</p>
            <p className="text-slate-400 font-bold">[10:42:14] 嘗試匯出至目錄: /mnt/shared/reports/export/</p>
            <p className="text-red-500 font-bold mt-2">[10:42:15] CRITICAL ERROR: Permission Denied (OSError 13)</p>
            <p className="text-red-400 mt-1 ml-4">無法寫入目標路徑，請檢查資料夾權限或磁碟空間。</p>
            <p className="text-red-400 ml-4">Traceback (most recent call last):</p>
            <p className="text-red-400 ml-8">File "main.py", line 428, in execute_export</p>
            <p className="text-red-400 ml-8">File "io_manager.py", line 55, in write_file</p>
            <p className="text-red-500 font-bold mt-2 ml-4">&gt;&gt; PermissionError: [Errno 13] Permission denied: '/mnt/shared/reports/export/finance_report.xlsx'</p>
            <p className="text-slate-500 mt-4">[10:42:15] 任務已中斷，正在釋放資源...</p>
            <p className="text-slate-500">[10:42:16] 處理程序退出。錯誤代碼: 1</p>
            <div className="h-4"></div>
            <p className="animate-pulse text-blue-500 font-bold">_</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">環境參數</p>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600 font-medium">作業系統</span>
                <span className="text-xs font-mono font-bold text-slate-700">Ubuntu 22.04 LTS</span>
              </div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">腳本版本</p>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-600 font-medium">finance_exporter.py</span>
                <span className="text-xs font-mono font-bold text-blue-600">v1.2.0-stable</span>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between bg-slate-50/50 gap-4">
          <button className="w-full sm:w-auto px-6 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-white hover:border-slate-300 hover:shadow-sm transition-all flex items-center justify-center gap-2">
            <span className="material-symbols-outlined text-lg">description</span>
            查看日誌檔案
          </button>
          <div className="flex w-full sm:w-auto gap-3">
            <button onClick={onClose} className="flex-1 sm:flex-none px-6 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all">
              取消
            </button>
            <button className="flex-1 sm:flex-none px-8 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-lg">replay</span>
              重新嘗試 (Try Again)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogModal;
