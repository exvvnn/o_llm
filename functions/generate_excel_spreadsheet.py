from openpyxl import Workbook
import datetime

current_time = datetime.datetime.now()

class ExcelClient:
    
    def __init__(self):
        self.workbook = Workbook()
        self.current_worksheet = self.workbook.active
        self.data_path = f""
        print(f"Client generated at: {current_time}")

    # No returns, takes in a sheet name and filename, and creates a new sheet
    def create_sheet(self, sheet_name, filename):
        self.current_worksheet['A1'] = sheet_name
        self.workbook.save(f"{filename}.xlsx")
        print(f"Spreadsheet generated at: {datetime.datetime.now()}")
        

    # Return string for class
    def __str__(self):
        return f"{self.data_path}"

     