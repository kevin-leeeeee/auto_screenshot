import openpyxl
import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog
import ctypes

def enable_dpi_awareness():
    # Fix blurry UI on Windows High DPI screens
    try:
        # For Windows 10+
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            # For older Windows
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def normalize(val):
    if val is None:
        return ""
    return str(val).strip()

def select_file():
    # Allow command line argument for testing purposes
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return sys.argv[1]
    
    enable_dpi_awareness()
    
    # Initialize Tkinter and hide the main window
    root = tk.Tk()
    root.withdraw()
    
    print("請選擇 Excel 檔案...")
    file_path = filedialog.askopenfilename(
        title="請選擇 Excel 檔案",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
    )
    return file_path

def main(input_file=None, start_date=None, end_date=None):
    if not input_file:
        input_file = select_file()
    
    if not input_file:
        print("未選擇檔案，程式結束。")
        return

    print(f"正在處理: {input_file}")
    if start_date:
        print(f"篩選起始日期: {start_date.replace('-', '年', 1).replace('-', '月', 1) + '日'}")
    if end_date:
        print(f"篩選結束日期: {end_date.replace('-', '年', 1).replace('-', '月', 1) + '日'}")

    try:
        wb = openpyxl.load_workbook(input_file, data_only=True)
        ws = wb.active
    except Exception as e:
        raise ValueError(f"讀取 Excel 檔案失敗: {e}")

    # Get headers
    headers = {}
    row_iter = ws.iter_rows(values_only=True)
    try:
        header_row = next(row_iter)
    except StopIteration:
        raise ValueError("錯誤: 檔案內容為空")

    for idx, col_name in enumerate(header_row):
        headers[normalize(col_name)] = idx

    # Ensure required columns exist
    # "檢舉日期" is optional if strictly required only for filtering, but good to have check if filtering is enabled
    required_cols = ["公文文號", "檢舉人", "檢舉人信箱", "網址"] 
    missing = [col for col in required_cols if col not in headers]
    if missing:
        raise ValueError(f"錯誤: 缺少必要欄位 {missing}。現有欄位: {list(headers.keys())}")

    # Parse filter dates
    filter_start = None
    filter_end = None
    try:
        if start_date:
            filter_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            filter_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("日期格式錯誤，請使用 年-月-日 (例如 2024-01-01)")

    # Read data
    data = []
    
    # Check if we need to filter by date
    check_date = (filter_start is not None) or (filter_end is not None)
    date_col_idx = headers.get("檢舉日期")
    
    if check_date and date_col_idx is None:
        raise ValueError("無法篩選日期：Excel 中找不到「檢舉日期」欄位")

    for row in row_iter:
        # Check if row is empty/all None
        if not any(row):
            continue
            
        # Date filtering logic
        if check_date:
            raw_date = row[date_col_idx]
            row_date = None
            if isinstance(raw_date, datetime.datetime):
                row_date = raw_date.date()
            elif isinstance(raw_date, str):
                try:
                    # Try parsing common formats
                    if "-" in raw_date:
                         row_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
                    elif "/" in raw_date:
                         row_date = datetime.datetime.strptime(raw_date, "%Y/%m/%d").date()
                except:
                    pass
            
            if row_date:
                if filter_start and row_date < filter_start:
                    continue
                if filter_end and row_date > filter_end:
                    continue
            else:
                # If date is missing or invalid format, decide policy. 
                # Strict: skip. Loose: keep. Let's skip to be safe if filtering is ON.
                continue

        row_data = {
            "公文文號": normalize(row[headers["公文文號"]]),
            "檢舉人": normalize(row[headers["檢舉人"]]),
            "檢舉人信箱": normalize(row[headers["檢舉人信箱"]]),
            "網址": normalize(row[headers["網址"]]),
        }
        data.append(row_data)

    if not data:
        raise ValueError("錯誤: 未在 Excel 中找到有效數據 (可能因日期篩選而為空)")

    # Union-Find initialization
    parent = list(range(len(data)))
    
    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_j] = root_i

    # Map values to row indices
    value_to_indices = {}

    for idx, row in enumerate(data):
        informant = row["檢舉人"]
        email = row["檢舉人信箱"]

        keys = []
        if informant:
            keys.append(f"NAME:{informant}")
        if email:
            keys.append(f"EMAIL:{email}")
        
        for key in keys:
            if key not in value_to_indices:
                value_to_indices[key] = []
            value_to_indices[key].append(idx)

    # Union rows that share the same key
    for key, indices in value_to_indices.items():
        first_idx = indices[0]
        for other_idx in indices[1:]:
            union(first_idx, other_idx)

    # Group rows by root
    groups = {}
    for idx in range(len(data)):
        root = find(idx)
        if root not in groups:
            groups[root] = []
        groups[root].append(idx)

    # Output directory with timestamp
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(script_dir, "output", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Process groups
    print(f"Found {len(groups)} unique groups.")
    print(f"Output directory: {output_dir}")
    
    for group_idx, (root, row_indices) in enumerate(groups.items()):
        # Sort indices to preserve original order
        row_indices.sort()
        
        # Collect content
        lines = []
        first_doc_no = None

        for idx in row_indices:
            row = data[idx]
            doc_no = row["公文文號"]
            url = row["網址"]

            if first_doc_no is None:
                first_doc_no = doc_no

            lines.append(f"#文號{doc_no}")
            lines.append(url)
            lines.append("") # Empty line after each pair
        
        # Sanitize filename
        safe_name = "".join(c for c in first_doc_no if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_name:
            safe_name = f"Group_{group_idx + 1}"
            
        filename = f"{safe_name}.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).strip())
        
        print(f"Created: {filepath}")
    
    print("Done!")
    return output_dir

if __name__ == "__main__":
    main()
