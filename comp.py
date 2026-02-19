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

        # Apply border
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

    # ---------------------------------------------------------
    # LOAD SHEET1 USING PANDAS
    # ---------------------------------------------------------

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
    ws = wb["Summary"]

    # Determine next empty column
    next_col = ws.max_column + 1
    prev_col = ws.max_column   # Used for copying format

    # ---------------------------------------------------------
    # WRITE VALUES DIRECTLY (NO DICTIONARY)
    # ---------------------------------------------------------

    ws.cell(row=1, column=next_col).value = current_date
    ws.cell(row=2, column=next_col).value = BuildNumber
    ws.cell(row=3, column=next_col).value = Trigger
    ws.cell(row=4, column=next_col).value = Iteration

    # Row 5 = KITE Tool Version (already exists in structure)

    ws.cell(row=6, column=next_col).value = total_ts
    ws.cell(row=7, column=next_col).value = passed_ts
    ws.cell(row=8, column=next_col).value = failed_ts
    ws.cell(row=9, column=next_col).value = verification_ts
    ws.cell(row=10, column=next_col).value = not_executed_ts

    # ---------------------------------------------------------
    # COPY FORMATTING FROM PREVIOUS COLUMN
    # ---------------------------------------------------------

    for row in range(1, 11):

        old_cell = ws.cell(row=row, column=prev_col)
        new_cell = ws.cell(row=row, column=next_col)

        if old_cell.has_style:
            new_cell.font = copy.copy(old_cell.font)
            new_cell.border = copy.copy(old_cell.border)
            new_cell.fill = copy.copy(old_cell.fill)
            new_cell.number_format = copy.copy(old_cell.number_format)
            new_cell.protection = copy.copy(old_cell.protection)
            new_cell.alignment = copy.copy(old_cell.alignment)

    wb.save(path)

    apply_style(path)
