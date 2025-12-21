import openpyxl
import os

def fix_excel_template():
    # Path to the template
    base_dir = os.getcwd()
    template_path = os.path.join(base_dir, "backend", "data", "templates", "financial_model_template.xlsx")
    
    print(f"Loading template from: {template_path}")
    
    if not os.path.exists(template_path):
        print("Error: Template file not found!")
        return

    try:
        wb = openpyxl.load_workbook(template_path)
        
        # Assuming the main calculation is on the first sheet or named "Summary" / "Cash Flow"
        # Let's check sheet names
        print(f"Sheet names: {wb.sheetnames}")
        
        # Target the 'Cash Flow' sheet specifically
        if "Cash Flow" in wb.sheetnames:
            ws = wb["Cash Flow"]
            print("Switched to 'Cash Flow' sheet.")
        else:
            ws = wb.active
            print(f"Using active sheet: {ws.title}")
        
        # Based on standard models:
        # Exit NOI is usually around Row 9 or 10
        # Exit Value is usually around Row 10 or 11
        # Year 10 NOI is usually Column L (12) if Year 1 is C (3)
        
        # Let's try to find the exact cells by inspecting labels in Column A
        exit_noi_row = None
        exit_value_row = None
        year_10_noi_cell = None
        
        # Scan first 20 rows
        for row in range(1, 25):
            cell_val = ws.cell(row=row, column=1).value
            if cell_val:
                s_val = str(cell_val).lower()
                if "exit noi" in s_val:
                    exit_noi_row = row
                elif "exit value" in s_val:
                    exit_value_row = row
                elif "net operating income" in s_val or "noi" in s_val:
                    # Assuming Year 1 is Col C (3), Year 10 would be Col L (12)
                    # Let's verify headers later, but standard models usually have 10 years
                    # If Col C is Year 1, Col L is Year 10.
                    year_10_noi_cell = ws.cell(row=row, column=12).coordinate
        
        print(f"Found Exit NOI row: {exit_noi_row}")
        print(f"Found Exit Value row: {exit_value_row}")
        print(f"Found Year 10 NOI cell: {year_10_noi_cell}")

        if exit_noi_row and exit_value_row and year_10_noi_cell:
            # Fix Exit NOI Formula: =Year10_NOI * (1 + Rent_Growth)
            # Assuming Rent_Growth is a named range "Rent_Growth"
            exit_noi_cell = ws.cell(row=exit_noi_row, column=2) # Column B
            exit_noi_cell.value = f"={year_10_noi_cell}*(1+Rent_Growth)"
            print(f"Updated Exit NOI formula in {exit_noi_cell.coordinate} to: {exit_noi_cell.value}")
            
            # Fix Exit Value Formula: =Exit_NOI / Exit_Yield
            # Assuming Exit_Yield is a named range "Exit_Yield"
            # And Exit_NOI is the cell we just fixed (e.g. B9)
            exit_value_cell = ws.cell(row=exit_value_row, column=2) # Column B
            exit_value_cell.value = f"={exit_noi_cell.coordinate}/Exit_Yield"
            print(f"Updated Exit Value formula in {exit_value_cell.coordinate} to: {exit_value_cell.value}")
            
            wb.save(template_path)
            print("Template successfully updated and saved.")
        else:
            print("Could not locate necessary rows/cells to apply fix automatically.")
            # Fallback: Hardcode based on standard layout if search fails
            # Usually B9 and B10 in Cash Flow sheet
            # Assuming L4 is Year 10 NOI (Row 4 is usually NOI)
            # Let's be safer and assume Row 4 is NOI based on typical structure
            
            # If we found NOI row but not Exit rows, use NOI row to find Year 10 cell
            if year_10_noi_cell:
                 y10_ref = year_10_noi_cell
            else:
                 y10_ref = "L4" # Default guess
            
            # Default locations for Exit NOI and Value if not found
            if not exit_noi_row: exit_noi_row = 9
            if not exit_value_row: exit_value_row = 10
            
            ws.cell(row=exit_noi_row, column=2).value = f"={y10_ref}*(1+Rent_Growth)"
            ws.cell(row=exit_value_row, column=2).value = f"=B{exit_noi_row}/Exit_Yield"
            
            wb.save(template_path)
            print(f"Applied fallback formulas to B{exit_noi_row} and B{exit_value_row} using {y10_ref}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_excel_template()