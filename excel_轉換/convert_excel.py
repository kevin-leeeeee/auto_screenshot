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

def main():
    input_file = select_file()
    
    if not input_file:
        print("未選擇檔案，程式結束。")
        return

    print(f"正在處理: {input_file}")

    try:
        wb = openpyxl.load_workbook(input_file, data_only=True)
        ws = wb.active
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        input("Press Enter to exit...") # Pause so user can see error
        return

    # Get headers
    headers = {}
    row_iter = ws.iter_rows(values_only=True)
    try:
        header_row = next(row_iter)
    except StopIteration:
        print("Error: Empty file")
        return

    for idx, col_name in enumerate(header_row):
        headers[normalize(col_name)] = idx

    # Ensure required columns exist
    required_cols = ["公文文號", "檢舉人", "檢舉人信箱", "網址"]
    missing = [col for col in required_cols if col not in headers]
    if missing:
        print(f"Error: Missing columns {missing}")
        print(f"Available columns: {list(headers.keys())}")
        input("Press Enter to exit...")
        return

    # Read data
    data = []
    for row in row_iter:
        # Check if row is empty/all None
        if not any(row):
            continue
        row_data = {
            "公文文號": normalize(row[headers["公文文號"]]),
            "檢舉人": normalize(row[headers["檢舉人"]]),
            "檢舉人信箱": normalize(row[headers["檢舉人信箱"]]),
            "網址": normalize(row[headers["網址"]]),
        }
        data.append(row_data)

    if not data:
        print("No data found.")
        return

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
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("output", timestamp)
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

if __name__ == "__main__":
    main()
