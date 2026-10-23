from pathlib import Path
import pandas as pd

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Location of the Excel dataset
DATA_FILE = PROJECT_DIR / "data" / "Online Retail.xlsx"

# Check whether the file exists
if not DATA_FILE.exists():
    print("ERROR: Dataset file not found!")
    print("Expected location:", DATA_FILE)
else:
    print("Dataset found:", DATA_FILE.name)

    # Load the Excel file
    df = pd.read_excel(DATA_FILE)

    # Display basic information
    print("\nDataset loaded successfully!")
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nColumn names:")
    print(df.columns.tolist())

# STEP 4: DATA QUALITY INSPECTION

print("\n" + "=" * 50)
print("DATA QUALITY INSPECTION")
print("=" * 50)

# 1. Check column data types
print("\n1. COLUMN DATA TYPES:")
print(df.dtypes)

# 2. Check missing values
print("\n2. MISSING VALUES:")
print(df.isnull().sum())

# 3. Check duplicate rows
print("\n3. DUPLICATE ROWS:")
print(df.duplicated().sum())

# 4. Check cancelled invoices
print("\n4. CANCELLED INVOICES:")
print(df["InvoiceNo"].astype(str).str.startswith("C").sum())

# 5. Check unusual quantities
print("\n5. ZERO OR NEGATIVE QUANTITIES:")
print((df["Quantity"] <= 0).sum())

# 6. Check zero or negative prices
print("\n6. ZERO OR NEGATIVE UNIT PRICES:")
print((df["UnitPrice"] <= 0).sum())

# 7. Show basic numerical statistics
print("\n7. NUMERICAL SUMMARY:")
print(df[["Quantity", "UnitPrice"]].describe())

print("\nInspection completed successfully!")

# STEP 4.3: CLEAN THE DATASET

print("\n" + "=" * 50)
print("CLEANING THE DATASET")
print("=" * 50)

# Work on a copy; preserve the original DataFrame
clean_df = df.copy()

# 1. Remove exact duplicate rows
before_duplicates = len(clean_df)
clean_df = clean_df.drop_duplicates()
duplicates_removed = before_duplicates - len(clean_df)

# 2. Convert dates into proper datetime values
clean_df["InvoiceDate"] = pd.to_datetime(
    clean_df["InvoiceDate"], errors="coerce"
)

# 3. Convert numeric columns safely
clean_df["Quantity"] = pd.to_numeric(
    clean_df["Quantity"], errors="coerce"
)
clean_df["UnitPrice"] = pd.to_numeric(
    clean_df["UnitPrice"], errors="coerce"
)

# 4. Remove rows with invalid essential transaction values
before_invalid = len(clean_df)

clean_df = clean_df.dropna(
    subset=["InvoiceNo", "StockCode", "InvoiceDate",
            "Quantity", "UnitPrice"]
)

invalid_removed = before_invalid - len(clean_df)

# 5. Create a revenue column
clean_df["Revenue"] = (
    clean_df["Quantity"] * clean_df["UnitPrice"]
)

# 6. Identify cancellations and returns
clean_df["IsCancelled"] = (
    clean_df["InvoiceNo"].astype(str).str.startswith("C")
)

clean_df["IsReturn"] = clean_df["Quantity"] < 0

# 7. Keep a completed-sales dataset separately
# Exclude cancellations, returns, and non-positive quantities/prices
sales_df = clean_df[
    (~clean_df["IsCancelled"])
    & (clean_df["Quantity"] > 0)
    & (clean_df["UnitPrice"] > 0)
].copy()

# 8. Create a monthly analysis column
sales_df["YearMonth"] = (
    sales_df["InvoiceDate"].dt.to_period("M").astype(str)
)

# 9. Save the cleaned transaction data
output_dir = PROJECT_DIR / "data"
output_dir.mkdir(exist_ok=True)

clean_df.to_csv(
    output_dir / "retail_clean.csv", index=False
)

sales_df.to_csv(
    output_dir / "ecommerce_sales_clean.csv", index=False
)

# 10. Print the cleaning summary
print("Original rows:", len(df))
print("Exact duplicates removed:", duplicates_removed)
print("Rows with invalid essential values removed:", invalid_removed)
print("Rows retained for transaction analysis:", len(clean_df))
print("Completed sales rows:", len(sales_df))
print("Total sales revenue:", round(sales_df["Revenue"].sum(), 2))
print("Missing CustomerIDs in sales:", sales_df["CustomerID"].isna().sum())

print("\nSaved files:")
print("data/retail_clean.csv")
print("data/ecommerce_sales_clean.csv")

print("\nCleaning completed successfully!")

# STEP 5: SALES AND CUSTOMER ANALYSIS

print("\n" + "=" * 50)
print("SALES AND CUSTOMER ANALYSIS")
print("=" * 50)

# Create an output folder for analysis results
output_dir = PROJECT_DIR / "data" / "analysis"
output_dir.mkdir(parents=True, exist_ok=True)

