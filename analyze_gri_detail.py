"""
分析 GRI Sheet 的 SUMPRODUCT 公式
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
print("分析 GRI SUMPRODUCT 公式")
print("=" * 80)

gri_sheet = workbook.Sheets("GRI")

# Row 21 formula: =+SUMPRODUCT(R$26:R$421,$C$26:$C$421)
# 这意味着 C列 是系数，R列 是值

print("\n【GRI Sheet 列 C 和 R 的内容 (Row 26 开始)】")
print("  C列是系数 (Lease/Unit indicator), R列是值 (季度租金)")

for row in range(26, 50):
    c_val = gri_sheet.Range(f"C{row}").Value
    r_val = gri_sheet.Range(f"R{row}").Value
    a_val = gri_sheet.Range(f"A{row}").Value
    b_val = gri_sheet.Range(f"B{row}").Value
    
    if c_val or r_val or a_val:
        print(f"  Row {row}: A={a_val}, B={b_val}, C={c_val}, R={r_val}")

# 看看 Column headers
print("\n【GRI Sheet Headers (Row 1-5)】")
for row in range(1, 6):
    for col in ['A', 'B', 'C', 'D', 'R', 'S']:
        val = gri_sheet.Range(f"{col}{row}").Value
        if val:
            print(f"  {col}{row}: {val}")

# 分析 Input Rent Roll 的数据传递
print("\n【Input Rent Roll 详细分析】")
input_rr = workbook.Sheets("Input Rent Roll")

print("  完整租户数据:")
for row in range(1, 10):
    row_data = []
    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        val = input_rr.Range(f"{col}{row}").Value
        row_data.append(str(val) if val else "")
    print(f"    Row {row}: {' | '.join(row_data)}")

# 关键：分析 Cash Flows Row 23 的 GRI
print("\n【Cash Flows Row 23 - GRI 详细】")
cash_flows = workbook.Sheets("Cash Flows")

# U23 = GRI!R21*(U$9<=_Exit)
# 这意味着只有在持有期内才计入

u9 = cash_flows.Range("U9").Value
print(f"  U9 (Quarter Number): {u9}")
print(f"  _Exit Named Range: 检查退出时间")

# 检查 _Exit
try:
    exit_range = workbook.Names("_Exit")
    print(f"  _Exit: {exit_range.Value}")
except:
    print("  _Exit: Not found as named range")

# 更直接：看 Row 9 的值
print("\n  Row 9 (Quarter indicators):")
for col in ['T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC']:
    val = cash_flows.Range(f"{col}9").Value
    print(f"    {col}9: {val}")

# 最关键：确认第二个租户的租金
print("\n【验证租户数据】")
tenant1_rent = input_rr.Range("G2").Value
tenant2_rent = input_rr.Range("G3").Value
print(f"  Tenant 1 (Ingram Micro): €{tenant1_rent:,.2f}")
print(f"  Tenant 2 (CNH Industrial): €{tenant2_rent:,.2f}")
print(f"  Total: €{tenant1_rent + tenant2_rent:,.2f}")
print(f"  ")
print(f"  注意: Tenant 2 租金 €{tenant2_rent:,.2f} = 年化GRI €409,491")
print(f"  季度GRI = €{tenant2_rent/4:,.2f} ≈ Excel显示的 €102,372.75")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
print("结论: Excel的GRI计算可能与租户2的租金 (€409,491) 相关")
print("这可能是因为只有一个租户的租约在当前期间有效")
print("=" * 80)
