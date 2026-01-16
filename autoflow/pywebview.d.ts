// Type definitions for pywebview API
interface PyWebViewAPI {
    // Excel conversion
    select_excel_file(): Promise<{ status: string; path?: string; filename?: string }>;
    run_excel_convert(start_date?: string, end_date?: string): Promise<any>;

    // Screenshot automation
    select_file(file_types?: any): Promise<any>;
    select_multiple_files(): Promise<any>;
    select_input_folder(): Promise<any>;
    select_directory(): Promise<any>;
    start_screenshot(config: any): Promise<any>;
    get_task_status(): Promise<any>;

    // File operations
    open_file(path: string): Promise<boolean>;
    open_folder(path: string): Promise<boolean>;
    open_logs_folder(): Promise<boolean>;
    open_downloads_folder(): Promise<{ status: string; path: string }>;

    // App state
    get_app_state(): Promise<any>;
    save_settings(settings: any): Promise<any>;
    clear_history(): Promise<any>;
    export_history(): Promise<any>;

    // Update functions
    check_update(): Promise<{
        has_update: boolean;
        current_version: string;
        latest_version?: string;
        release_url?: string;
        download_url?: string;
        changelog?: string;
        published_at?: string;
        release_name?: string;
        error?: string;
    }>;
    get_update_info(): Promise<any>;
    update_scripts(): Promise<{
        status: string;
        details?: string[];
        backups?: string[];
        message?: string;
        new_version?: string;
    }>;
    download_full_update(save_path?: string): Promise<{
        status: string;
        path?: string;
        message: string;
        size_mb?: number;
        version?: string;
    }>;

    // Browser
    open_browser(url: string): Promise<void>;

    // Other
    clear_done_log(input_file_path: string): Promise<any>;
}

interface Window {
    pywebview: {
        api: PyWebViewAPI;
    };
}
