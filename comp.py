import sys
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import copy


# ---------------------------------------------------------
# APPLY STYLE FUNCTION
# ---------------------------------------------------------

def apply_style(path):

    wb = load_workbook(path)

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for ws in wb.worksheets:

        # Set column width
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = 18

        # Apply borders
        for row in ws.iter_rows(min_row=1,
                                max_row=ws.max_row,
                                min_col=1,
                                max_col=ws.max_column):
            for cell in row:
                cell.border = thin_border

    wb.save(path)


# ---------------------------------------------------------
# UPDATE EXECUTION REPORT FUNCTION
# ---------------------------------------------------------

def update_execution_report(path, BuildNumber, Trigger, Iteration):

    # Load execution sheet using pandas
    execution_report_data = pd.read_excel(path, sheet_name="Sheet1")

    current_date = datetime.today().strftime("%Y-%m-%d")

    if current_date not in execution_report_data.columns:
        raise ValueError(f"{current_date} column not found in Sheet1")

    # ---------------------------------------------------------
    # CALCULATE METRICS
    # ---------------------------------------------------------

    total_ts = len(execution_report_data[current_date].dropna())

    passed_ts = len(
        execution_report_data[
            execution_report_data[current_date].astype(str).str.startswith('Pass')
        ]
    )

    failed_ts = len(
        execution_report_data[
            execution_report_data[current_date].astype(str).str.startswith('Fail')
        ]
    )

    verification_ts = len(
        execution_report_data[
            execution_report_data[current_date].astype(str).str.startswith('VERI')
        ]
    )

    not_executed_ts = len(
        execution_report_data[
            execution_report_data[current_date].astype(str).str.startswith('Not')
        ]
    )

    # ---------------------------------------------------------
    # OPEN SUMMARY SHEET USING OPENPYXL
    # ---------------------------------------------------------

    wb = load_workbook(path)
    ws_summary = wb["Summary"]

    # Find next empty column
    next_col = ws_summary.max_column + 1

    # ---------------------------------------------------------
    # WRITE DATA INTO FIXED ROW STRUCTURE
    # ---------------------------------------------------------

    ws_summary.cell(row=1, column=next_col).value = current_date
    ws_summary.cell(row=2, column=next_col).value = BuildNumber
    ws_summary.cell(row=3, column=next_col).value = Trigger
    ws_summary.cell(row=4, column=next_col).value = Iteration

    # Row 5 = KITE Tool Version (kept as existing structure)

    ws_summary.cell(row=6, column=next_col).value = total_ts
    ws_summary.cell(row=7, column=next_col).value = passed_ts
    ws_summary.cell(row=8, column=next_col).value = failed_ts
    ws_summary.cell(row=9, column=next_col).value = verification_ts
    ws_summary.cell(row=10, column=next_col).value = not_executed_ts

    wb.save(path)

    # Apply formatting
    apply_style(path)


# ---------------------------------------------------------
# OPTIONAL: MAIN EXECUTION (Example Usage)
# ---------------------------------------------------------

if __name__ == "__main__":

    file_path = "your_excel_file.xlsx"

    BuildNumber = "BuildNumber_1234"
    Trigger = "02:06:21"
    Iteration = "IdNu"

    update_execution_report(file_path, BuildNumber, Trigger, Iteration)

    print("Execution report updated successfully.")
