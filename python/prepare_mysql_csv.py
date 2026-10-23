
import pandas as pd
from pathlib import Path

# Locate the project data folder
project_folder = Path(__file__).resolve().parent.parent
input_file = project_folder / "data" / "retail_clean.csv"
output_file = project_folder / "data" / "retail_mysql_ready.csv"

# Read the original CSV
df = pd.read_csv(input_file)

# Convert dates to MySQL-friendly format
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
).dt.strftime("%Y-%m-%d %H:%M:%S")

# Convert Boolean values to 1 and 0
df["IsCancelled"] = df["IsCancelled"].map(
    {True: 1, False: 0}
)
df["IsReturn"] = df["IsReturn"].map(
    {True: 1, False: 0}
)

# Add YearMonth from InvoiceDate
df["YearMonth"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
).dt.strftime("%Y-%m")

# Arrange columns to match the MySQL table
columns = [
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country",
    "Revenue", "IsCancelled", "IsReturn", "YearMonth"
]
df = df[columns]

# Save a new file; keep the original unchanged
df.to_csv(output_file, index=False, date_format="%Y-%m-%d %H:%M:%S")

print("File created successfully!")
print("Output:", output_file)
print("Rows:", len(df))
print("Columns:", df.columns.tolist())
print(df.head(3).to_string(index=False))

