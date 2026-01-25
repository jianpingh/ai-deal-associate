"""
分析 MS Canopy Template 的计算逻辑
读取关键单元格的值和公式
"""
import sys
sys.path.insert(0, 'backend')

import win32com.client
import pythoncom
import os

template_path = os.path.abspath('backend/data/templates/MS Canopy Template -v5.xlsx')

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

workbook = excel.Workbooks.Open(template_path, UpdateLinks=False)
excel.CalculateFull()

print("=" * 80)
print("MS Canopy Template 计算逻辑分析")
print("=" * 80)

# 1. Money Page 关键单元格
print("\n【Money Page 关键单元格】")
money_page = workbook.Sheets("Money Page")

cells_to_check = [
    ("E31", "Total Investment Cost (TIC)"),
    ("E43", "LTV"),
    ("E44", "Senior Debt"),
    ("E30", "Net Purchase Price"),
    ("E32", "Purchasers Costs"),
    ("E33", "Capex"),
]

for cell, desc in cells_to_check:
    val = money_page.Range(cell).Value
    formula = money_page.Range(cell).Formula
    print(f"  {cell} ({desc}): Value={val}, Formula={formula}")

# 2. Input Other 关键单元格
print("\n【Input Other 关键单元格】")
input_other = workbook.Sheets("Input Other")

input_cells = [
    ("B1", "Project Name"),
    ("B4", "Hold Period"),
    ("B5", "Market Rent (ERV)"),
    ("B12", "Entry Cap Rate"),
    ("B13", "Transfer Taxes"),
    ("B15", "Exit Cap Rate"),
]

for cell, desc in input_cells:
    val = input_other.Range(cell).Value
    print(f"  {cell} ({desc}): {val}")

# 3. Debt Schedule
print("\n【Debt Schedule (Bullet) 关键单元格】")
debt_schedule = workbook.Sheets("Debt Schedule (Bullet)")

debt_cells = [
    ("D10", "Interest Rate"),
    ("D11", "Loan Amount"),
]

for cell, desc in debt_cells:
    val = debt_schedule.Range(cell).Value
    formula = debt_schedule.Range(cell).Formula
    print(f"  {cell} ({desc}): Value={val}, Formula={formula}")

# 4. Cash Flows sheet - 关键行
print("\n【Cash Flows Sheet 关键单元格】")
cash_flows = workbook.Sheets("Cash Flows")

# Row 78 是日期行，Row 102 是 Levered Post Tax CF
print("\n  日期行 (Row 78) - 前几个季度:")
for col in ['T', 'U', 'V', 'W', 'X']:
    val = cash_flows.Range(f"{col}78").Value
    print(f"    {col}78: {val}")

print("\n  Levered Post Tax CF (Row 102) - 前几个季度:")
for col in ['T', 'U', 'V', 'W', 'X']:
    val = cash_flows.Range(f"{col}102").Value
    formula = cash_flows.Range(f"{col}102").Formula
    print(f"    {col}102: Value={val}, Formula={formula[:50] if formula else 'N/A'}...")

# 5. 关键输出单元格
print("\n【关键输出单元格 (Cash Flows E列)】")
output_cells = [
    ("E105", "Equity Invested"),
    ("E107", "Levered IRR"),
    ("E108", "Levered Multiple"),
    ("E110", "Net Gain/(Loss)"),
]

for cell, desc in output_cells:
    val = cash_flows.Range(cell).Value
    formula = cash_flows.Range(cell).Formula
    print(f"  {cell} ({desc}):")
    print(f"    Value: {val}")
    print(f"    Formula: {formula}")

# 6. 分析 EBITDA 和现金流组成
print("\n【EBITDA 和现金流组成 (第一个季度 T列)】")
cf_rows = [
    (80, "EBITDA"),
    (82, "Senior Interest"),
    (83, "Upfront Fees"),
    (84, "Taxes"),
    (86, "Cash Flows From Operations"),
    (88, "Total Capex"),
    (90, "Net Disposal Proceeds"),
    (92, "Total Acquisition Price"),
    (94, "Cash Flows From Investing Activities"),
    (96, "Total Debt Issuance"),
    (97, "Total Debt Repayment"),
    (99, "Cash Flows From Financing Activities"),
    (102, "Levered Post Tax CF"),
]

for row, desc in cf_rows:
    val = cash_flows.Range(f"T{row}").Value
    formula = cash_flows.Range(f"T{row}").Formula
    if val or formula:
        print(f"  Row {row} ({desc}): Value={val}, Formula={formula[:60] if formula else 'N/A'}")

# 7. 获取完整的现金流序列
print("\n【完整的 Levered Post Tax CF 序列】")
print("  从 T102 到 BH102 (季度现金流):")

# 找到现金流的起止列
cf_values = []
cf_dates = []
for col_num in range(20, 61):  # T=20, BH=60
    col_letter = ""
    if col_num <= 26:
        col_letter = chr(ord('A') + col_num - 1)
    else:
        col_letter = chr(ord('A') + (col_num - 1) // 26 - 1) + chr(ord('A') + (col_num - 1) % 26)
    
    val = cash_flows.Range(f"{col_letter}102").Value
    date_val = cash_flows.Range(f"{col_letter}78").Value
    
    if val is not None:
        cf_values.append(val)
        cf_dates.append(date_val)

print(f"  共 {len(cf_values)} 个季度")
print(f"  现金流范围: {min(cf_values):,.0f} 到 {max(cf_values):,.0f}")
print(f"  负现金流(投资): {sum(v for v in cf_values if v < 0):,.0f}")
print(f"  正现金流(收益): {sum(v for v in cf_values if v > 0):,.0f}")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
