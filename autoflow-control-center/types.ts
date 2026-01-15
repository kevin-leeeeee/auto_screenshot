
export enum TaskStatus {
  COMPLETED = '完成',
  RUNNING = '執行中',
  ERROR = '錯誤',
  WARNING = '警告',
  PAUSED = '已暫停',
}

export interface Task {
  id: string;
  name: string;
  status: TaskStatus;
  duration: string;
  time: string;
  progress?: number;
  lastRun?: string;
}

export interface AutomationConfig {
  waitPerPage: { min: number, max: number }; // replace simple number
  screenshotDelay: number;
  cropEnabled: boolean;
  cropTop: number;
  cropBottom: number;
  range: 'viewport' | 'fullscreen';
  batchRestEnabled: boolean;
  batchSize: number;
  batchRestRange: { min: number, max: number };
  keywords: string[];
  autoWordExport: boolean;
  skipDone: boolean;
  // Extended Config
  captchaKeywords: string[];
  notFoundKeywords: string[];
  loginKeywords: string[];
  bsmiKeywords: string[];
  textCheckEnabled: boolean;
  scrollCapture: boolean;
  scrollStitch: boolean;
  scrollTimes: number;
  customCategories?: Record<string, string[]>;
  categoryPause?: Record<string, boolean>;
  inputFiles: any[]; // Changed to any[] to support objects with {path, name}
  inputFilesDisplay: string[]; // for display names
  // Legacy single file support (optional, can keep for compatibility or remove)
  inputFile?: string;
  inputFileDisplay?: string;
  outputDir?: string;
  outputDirDisplay?: string;

}

export interface DisplaySettings {
  theme: 'light' | 'dark';
  fontSize: number; // 1-7
}

export type ViewType = 'dashboard' | 'tasks' | 'logs' | 'settings';
