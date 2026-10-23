
USE ecommerce_analytics;

-- 1. Total revenue
SELECT ROUND(SUM(Revenue), 2) AS total_revenue
FROM ecommerce_sales
WHERE IsCancelled = 0 AND IsReturn = 0;

-- 2. Total unique orders
SELECT COUNT(DISTINCT InvoiceNo) AS total_orders
FROM ecommerce_sales
WHERE IsCancelled = 0 AND IsReturn = 0;

-- 3. Total unique customers (exclude missing/invalid IDs)
SELECT COUNT(DISTINCT CustomerID) AS total_customers
FROM ecommerce_sales
WHERE IsCancelled = 0
  AND IsReturn = 0
  AND CustomerID IS NOT NULL
  AND CustomerID <> 0;

-- 4. Top 10 products by revenue
SELECT StockCode, Description,
       ROUND(SUM(Revenue), 2) AS total_revenue,
       SUM(Quantity) AS units_sold
FROM ecommerce_sales
WHERE IsCancelled = 0 AND IsReturn = 0
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;

-- 5. Monthly revenue trend
SELECT YearMonth,
       ROUND(SUM(Revenue), 2) AS monthly_revenue,
       COUNT(DISTINCT InvoiceNo) AS total_orders
FROM ecommerce_sales
WHERE IsCancelled = 0 AND IsReturn = 0
GROUP BY YearMonth
ORDER BY YearMonth;

-- 6. Top 10 customers (exclude invalid IDs)
SELECT CustomerID,
       ROUND(SUM(Revenue), 2) AS total_revenue,
       COUNT(DISTINCT InvoiceNo) AS total_orders
FROM ecommerce_sales
WHERE IsCancelled = 0
  AND IsReturn = 0
  AND CustomerID IS NOT NULL
  AND CustomerID <> 0
GROUP BY CustomerID
ORDER BY total_revenue DESC
LIMIT 10;

-- Monthly revenue by product for Power BI
SELECT
    YearMonth,
    StockCode,
    Description,
    SUM(Revenue) AS total_revenue
FROM ecommerce_sales
WHERE IsCancelled = 0
  AND IsReturn = 0
  AND StockCode NOT IN ('POST', 'DOT', 'M')
GROUP BY
    YearMonth,
    StockCode,
    Description
ORDER BY
    YearMonth,
    total_revenue DESC;

