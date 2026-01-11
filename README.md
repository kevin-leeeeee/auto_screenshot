# Screenshot Tool (test.py)

## Quick Start
- Run with UI (recommended): double click `test.py` or `python test.py`
- Run with CLI: `python test.py urls.txt`

## UI Options
- Input settings:
  - URLs file: pick a `.txt` file, one URL per line.
  - Lines starting with `#` are notes and will be inserted into the Word output.
- Output settings:
  - Output folder: where screenshots are saved.
- Humanized:
  - Page wait (seconds): random wait range before capture.
  - Countdown (seconds): final countdown overlay before screenshot.
  - Scroll capture: 2 shots, scrolls configurable PageDown count between them.
- Capture area:
  - Screenshot mode: full or window.
  - Crop is optional and configurable (top/bottom pixels).
  - PageDown count is configurable.
- Batch mode:
  - Enable/disable rest between batches.
  - Batch size and rest range (seconds).
- Output record:
  - Record output file path into `done_urls.json`.
  - Clear all records (URLs + outputs) via button.
- Word export:
  - Save URL + image into a `.docx` in the output folder (requires `python-docx`).
  - Each run generates a new Word file (timestamp in filename).
- Preferences:
  - Auto-saved when you click Start, loaded on next launch.
- Text classification (Ctrl+A):
  - Use Ctrl+A + Ctrl+C to read page text after screenshot.
  - If classification hits Login/Captcha, capture will pause for manual action.
  - Categories: 驗證是否人類 / 商品不存在 / 商品存在 且有BSMI認證 / 無法判斷
  - Keywords can be edited in UI (comma-separated). Use "關鍵字設定" to show fields.

## Files
- `done_urls.json`: records completed URLs. When "Record output file" is enabled, each entry stores `url` and `output`.
- `preferences.json`: saved UI preferences (last settings).

## Text Classification Setup
- Works by Ctrl+A + Ctrl+C; no extra install required.

## Notes
- `urls.txt` default is in the working directory.
- `screenshots_<urls_file>` is the default output folder if you leave output empty.

## Packaging
- Use a clean venv to avoid bundling unrelated packages.
  - `python -m venv .venv`
  - `.venv\\Scripts\\python -m pip install pyinstaller pyautogui pillow python-docx pygetwindow`
- Build with spec (onedir):
  - `.venv\\Scripts\\python -m PyInstaller -y screenshot_tool.spec`
- Output: `dist\\screenshot_tool\\screenshot_tool.exe`
