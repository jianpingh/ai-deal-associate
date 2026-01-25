"""
深入分析 Excel TIC 和 Cash Flow 的计算逻辑 (修复版)
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
print("关键发现: Excel TIC 计算逻辑")
print("=" * 80)

cash_flows = workbook.Sheets("Cash Flows")
money_page = workbook.Sheets("Money Page")

# 关键发现
print("\n【关键公式】")
print("  Money Page E31 (TIC) = -'Cash Flows'!T61")
print("  Cash Flows T61 (Purchase Price) = -SUM(U23:X23)/$D61")
print("")
print("  这意味着 TIC 不是简单的 Passing Rent / Entry Cap * (1 + costs)")
print("  而是从 Cash Flows Sheet 的 Row 23 计算得来!")

# 查看 Row 23
print("\n【Cash Flows Row 23 - 关键收入行】")
for col in ['B', 'C', 'D', 'T', 'U', 'V', 'W', 'X']:
    val = cash_flows.Range(f"{col}23").Value
    formula = cash_flows.Range(f"{col}23").Formula
    print(f"  {col}23: Value={val}, Formula={formula[:50] if formula and len(formula) > 50 else formula}")

# 查看 D61
print("\n【D61 - 分母】")
d61 = cash_flows.Range("D61").Value
d61_formula = cash_flows.Range("D61").Formula
print(f"  D61: Value={d61}, Formula={d61_formula}")

# 计算验证
print("\n【计算验证】")
u23 = cash_flows.Range("U23").Value or 0
v23 = cash_flows.Range("V23").Value or 0
w23 = cash_flows.Range("W23").Value or 0
x23 = cash_flows.Range("X23").Value or 0
sum_u_x_23 = u23 + v23 + w23 + x23

print(f"  U23 = {u23:,.2f}")
print(f"  V23 = {v23:,.2f}")
print(f"  W23 = {w23:,.2f}")
print(f"  X23 = {x23:,.2f}")
print(f"  SUM(U23:X23) = {sum_u_x_23:,.2f}")
print(f"  D61 (Cap Rate) = {d61}")
print(f"  Purchase Price = -SUM(U23:X23) / D61 = -{sum_u_x_23:,.2f} / {d61} = {-sum_u_x_23/d61:,.2f}")

# 查看 Row 23 的标签
print("\n【Row 23 是什么?】")
b23 = cash_flows.Range("B23").Value
print(f"  B23 (Label): {b23}")

# 查看更多上下文 - Row 20-30
print("\n【Cash Flows Row 20-30 上下文】")
for row in range(20, 31):
    b_val = cash_flows.Range(f"B{row}").Value
    t_val = cash_flows.Range(f"T{row}").Value
    u_val = cash_flows.Range(f"U{row}").Value
    if b_val:
        print(f"  Row {row}: {b_val}")
        if t_val is not None:
            print(f"    T{row} = {t_val:,.2f if isinstance(t_val, (int, float)) else t_val}")
        if u_val is not None:
            print(f"    U{row} = {u_val:,.2f if isinstance(u_val, (int, float)) else u_val}")

# 看看实际的 EBITDA 计算
print("\n【EBITDA 计算 (Row 48)】")
for col in ['B', 'T', 'U', 'V']:
    val = cash_flows.Range(f"{col}48").Value
    formula = cash_flows.Range(f"{col}48").Formula
    print(f"  {col}48: Value={val}, Formula={formula[:60] if formula else 'N/A'}")

# 看看 Row 48 的构成 (NOI)
print("\n【NOI 构成 (Row 40-50)】")
for row in range(40, 51):
    b_val = cash_flows.Range(f"B{row}").Value
    u_val = cash_flows.Range(f"U{row}").Value
    if b_val:
        print(f"  Row {row} ({b_val}): U{row} = {u_val:,.2f if isinstance(u_val, (int, float)) and u_val else 'N/A'}")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
print("结论: Excel使用 'Gross Income' (Row 23) 的年化值除以 Entry Cap 来计算 Purchase Price")
print("Row 23 应该是 Gross Rental Income (年化)")
print("=" * 80)
