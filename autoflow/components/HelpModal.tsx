
import React from 'react';

interface HelpModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-300"
                onClick={onClose}
            ></div>

            {/* Modal Content */}
            <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300 border border-slate-200 dark:border-slate-800 flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/30">
                    <div className="flex items-center gap-3">
                        <div className="size-10 rounded-xl bg-blue-600/10 text-blue-600 flex items-center justify-center">
                            <span className="material-symbols-outlined">help_center</span>
                        </div>
                        <div>
                            <h2 className="text-xl font-black dark:text-white leading-none">使用說明與技術支援</h2>
                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">User Guide & System Support</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-red-500 transition-all"
                    >
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    <div className="space-y-12">

                        {/* Step 1: Excel to TXT */}
                        <section className="relative">
                            <div className="flex items-center gap-4 mb-4">
                                <span className="size-8 rounded-full bg-emerald-600 text-white flex items-center justify-center text-sm font-black italic shadow-lg shadow-emerald-600/20">01</span>
                                <h3 className="text-lg font-bold text-slate-800 dark:text-white">Excel 轉 TXT 轉換指南</h3>
                            </div>
                            <div className="pl-12 space-y-3">
                                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                    將公文系統匯出的 Excel 檔案拖入區域，系統會自動根據「檢舉人」與「聯絡信箱」進行分組，並產出符合系統輸入格式的 TXT 文件。
                                </p>
                                <div className="grid grid-cols-2 gap-3 text-xs font-medium">
                                    <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700 flex items-center gap-2">
                                        <span className="material-symbols-outlined text-base text-emerald-500">done_all</span>
                                        <span className="dark:text-slate-300">支援 .xlsx, .xls, .csv</span>
                                    </div>
                                    <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700 flex items-center gap-2">
                                        <span className="material-symbols-outlined text-base text-emerald-500">group</span>
                                        <span className="dark:text-slate-300">自動合併相同檢舉人</span>
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Step 2: Auto Screenshot */}
                        <section className="relative">
                            <div className="flex items-center gap-4 mb-4">
                                <span className="size-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black italic shadow-lg shadow-blue-600/20">02</span>
                                <h3 className="text-lg font-bold text-slate-800 dark:text-white">自動截圖任務流程</h3>
                            </div>
                            <div className="pl-12 space-y-3">
                                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                    點擊「啟動任務」後，系統會自動在後端開啟瀏覽器並依序擷取畫面。您可以透過右下角的迷你視窗觀察即時進度。
                                </p>
                                <ul className="space-y-2 text-xs dark:text-slate-400">
                                    <li className="flex items-start gap-2">
                                        <span className="material-symbols-outlined text-sm text-blue-500 mt-0.5">ads_click</span>
                                        <span>遇到風險驗證或登入頁面，系統會自動暫停並跳出提示，請手動處理後繼續。</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="material-symbols-outlined text-sm text-blue-500 mt-0.5">folder_open</span>
                                        <span>完成後檔案會自動由「產出 Word」按鈕封裝為正式文件。</span>
                                    </li>
                                </ul>
                            </div>
                        </section>

                        {/* Support */}
                        <section className="p-6 bg-blue-600/5 dark:bg-blue-600/10 rounded-2xl border border-blue-600/10">
                            <div className="flex items-center gap-3 mb-4">
                                <span className="material-symbols-outlined text-blue-600">support_agent</span>
                                <h3 className="font-bold text-blue-600">需要更多協助？</h3>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-4">
                                如果您在使用過程中遇到任何技術問題、錯誤回報或有新功能建議，請隨時連繫開發團隊。
                            </p>
                            <div className="flex gap-4">
                                <button
                                    onClick={() => window.open('mailto:kevin559009390@gmail.com', '_blank')}
                                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 py-3 rounded-xl shadow-sm text-xs font-bold text-slate-700 dark:text-slate-300 hover:shadow-md transition-all flex items-center justify-center gap-2"
                                >
                                    <span className="material-symbols-outlined text-sm">mail</span>
                                    <span>電子郵件聯繫</span>
                                </button>
                                <button
                                    onClick={() => window.open('https://github.com/kevin-leeeeee/auto_screenshot', '_blank')}
                                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 py-3 rounded-xl shadow-sm text-xs font-bold text-slate-700 dark:text-slate-300 hover:shadow-md transition-all flex items-center justify-center gap-2"
                                >
                                    <span className="material-symbols-outlined text-sm">open_in_new</span>
                                    <span>查看官方 GitHub</span>
                                </button>
                            </div>
                        </section>

                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                    </div>
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-black uppercase tracking-widest rounded-xl hover:opacity-90 transition-all active:scale-95"
                    >
                        我瞭解了
                    </button>
                </div>

            </div>
        </div>
    );
};

export default HelpModal;
