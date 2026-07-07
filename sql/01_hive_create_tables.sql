-- ============================================================
-- 智慧农业大数据分析系统 — Hive 数仓建表
-- 文件: sql/01_hive_create_tables.sql
-- 运行: hive -f sql/01_hive_create_tables.sql
-- 或:   beeline -u jdbc:hive2://node01:10000 -n bigdata --silent=true -f sql/01_hive_create_tables.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS agri_dw;
USE agri_dw;

-- ============================================================
-- ODS 层 — 订单原始数据 (外部表, 映射 HDFS /agri/ods/order)
-- ============================================================
DROP TABLE IF EXISTS ods_order;
CREATE EXTERNAL TABLE ods_order (
    order_id      STRING,
    user_id       STRING,
    product_id    STRING,
    product_name  STRING,
    category      STRING,
    province      STRING,
    city          STRING,
    price         DOUBLE,
    quantity      INT,
    sales_amount  DOUBLE,
    order_time    STRING,
    order_date    STRING,
    month_num     INT,
    week_num      INT,
    pay_status    STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/agri/ods/order'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ============================================================
-- DIM 层 — 商品维表 (外部表, 映射 HDFS /agri/dim/product)
-- ============================================================
DROP TABLE IF EXISTS dim_product;
CREATE EXTERNAL TABLE dim_product (
    product_id    STRING,
    product_name  STRING,
    category      STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/agri/dim/product'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ============================================================
-- DIM 层 — 用户维表 (外部表, 映射 HDFS /agri/dim/user)
-- ============================================================
DROP TABLE IF EXISTS dim_user;
CREATE EXTERNAL TABLE dim_user (
    user_id   STRING,
    province  STRING,
    city      STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/agri/dim/user'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ============================================================
-- DWD 层 — 订单事实表 (外部表, 映射 HDFS /agri/dwd/fact_order)
-- ============================================================
DROP TABLE IF EXISTS fact_order;
CREATE EXTERNAL TABLE fact_order (
    order_id      STRING,
    user_id       STRING,
    product_id    STRING,
    price         DOUBLE,
    quantity      INT,
    sales_amount  DOUBLE,
    order_time    STRING,
    order_date    STRING,
    month_num     INT,
    week_num      INT,
    pay_status    STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/agri/dwd/fact_order'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ============================================================
-- 验证
-- ============================================================
SHOW TABLES;
SELECT 'ods_order' AS table_name, COUNT(*) AS row_count FROM ods_order
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_user', COUNT(*) FROM dim_user
UNION ALL
SELECT 'fact_order', COUNT(*) FROM fact_order;
