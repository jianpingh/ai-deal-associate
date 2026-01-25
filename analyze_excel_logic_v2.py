"""
深入分析 MS Canopy Template 的计算逻辑 - 第二部分
"""
import sys
sys.path.insert(0, 'backend')

import win32com.client
import pythoncom
import os
from datetime import datetime

template_path = os.path.abspath('backend/data/templates/MS Canopy Template -v5.xlsx')

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

workbook = excel.Workbooks.Open(template_path, UpdateLinks=False)
excel.CalculateFull()

print("=" * 80)
print("MS Canopy Template 详细计算逻辑")
print("=" * 80)

# 1. Money Page 完整分析
print("\n【Money Page 完整分析】")
money_page = workbook.Sheets("Money Page")

# 关键计算行
mp_cells = [
    ("E29", "Passing Rent Total"),
    ("E30", "Entry Cap Rate (from Input)"),
    ("E31", "Total Investment Cost"),
    ("E32", "Purchasers Costs %"),
    ("E33", "Capex/Closing Costs %"),
    ("E40", "Tax Rate"),
    ("E43", "LTV %"),
    ("E44", "Senior Debt"),
    ("E46", "Upfront Fee %"),
]

for cell, desc in mp_cells:
    val = money_page.Range(cell).Value
    formula = money_page.Range(cell).Formula
    if val is not None:
        print(f"  {cell} ({desc}): Value={val}, Formula={formula}")

# 2. Cash Flows - 分析每个组成部分
print("\n【Cash Flows - 现金流组成分析】")
cash_flows = workbook.Sheets("Cash Flows")

# 获取所有季度的现金流数据
print("\n  === 季度现金流详细数据 ===")

# 列名转换函数
def col_num_to_letter(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

# 收集完整数据
quarters_data = []
col_start = 20  # T = 20

for i in range(41):  # 41个季度
    col_num = col_start + i
    col = col_num_to_letter(col_num)
    
    date_val = cash_flows.Range(f"{col}78").Value
    ebitda = cash_flows.Range(f"{col}80").Value or 0
    interest = cash_flows.Range(f"{col}82").Value or 0
    upfront_fees = cash_flows.Range(f"{col}83").Value or 0
    taxes = cash_flows.Range(f"{col}84").Value or 0
    cf_ops = cash_flows.Range(f"{col}86").Value or 0
    capex = cash_flows.Range(f"{col}88").Value or 0
    disposal = cash_flows.Range(f"{col}90").Value or 0
    acquisition = cash_flows.Range(f"{col}92").Value or 0
    cf_investing = cash_flows.Range(f"{col}94").Value or 0
    debt_issuance = cash_flows.Range(f"{col}96").Value or 0
    debt_repayment = cash_flows.Range(f"{col}97").Value or 0
    cf_financing = cash_flows.Range(f"{col}99").Value or 0
    levered_cf = cash_flows.Range(f"{col}102").Value or 0
    
    quarters_data.append({
        'col': col,
        'date': date_val,
        'ebitda': ebitda,
        'interest': interest,
        'upfront_fees': upfront_fees,
        'taxes': taxes,
        'cf_ops': cf_ops,
        'capex': capex,
        'disposal': disposal,
        'acquisition': acquisition,
        'cf_investing': cf_investing,
        'debt_issuance': debt_issuance,
        'debt_repayment': debt_repayment,
        'cf_financing': cf_financing,
        'levered_cf': levered_cf
    })

# 打印前3个和最后2个季度
print("\n  前3个季度:")
for q in quarters_data[:3]:
    print(f"    {q['col']}: Date={q['date']}")
    print(f"       EBITDA={q['ebitda']:,.0f}, Interest={q['interest']:,.0f}")
    print(f"       CF_Ops={q['cf_ops']:,.0f}, CF_Inv={q['cf_investing']:,.0f}, CF_Fin={q['cf_financing']:,.0f}")
    print(f"       Levered CF={q['levered_cf']:,.0f}")

print("\n  最后2个季度 (包含退出):")
for q in quarters_data[-2:]:
    print(f"    {q['col']}: Date={q['date']}")
    print(f"       EBITDA={q['ebitda']:,.0f}, Interest={q['interest']:,.0f}")
    print(f"       Disposal={q['disposal']:,.0f}, Debt_Repay={q['debt_repayment']:,.0f}")
    print(f"       CF_Ops={q['cf_ops']:,.0f}, CF_Inv={q['cf_investing']:,.0f}, CF_Fin={q['cf_financing']:,.0f}")
    print(f"       Levered CF={q['levered_cf']:,.0f}")

# 3. 汇总验证
print("\n【汇总验证】")
all_levered_cf = [q['levered_cf'] for q in quarters_data]
all_dates = [q['date'] for q in quarters_data]

negative_cf = sum(cf for cf in all_levered_cf if cf < 0)
positive_cf = sum(cf for cf in all_levered_cf if cf > 0)

print(f"  负现金流总和 (投资): €{negative_cf:,.2f}")
print(f"  正现金流总和 (收益): €{positive_cf:,.2f}")
print(f"  净现金流总和: €{sum(all_levered_cf):,.2f}")
print(f"  Equity Multiple (Python): {-positive_cf/negative_cf:.4f}x")

# 4. 提取关键参数用于Python复现
print("\n【关键参数提取 - 用于Python复现】")

# 从 Input Rent Roll 获取租金数据
input_rr = workbook.Sheets("Input Rent Roll")
total_rent = 0
for row in range(2, 20):  # 假设最多18个租户
    rent = input_rr.Range(f"G{row}").Value
    if rent:
        total_rent += rent
print(f"  Total Passing Rent (from Rent Roll): €{total_rent:,.2f}")

# 从 Cash Flows 获取 EBITDA (稳定后)
stable_ebitda = cash_flows.Range("U80").Value  # 第二个季度的EBITDA
print(f"  Quarterly EBITDA (stable): €{stable_ebitda:,.2f}")
print(f"  Annual EBITDA: €{stable_ebitda * 4:,.2f}")

# 利息计算
quarterly_interest = cash_flows.Range("U82").Value
print(f"  Quarterly Interest: €{quarterly_interest:,.2f}")

# 税率
tax_rate = money_page.Range("E40").Value
print(f"  Tax Rate: {tax_rate*100:.2f}%")

# Upfront Fee
upfront_fee_pct = money_page.Range("E46").Value
print(f"  Upfront Fee %: {upfront_fee_pct*100:.2f}%")

# 5. 输出完整的现金流序列用于验证
print("\n【完整现金流序列 (用于XIRR验证)】")
print("dates = [")
for q in quarters_data:
    if q['date']:
        dt = q['date']
        if hasattr(dt, 'strftime'):
            print(f"    datetime({dt.year}, {dt.month}, {dt.day}),")
        else:
            print(f"    # {dt}")
print("]")

print("\ncash_flows = [")
for q in quarters_data:
    print(f"    {q['levered_cf']:.2f},  # {q['col']}")
print("]")

workbook.Close(False)
excel.Quit()
pythoncom.CoUninitialize()

print("\n" + "=" * 80)
