import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import os

def create_underwriting_template():
    # Ensure directory exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "data", "templates")
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, "financial_model_template.xlsx")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Inputs"
    
    # Setup labels and initial values
    data = [
        ("Parameter", "Value", "Named Range"),
        ("Market Rent (EUR/sqm)", 100, "Market_Rent"),
        ("Exit Yield (%)", 0.05, "Exit_Yield"),
        ("CPI Growth (%)", 0.02, "CPI_Growth"),
        ("Purchase Price", 5000000, "Purchase_Price"),
        ("Cap Rate", 0.06, "Cap_Rate")
    ]
    
    for row_idx, row_data in enumerate(data, 1):
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)
            
    # Create Named Ranges
    # Market_Rent -> B2
    wb.create_named_range("Market_Rent", ws, "$B$2")
    # Exit_Yield -> B3
    wb.create_named_range("Exit_Yield", ws, "$B$3")
    # CPI_Growth -> B4
    wb.create_named_range("CPI_Growth", ws, "$B$4")
    
    # Add some formatting
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 20
    
    print(f"Creating template at: {file_path}")
    wb.save(file_path)
    print("Template created successfully with named ranges: Market_Rent, Exit_Yield, CPI_Growth")

if __name__ == "__main__":
    create_underwriting_template()
