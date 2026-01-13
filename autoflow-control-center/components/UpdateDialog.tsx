import React, { useState } from 'react';

interface UpdateInfo {
    has_update: boolean;
    current_version: string;
    latest_version?: string;
    release_url?: string;
    download_url?: string;
    changelog?: string;
    published_at?: string;
    release_name?: string;
    error?: string;
}

interface UpdateDialogProps {
    updateInfo: UpdateInfo;
    onClose: () => void;
}

const UpdateDialog: React.FC<UpdateDialogProps> = ({ updateInfo, onClose }) => {
    const [isUpdating, setIsUpdating] = useState(false);
    const [updateStatus, setUpdateStatus] = useState<'idle' | 'downloading' | 'success' | 'error'>('idle');
    const [statusMessage, setStatusMessage] = useState('');

    const handleUpdateScripts = async () => {
        setIsUpdating(true);
        setUpdateStatus('downloading');
        setStatusMessage('正在更新外部腳本...');

        try {
            const result = await window.pywebview.api.update_scripts();

            if (result.status === 'success' || result.status === 'partial') {
                setUpdateStatus('success');
                setStatusMessage('腳本更新完成!');

                // Show details
                if (result.details && Array.isArray(result.details)) {
                    console.log('Update details:', result.details);
                }
            } else {
                setUpdateStatus('error');
                setStatusMessage(result.message || '更新失敗');
            }
        } catch (error) {
            setUpdateStatus('error');
            setStatusMessage(`更新失敗: ${error}`);
        } finally {
            setIsUpdating(false);
        }
    };

    const handleDownloadFull = async () => {
        setIsUpdating(true);
        setUpdateStatus('downloading');
        setStatusMessage('正在下載完整更新包...');

        try {
            const result = await window.pywebview.api.download_full_update();

            if (result.status === 'success') {
                setUpdateStatus('success');
                setStatusMessage(`下載完成! (${result.size_mb} MB)`);

                // Open downloads folder
                setTimeout(async () => {
                    await window.pywebview.api.open_downloads_folder();
                }, 1000);
            } else if (result.status === 'no_update') {
                setUpdateStatus('idle');
                setStatusMessage('目前已是最新版本');
            } else {
                setUpdateStatus('error');
                setStatusMessage(result.message || '下載失敗');
            }
        } catch (error) {
            setUpdateStatus('error');
            setStatusMessage(`下載失敗: ${error}`);
        } finally {
            setIsUpdating(false);
        }
    };

    const handleOpenReleasePage = () => {
        if (updateInfo.release_url) {
            window.open(updateInfo.release_url, '_blank');
        }
    };

    // Format changelog for display
    const formatChangelog = (changelog: string) => {
        if (!changelog) return null;

        // Limit to first 500 characters
        const truncated = changelog.length > 500 ? changelog.substring(0, 500) + '...' : changelog;
        return truncated;
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-slate-200 dark:border-slate-700">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <span className="material-symbols-outlined text-3xl">system_update</span>
                            <div>
                                <h2 className="text-xl font-bold">軟體更新</h2>
                                <p className="text-sm text-blue-100">發現新版本可用</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-white/80 hover:text-white transition-colors"
                            disabled={isUpdating}
                        >
                            <span className="material-symbols-outlined">close</span>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
                    {updateInfo.error ? (
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
                            <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                                <span className="material-symbols-outlined">error</span>
                                <span className="font-medium">{updateInfo.error}</span>
                            </div>
                        </div>
                    ) : updateInfo.has_update ? (
                        <>
                            {/* Version Info */}
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">目前版本</p>
                                    <p className="text-lg font-bold dark:text-white">{updateInfo.current_version}</p>
                                </div>
                                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                                    <p className="text-xs text-blue-600 dark:text-blue-400 mb-1">最新版本</p>
                                    <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{updateInfo.latest_version}</p>
                                </div>
                            </div>

                            {/* Changelog */}
                            {updateInfo.changelog && (
                                <div className="mb-6">
                                    <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">更新內容</h3>
                                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">
                                        {formatChangelog(updateInfo.changelog)}
                                    </div>
                                    <button
                                        onClick={handleOpenReleasePage}
                                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline mt-2"
                                    >
                                        查看完整更新說明 →
                                    </button>
                                </div>
                            )}

                            {/* Status Message */}
                            {statusMessage && (
                                <div className={`mb-4 p-4 rounded-lg border ${updateStatus === 'success'
                                        ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400'
                                        : updateStatus === 'error'
                                            ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400'
                                            : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400'
                                    }`}>
                                    <div className="flex items-center gap-2">
                                        {updateStatus === 'downloading' && (
                                            <span className="material-symbols-outlined animate-spin">progress_activity</span>
                                        )}
                                        {updateStatus === 'success' && (
                                            <span className="material-symbols-outlined">check_circle</span>
                                        )}
                                        {updateStatus === 'error' && (
                                            <span className="material-symbols-outlined">error</span>
                                        )}
                                        <span className="font-medium">{statusMessage}</span>
                                    </div>
                                </div>
                            )}

                            {/* Update Options */}
                            <div className="space-y-3">
                                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                                    <div className="flex items-start gap-3 mb-3">
                                        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">bolt</span>
                                        <div className="flex-1">
                                            <h4 className="font-semibold text-slate-900 dark:text-white mb-1">快速更新 (推薦)</h4>
                                            <p className="text-xs text-slate-600 dark:text-slate-400">僅更新外部腳本,無需重啟程式</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={handleUpdateScripts}
                                        disabled={isUpdating}
                                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                                    >
                                        {isUpdating && updateStatus === 'downloading' ? (
                                            <>
                                                <span className="material-symbols-outlined animate-spin">progress_activity</span>
                                                更新中...
                                            </>
                                        ) : (
                                            <>
                                                <span className="material-symbols-outlined">download</span>
                                                更新腳本
                                            </>
                                        )}
                                    </button>
                                </div>

                                <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-start gap-3 mb-3">
                                        <span className="material-symbols-outlined text-slate-600 dark:text-slate-400">package_2</span>
                                        <div className="flex-1">
                                            <h4 className="font-semibold text-slate-900 dark:text-white mb-1">完整更新</h4>
                                            <p className="text-xs text-slate-600 dark:text-slate-400">下載完整更新包,需手動解壓覆蓋</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={handleDownloadFull}
                                        disabled={isUpdating}
                                        className="w-full bg-slate-600 hover:bg-slate-700 disabled:bg-slate-400 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                                    >
                                        <span className="material-symbols-outlined">download</span>
                                        下載完整更新包
                                    </button>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-8">
                            <span className="material-symbols-outlined text-6xl text-green-500 mb-4">check_circle</span>
                            <p className="text-lg font-semibold text-slate-900 dark:text-white mb-2">目前已是最新版本</p>
                            <p className="text-sm text-slate-600 dark:text-slate-400">{updateInfo.current_version}</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-slate-50 dark:bg-slate-800 px-6 py-4 border-t border-slate-200 dark:border-slate-700">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={handleOpenReleasePage}
                            className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                        >
                            <span className="material-symbols-outlined text-sm">open_in_new</span>
                            前往 GitHub Releases
                        </button>
                        <button
                            onClick={onClose}
                            disabled={isUpdating}
                            className="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 disabled:bg-slate-100 dark:disabled:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg transition-colors font-medium"
                        >
                            關閉
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UpdateDialog;
