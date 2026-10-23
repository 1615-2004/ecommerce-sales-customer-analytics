import pandas as pd
from pathlib import Path
import mysql.connector
from getpass import getpass

project_folder = Path(__file__).resolve().parent.parent
output_folder = project_folder / "data" / "sql_exports"
output_folder.mkdir(parents=True, exist_ok=True)

password = getpass("Enter your MySQL password: ")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="ecommerce_analytics"
)

queries = {
    "monthly_revenue": """
        SELECT
            YearMonth,
            ROUND(SUM(Revenue), 2) AS monthly_revenue,
            COUNT(DISTINCT InvoiceNo) AS total_orders
        FROM ecommerce_sales
        WHERE IsCancelled = 0 AND IsReturn = 0
        GROUP BY YearMonth
        ORDER BY YearMonth
    """,

    "monthly_product_revenue": """
        SELECT
            YearMonth,
            StockCode,
            Description,
            ROUND(SUM(Revenue), 2) AS total_revenue
        FROM ecommerce_sales
        WHERE IsCancelled = 0
          AND IsReturn = 0
          AND StockCode NOT IN ('POST', 'DOT', 'M')
        GROUP BY YearMonth, StockCode, Description
        ORDER BY YearMonth, total_revenue DESC
    """,

    "top_products": """
        SELECT
            StockCode,
            Description,
            ROUND(SUM(Revenue), 2) AS total_revenue,
            SUM(Quantity) AS units_sold
        FROM ecommerce_sales
        WHERE IsCancelled = 0 AND IsReturn = 0
        GROUP BY StockCode, Description
        ORDER BY total_revenue DESC
        LIMIT 10
    """,

    "top_customers": """
        SELECT
            CustomerID,
            ROUND(SUM(Revenue), 2) AS total_revenue,
            COUNT(DISTINCT InvoiceNo) AS total_orders
        FROM ecommerce_sales
        WHERE IsCancelled = 0
          AND IsReturn = 0
          AND CustomerID IS NOT NULL
          AND CustomerID <> 0
        GROUP BY CustomerID
        ORDER BY total_revenue DESC
        LIMIT 10
    """
}

try:
    for name, query in queries.items():
        df = pd.read_sql(query, conn)
        path = output_folder / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"Saved: {path} ({len(df)} rows)")

    print("All exports completed successfully!")

finally:
    conn.close()