# 1. KEY PERFORMANCE INDICATORS (KPIs)
total_revenue = sales_df["Revenue"].sum()
total_orders = sales_df["InvoiceNo"].nunique()
total_customers = sales_df["CustomerID"].nunique()
total_products = sales_df["StockCode"].nunique()
average_order_value = total_revenue / total_orders if total_orders else 0

print("\n1. BUSINESS KPIs")
print("Total Revenue:", round(total_revenue, 2))
print("Total Orders:", total_orders)
print("Unique Customers:", total_customers)
print("Unique Products:", total_products)
print("Average Order Value:", round(average_order_value, 2))

# 2. TOP 10 PRODUCTS BY QUANTITY SOLD
top_products = (
    sales_df.groupby("Description", dropna=True)["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

top_products.to_csv(output_dir / "top_10_products.csv", index=False)

print("\n2. TOP 10 PRODUCTS BY QUANTITY")
print(top_products.to_string(index=False))

# 3. REVENUE BY COUNTRY
country_revenue = (
    sales_df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

country_revenue.to_csv(output_dir / "country_revenue.csv", index=False)

print("\n3. TOP 10 COUNTRIES BY REVENUE")
print(country_revenue.head(10).to_string(index=False))

# 4. MONTHLY REVENUE
monthly_revenue = (
    sales_df.groupby("YearMonth")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("YearMonth")
)

monthly_revenue.to_csv(output_dir / "monthly_revenue.csv", index=False)

print("\n4. MONTHLY REVENUE")
print(monthly_revenue.to_string(index=False))

# 5. TOP 10 CUSTOMERS BY SPENDING
customer_sales = sales_df.dropna(subset=["CustomerID"]).copy()

top_customers = (
    customer_sales.groupby("CustomerID")
    .agg(
        Total_Spending=("Revenue", "sum"),
        Total_Orders=("InvoiceNo", "nunique"),
        Items_Purchased=("Quantity", "sum")
    )
    .sort_values("Total_Spending", ascending=False)
    .head(10)
    .reset_index()
)

top_customers.to_csv(output_dir / "top_10_customers.csv", index=False)

print("\n5. TOP 10 CUSTOMERS BY SPENDING")
print(top_customers.to_string(index=False))

# 6. CUSTOMER PURCHASE FREQUENCY
customer_frequency = (
    customer_sales.groupby("CustomerID")
    .agg(
        Total_Orders=("InvoiceNo", "nunique"),
        Total_Spending=("Revenue", "sum")
    )
    .reset_index()
)

customer_frequency.to_csv(
    output_dir / "customer_purchase_frequency.csv",
    index=False
)

print("\n6. CUSTOMER PURCHASE FREQUENCY")
print(customer_frequency.head(10).to_string(index=False))

print("\nAnalysis completed successfully!")
print("Analysis files saved in:", output_dir)

# STEP 6: DATA VISUALIZATIONS

import matplotlib.pyplot as plt

print("\nCreating charts...")

# Folder for chart images
chart_dir = PROJECT_DIR / "data" / "analysis" / "charts"
chart_dir.mkdir(parents=True, exist_ok=True)

# Chart 1: Top 10 Products by Quantity Sold
plt.figure(figsize=(12, 7))
plt.barh(
    top_products["Description"].astype(str).iloc[::-1],
    top_products["Quantity"].iloc[::-1]
)
plt.title("Top 10 Products by Quantity Sold")
plt.xlabel("Quantity Sold")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig(chart_dir / "top_10_products.png", dpi=150)
plt.close()

# Chart 2: Top 10 Countries by Revenue
top_countries = country_revenue.head(10).sort_values("Revenue")

plt.figure(figsize=(12, 7))
plt.barh(top_countries["Country"], top_countries["Revenue"])
plt.title("Top 10 Countries by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig(chart_dir / "top_10_countries.png", dpi=150)
plt.close()

# Chart 3: Monthly Revenue Trend
plt.figure(figsize=(12, 6))
plt.plot(
    monthly_revenue["YearMonth"],
    monthly_revenue["Revenue"],
    marker="o"
)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(chart_dir / "monthly_revenue_trend.png", dpi=150)
plt.close()

# Chart 4: Top 10 Customers by Spending
top_customers_chart = top_customers.sort_values("Total_Spending")

plt.figure(figsize=(12, 7))
plt.barh(
    top_customers_chart["CustomerID"].astype(str),
    top_customers_chart["Total_Spending"]
)
plt.title("Top 10 Customers by Spending")
plt.xlabel("Total Spending")
plt.ylabel("Customer ID")
plt.tight_layout()
plt.savefig(chart_dir / "top_10_customers.png", dpi=150)
plt.close()

print("\nAll charts created successfully!")
print("Chart location:", chart_dir)
print("1. top_10_products.png")
print("2. top_10_countries.png")
print("3. monthly_revenue_trend.png")
print("4. top_10_customers.png")

import pandas as pd

csv_path = "../data/retail_clean.csv"
check_df = pd.read_csv(csv_path)

print(check_df[["InvoiceDate", "IsCancelled", "IsReturn", "YearMonth"]].head(5).to_string(index=False))
