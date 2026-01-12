
import React from 'react';
import { TaskStatus } from '../types';

interface TasksProps {
  onShowLogs: (id: string) => void;
}

const Tasks: React.FC<TasksProps> = ({ onShowLogs }) => {
  const workflows = [
    {
      id: 'WF-001',
      name: '庫存每日自動對帳',
      description: '自動比對 ERP 系統與實體倉庫庫存 Excel，並輸出異常報告。',
      status: TaskStatus.RUNNING,
      progress: 65,
      lastRun: '2023-11-24 09:00',
      frequency: '每日',
    },
    {
      id: 'WF-002',
      name: '電商平台價格爬蟲',
      description: '抓取 PChome、Momo 競品價格，並更新至內部價格庫。',
      status: TaskStatus.COMPLETED,
      progress: 100,
      lastRun: '2023-11-24 10:30',
      frequency: '每 4 小時',
    },
    {
      id: 'WF-003',
      name: '財務報表自動彙總',
      description: '從各部門上傳的 Excel 中提取關鍵指標，彙整至總表。',
      status: TaskStatus.ERROR,
      progress: 12,
      lastRun: '2023-11-24 08:45',
      frequency: '每週一',
    },
    {
      id: 'WF-004',
      name: '客戶滿意度分析',
      description: '分析問卷調查數據，並自動產生 Word 總結報告。',
      status: TaskStatus.PAUSED,
      progress: 0,
      lastRun: '2023-11-23 16:20',
      frequency: '手動觸發',
    }
  ];

  const getStatusStyle = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.RUNNING: return 'bg-blue-600/10 text-blue-600 border-blue-600/20';
      case TaskStatus.COMPLETED: return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case TaskStatus.ERROR: return 'bg-red-500/10 text-red-500 border-red-500/20';
      case TaskStatus.PAUSED: return 'bg-slate-500/10 text-slate-500 border-slate-500/20';
      default: return 'bg-slate-100 text-slate-400';
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-[1400px] mx-auto">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-3xl font-black tracking-tight mb-1 dark:text-white">任務管理</h2>
          <p className="text-slate-500 dark:text-slate-400">監控與調度所有自動化工作流的運行狀態。</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm dark:text-white">
            <span className="material-symbols-outlined text-sm">filter_alt</span>
            篩選
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200 dark:shadow-none">
            <span className="material-symbols-outlined text-sm">add</span>
            建立新任務
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {workflows.map((wf) => (
          <div key={wf.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className={`size-12 rounded-xl flex items-center justify-center ${getStatusStyle(wf.status)} border`}>
                    <span className="material-symbols-outlined text-2xl">
                      {wf.status === TaskStatus.RUNNING ? 'autorenew' : 
                       wf.status === TaskStatus.COMPLETED ? 'check_circle' : 
                       wf.status === TaskStatus.ERROR ? 'report' : 'pause_circle'}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-slate-800 dark:text-white">{wf.name}</h3>
                    <p className="text-xs font-mono text-slate-400">{wf.id} • {wf.frequency}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${getStatusStyle(wf.status)}`}>
                  {wf.status}
                </div>
              </div>

              <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6 h-10 overflow-hidden line-clamp-2">
                {wf.description}
              </p>

              <div className="space-y-4">
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-bold">
                    <span className="text-slate-400">執行進度</span>
                    <span className="text-blue-600">{wf.progress}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-1000 ease-out ${
                        wf.status === TaskStatus.ERROR ? 'bg-red-500' : 'bg-blue-600'
                      }`}
                      style={{ width: `${wf.progress}%` }}
                    ></div>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs text-slate-400 border-t border-slate-50 dark:border-slate-800 pt-4">
                  <span>上次執行：{wf.lastRun}</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => onShowLogs(wf.id)}
                      className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500 transition-colors"
                      title="查看日誌"
                    >
                      <span className="material-symbols-outlined text-[18px]">list_alt</span>
                    </button>
                    <button className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500 transition-colors" title="編輯設定">
                      <span className="material-symbols-outlined text-[18px]">settings</span>
                    </button>
                    <button 
                      className={`p-1.5 rounded transition-all ${
                        wf.status === TaskStatus.RUNNING 
                        ? 'text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-500/10' 
                        : 'text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-600/10'
                      }`}
                      title={wf.status === TaskStatus.RUNNING ? '暫停任務' : '立即啟動'}
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        {wf.status === TaskStatus.RUNNING ? 'pause' : 'play_arrow'}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tasks;
