import csv
from openpyxl import Workbook
from openpyxl.styles import Alignment
from logger import log


def write_csv(rows, csv_file):
    log("Writing CSV")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def write_excel(rows, excel_file):
    log("Generating Excel")

    wb = Workbook()
    ws = wb.active
    ws.title = "Bitbucket Inventory"

    headers = list(rows[0].keys())
    ws.append(headers)

    for row in rows:
        ws.append(list(row.values()))

    wrap_columns = {
        "branches", "protected_branches", "tags", "releases",
        "users_access", "repo_tokens", "pipelines", "webhooks"
    }

    for col_idx, col_name in enumerate(headers, start=1):
        if col_name in wrap_columns:
            for col in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                for cell in col:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(excel_file)
