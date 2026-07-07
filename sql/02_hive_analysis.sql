-- ============================================================
-- 智慧农业大数据分析系统 — Hive 销售分析 SQL
-- 文件: sql/02_hive_analysis.sql
-- 运行: hive -f sql/02_hive_analysis.sql
-- 或:   beeline -u jdbc:hive2://node01:10000 -n bigdata --silent=true -f sql/02_hive_analysis.sql
-- ============================================================

USE agri_dw;

-- ============================================================
-- 1. 品类销售汇总 (DWS)
-- ============================================================
DROP TABLE IF EXISTS dws_category_sales;
CREATE TABLE dws_category_sales AS
SELECT
    p.category AS category,
    ROUND(SUM(f.sales_amount), 2) AS total_sales,
    SUM(f.quantity) AS total_quantity,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order f
LEFT JOIN dim_product p ON f.product_id = p.product_id
WHERE f.pay_status = '已支付'
GROUP BY p.category;

-- ============================================================
-- 2. 商品销量 Top10 (DWS)
-- ============================================================
DROP TABLE IF EXISTS dws_product_top10;
CREATE TABLE dws_product_top10 AS
SELECT
    f.product_id AS product_id,
    p.product_name AS product_name,
    p.category AS category,
    SUM(f.quantity) AS total_quantity,
    ROUND(SUM(f.sales_amount), 2) AS total_sales,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order f
LEFT JOIN dim_product p ON f.product_id = p.product_id
WHERE f.pay_status = '已支付'
GROUP BY f.product_id, p.product_name, p.category
ORDER BY total_quantity DESC
LIMIT 10;

-- ============================================================
-- 3. 城市销售排行 (DWS)
-- ============================================================
DROP TABLE IF EXISTS dws_city_sales;
CREATE TABLE dws_city_sales AS
SELECT
    u.city AS city,
    ROUND(SUM(f.sales_amount), 2) AS total_sales,
    SUM(f.quantity) AS total_quantity,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order f
LEFT JOIN dim_user u ON f.user_id = u.user_id
WHERE f.pay_status = '已支付'
GROUP BY u.city;

-- ============================================================
-- 4. 每日销售趋势 (DWS)
-- ============================================================
DROP TABLE IF EXISTS dws_daily_sales;
CREATE TABLE dws_daily_sales AS
SELECT
    f.order_date AS order_date,
    ROUND(SUM(f.sales_amount), 2) AS total_sales,
    SUM(f.quantity) AS total_quantity,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order f
WHERE f.pay_status = '已支付'
GROUP BY f.order_date;

-- ============================================================
-- 验证查询
-- ============================================================
SELECT '=== 品类销售 ===' AS info;
SELECT * FROM dws_category_sales;

SELECT '=== 商品 Top10 ===' AS info;
SELECT * FROM dws_product_top10;

SELECT '=== 城市销售 ===' AS info;
SELECT * FROM dws_city_sales;

SELECT '=== 每日趋势 (前10天) ===' AS info;
SELECT * FROM dws_daily_sales LIMIT 10;
