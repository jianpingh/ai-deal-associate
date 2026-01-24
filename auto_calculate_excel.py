"""
使用win32com直接操作Excel，确保公式被计算
"""
import sys
sys.path.insert(0, r'backend')

import win32com.client
import os
from deal_agent.nodes.model import get_model_inputs, calculate_simple_metrics
from deal_agent.tools.excel_engine import update_financial_model, write_list_to_excel
from datetime import datetime
import shutil

print("=== 完全自动化的Excel更新流程 ===\n")

# 1. 准备数据
assumptions = {
    "erv": 80,
    "leasable_area": 13604,
    "entry_yield": 6.5,
    "exit_yield": 6.0,
    "rent_growth": 2.0,
    "ltv": 60,
    "interest_rate": 4.5,
    "purchasers_costs": 5.0,
    "hold_period": 7,
    "project_name": "自动计算测试"
}

passing_rent = 900000
inputs = get_model_inputs(assumptions)
metrics = calculate_simple_metrics(inputs, passing_rent_total=passing_rent)
loan_amount = metrics['debug']['loan_amount']

print(f"计算的贷款金额: €{loan_amount:,.0f}")
print()

# 2. 创建输出文件
template_path = os.path.abspath(r'backend/data/templates/MS Canopy Template -v5.xlsx')
output_path = os.path.abspath(r'backend/data/templates/AUTO_CALCULATED.xlsx')

shutil.copy(template_path, output_path)
print(f"已创建输出文件: {output_path}\n")

# 3. 写入数据
tenancy_data = [
    {"name": "Tenant A", "area": 5000, "lease_start": "2023-01-01", "lease_end": "2028-12-31", "current_rent": 400000},
    {"name": "Tenant B", "area": 8604, "lease_start": "2022-06-01", "lease_end": "2027-05-31", "current_rent": 500000},
]

def parse_date(date_str):
    try:
        return datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d")
    except:
        return date_str

rr_rows = [[t["name"], t["area"], parse_date(t["lease_start"]), "", "", parse_date(t["lease_end"]), t["current_rent"]] for t in tenancy_data]

write_list_to_excel.invoke({
    "file_path": output_path,
    "sheet_name": "Input Rent Roll",
    "data": rr_rows,
    "start_row": 2,
    "start_col": 1
})
print("✓ 租金表已写入")

updates = {
    "Input Other!B1": inputs["project_name"],
    "Input Other!B4": inputs["hold_period"],
    "Input Other!B5": inputs["market_rent"],
    "Input Other!B12": inputs["entry_yield"],
    "Input Other!B13": inputs["purchasers_costs"],
    "Input Other!B15": inputs["exit_yield"],
    "Debt Schedule (Bullet)!D10": inputs["interest_rate"],
    "Money Page!E44": loan_amount
}

update_financial_model.invoke({
    "file_path": output_path,
    "updates": updates
})
print("✓ 假设参数已更新")
print()

# 4. 使用COM打开Excel并强制计算
print("正在打开Excel并强制重新计算...")
try:
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # 显示Excel窗口
    excel.DisplayAlerts = False
    
    workbook = excel.Workbooks.Open(output_path)
    
    # 强制完全重新计算
    excel.CalculateFull()
    print("✓ 已执行CalculateFull()")
    
    # 等待计算完成
    import time
    time.sleep(2)
    
    # 读取计算结果
    try:
        cash_flows = workbook.Sheets("Cash Flows")
        equity_invested = cash_flows.Range("C105").Value
        levered_irr = cash_flows.Range("C107").Value
        levered_multiple = cash_flows.Range("C108").Value
        
        print("\n=== Excel计算结果 ===")
        print(f"Equity Invested: €{equity_invested:,.0f}" if equity_invested else "Equity Invested: 未找到")
        print(f"Levered IRR: {levered_irr*100:.2f}%" if levered_irr else "Levered IRR: 未找到")
        print(f"Levered Multiple: {levered_multiple:.2f}x" if levered_multiple else "Levered Multiple: 未找到")
    except Exception as e:
        print(f"读取结果时出错: {e}")
    
    # 保存并关闭
    workbook.Save()
    workbook.Close()
    excel.Quit()
    
    print(f"\n✓ 文件已保存: {output_path}")
    print("\n请打开此文件查看结果！")
    
except Exception as e:
    print(f"❌ Excel操作失败: {e}")
    import traceback
    traceback.print_exc()
