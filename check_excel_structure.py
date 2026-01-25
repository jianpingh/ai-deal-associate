import win32com.client
import os

output_path = os.path.abspath(r'backend/data/templates/AUTO_CALCULATED.xlsx')

print("=== Check Cash Flows sheet actual content ===\n")

try:
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    
    workbook = excel.Workbooks.Open(output_path)
    cash_flows = workbook.Sheets("Cash Flows")
    
    print("Check rows 105-110 columns B and C:")
    for row in range(105, 111):
        b_val = cash_flows.Range(f"B{row}").Value
        c_val = cash_flows.Range(f"C{row}").Value
        print(f"Row {row}: B={b_val}, C={c_val}")
    
    print("\nSearch for cells containing 'Equity':")
    used_range = cash_flows.UsedRange
    for row in range(1, min(used_range.Rows.Count + 1, 150)):
        for col in ['B', 'C', 'D', 'E', 'F']:
            cell_val = cash_flows.Range(f"{col}{row}").Value
            if cell_val and isinstance(cell_val, str) and 'equity' in cell_val.lower():
                next_col = chr(ord(col) + 1)
                value = cash_flows.Range(f"{next_col}{row}").Value
                print(f"  {col}{row}: {cell_val} | {next_col}{row}: {value}")
    
    workbook.Close(False)
    excel.Quit()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
