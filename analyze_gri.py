"""
深入分析 Excel GRI (Gross Rental Income) 的来源
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
print("分析 Excel GRI (Gross Rental Income) 的来源")
print("=" * 80)

# GRI Sheet
print("\n【GRI Sheet 分析】")
try:
    gri_sheet = workbook.Sheets("GRI")
    
    # Row 21 是关键 (因为 Cash Flows U23 = GRI!R21)
    print("\n  GRI Row 21 (关键行):")
    for col in ['A', 'B', 'C', 'D', 'R', 'S', 'T', 'U']:
        val = gri_sheet.Range(f"{col}21").Value
        formula = gri_sheet.Range(f"{col}21").Formula
        print(f"    {col}21: Value={val}, Formula={formula[:50] if formula and len(str(formula)) > 50 else formula}")
    
    # 看看整个 GRI 的结构
    print("\n  GRI Sheet 结构 (Row 1-25, Col A-D):")
    for row in range(1, 26):
        a_val = gri_sheet.Range(f"A{row}").Value
        if a_val:
            print(f"    Row {row}: {a_val}")

except Exception as e:
    print(f"  Error: {e}")

# Input Rent Roll
print("\n【Input Rent Roll 分析】")
input_rr = workbook.Sheets("Input Rent Roll")

print("  租金表内容:")
total_rent = 0
for row in range(1, 15):
    a_val = input_rr.Range(f"A{row}").Value
    g_val = input_rr.Range(f"G{row}").Value
    if a_val or g_val:
        print(f"    Row {row}: Tenant={a_val}, Rent={g_val}")
        if g_val and isinstance(g_val, (int, float)):
            total_rent += g_val
print(f"  Total Rent from Input: €{total_rent:,.2f}")

# Cash Flows EBITDA 来源
print("\n【Cash Flows EBITDA 来源】")
cash_flows = workbook.Sheets("Cash Flows")

# T48 是 EBITDA
print("\n  EBITDA (Row 48):")
print(f"    T48 Formula: {cash_flows.Range('T48').Formula}")
print(f"    U48 Formula: {cash_flows.Range('U48').Formula}")
print(f"    U48 Value: {cash_flows.Range('U48').Value}")

# 追溯 Row 48 引用的行
print("\n  EBITDA 相关行 (Row 40-50, Col U):")
for row in range(40, 51):
    label = cash_flows.Range(f"B{row}").Value
    val = cash_flows.Range(f"U{row}").Value
    formula = cash_flows.Range(f"U{row}").Formula
    if label or val:
        print(f"    Row {row} ({label}): U={val}, Formula={formula[:40] if formula else 'N/A'}")

# Money Page 关键数据
print("\n【Money Page 总结】")
money_page = workbook.Sheets("Money Page")

mp_data = {
    "E30 (Entry Cap)": money_page.Range("E30").Value,
    "E31 (TIC)": money_page.Range("E31").Value,
    "E43 (LTV)": money_page.Range("E43").Value,
    "E44 (Senior Debt)": money_page.Range("E44").Value,
}

for key, val in mp_data.items():
    print(f"  {key}: {val}")

# 关键计算验证
print("\n【关键计算验证】")
tic = mp_data["E31 (TIC)"]
ltv = mp_data["E43 (LTV)"]
senior_debt = mp_data["E44 (Senior Debt)"]
equity = tic - senior_debt

print(f"  TIC: €{tic:,.2f}")
print(f"  LTV: {ltv*100:.0f}%")
print(f"  Senior Debt = TIC × LTV = €{tic:,.2f} × {ltv} = €{tic * ltv:,.2f}")
print(f"  Actual Senior Debt: €{senior_debt:,.2f}")
print(f"  Equity = TIC - Debt = €{tic:,.2f} - €{senior_debt:,.2f} = €{equity:,.2f}")

# Excel的计算关系
print("\n【Excel计算关系总结】")
print(f"  1. Input Rent Roll Total: €{total_rent:,.2f}")
print(f"  2. GRI Row 21 (季度): €102,372.75")
print(f"  3. 年化GRI = 4季度 = €409,491")
print(f"  4. Purchase Price = 年化GRI / Entry Cap = €409,491 / 0.065 = €{409491/0.065:,.2f}")
print(f"  5. TIC ≈ Purchase Price (实际TIC: €{tic:,.2f})")
print(f"  ")
print(f"  关键比率: GRI年化 / Input Rent = €409,491 / €{total_rent:,.2f} = {409491/total_rent:.4f}")
print(f"  ")
print(f"  这意味着 GRI = Input Rent × {409491/total_rent:.4f}")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
