"""
深入分析 Excel TIC (Total Investment Cost) 的计算逻辑
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
print("分析 Excel TIC (Total Investment Cost) 计算逻辑")
print("=" * 80)

# Money Page E31 = -'Cash Flows'!T61
# 需要找到 Cash Flows T61 是什么

cash_flows = workbook.Sheets("Cash Flows")
money_page = workbook.Sheets("Money Page")

print("\n【Cash Flows Sheet - T列关键行】")
for row in range(55, 75):
    val = cash_flows.Range(f"T{row}").Value
    formula = cash_flows.Range(f"T{row}").Formula
    label_b = cash_flows.Range(f"B{row}").Value
    if val or formula or label_b:
        print(f"  Row {row}: B={label_b}, T={val}, Formula={formula[:60] if formula else 'N/A'}")

print("\n【Money Page - 关键单元格详细】")
mp_cells = [
    ("E28", "Description"),
    ("E29", "Passing Rent / Gross Income"),
    ("E30", "Entry Cap Rate"),
    ("E31", "Total Investment Cost (TIC)"),
    ("E32", "Purchasers Costs"),
    ("E33", "Closing Costs"),
    ("E34", "Description"),
    ("E40", "Tax Rate"),
    ("E43", "LTV"),
    ("E44", "Senior Debt"),
]

for cell, desc in mp_cells:
    val = money_page.Range(cell).Value
    formula = money_page.Range(cell).Formula
    print(f"  {cell} ({desc}): Value={val}, Formula={formula}")

# 深入分析 Cash Flows T61 的组成
print("\n【Cash Flows T61 (Total Acquisition Price) 详细分析】")
t61_val = cash_flows.Range("T61").Value
t61_formula = cash_flows.Range("T61").Formula
print(f"  T61 Value: {t61_val}")
print(f"  T61 Formula: {t61_formula}")

# 看 T61 引用了哪些行
print("\n【Cash Flows T55-T65 详细】")
for row in range(55, 66):
    val = cash_flows.Range(f"T{row}").Value
    formula = cash_flows.Range(f"T{row}").Formula
    label = cash_flows.Range(f"B{row}").Value
    print(f"  T{row} ({label}): Value={val:,.2f if val else 0:.2f}, Formula={formula}")

# 验证 TIC 计算
print("\n【验证 TIC 计算】")
passing_rent = cash_flows.Range("T48").Value or 0  # 假设 T48 是收入
entry_cap = money_page.Range("E30").Value
purchasers_costs = money_page.Range("E32").Value
closing_costs = money_page.Range("E33").Value
tic = money_page.Range("E31").Value

print(f"  Input Rent Roll Total: €{1631706.50:,.2f}")  # 已知
print(f"  Entry Cap Rate: {entry_cap}")
print(f"  Purchasers Costs %: {purchasers_costs}")
print(f"  Closing Costs %: {closing_costs}")
print(f"  Actual TIC from Excel: €{tic:,.2f}")

# 计算验证
if entry_cap and entry_cap > 0:
    calc_net_price = 1631706.50 / entry_cap
    calc_tic = calc_net_price * (1 + purchasers_costs + closing_costs)
    print(f"\n  计算验证:")
    print(f"    Net Purchase Price = 1,631,706.50 / {entry_cap} = €{calc_net_price:,.2f}")
    print(f"    TIC = {calc_net_price:,.2f} * (1 + {purchasers_costs} + {closing_costs}) = €{calc_tic:,.2f}")
    print(f"    差异: €{tic - calc_tic:,.2f}")

# 查看 Cash Flows 是如何计算收入的
print("\n【Cash Flows 收入计算】")
input_rr = workbook.Sheets("Input Rent Roll")
print("  Input Rent Roll G列 (年租金):")
total_rent = 0
for row in range(2, 10):
    rent = input_rr.Range(f"G{row}").Value
    if rent:
        total_rent += rent
        name = input_rr.Range(f"A{row}").Value
        print(f"    Row {row}: {name} = €{rent:,.2f}")
print(f"  Total: €{total_rent:,.2f}")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
