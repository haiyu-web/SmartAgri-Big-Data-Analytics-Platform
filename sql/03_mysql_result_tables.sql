-- ============================================================
-- 智慧农业大数据分析系统 — MySQL 结果表建表
-- 文件: sql/03_mysql_result_tables.sql
-- 运行: mysql -uagri -pAgri@123456 agri_ai < sql/03_mysql_result_tables.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS agri_ai DEFAULT CHARACTER SET utf8mb4;
USE agri_ai;

-- 1. 品类销售结果表
CREATE TABLE IF NOT EXISTS sales_category_result (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    category       VARCHAR(100),
    total_sales    DECIMAL(18,2),
    total_quantity BIGINT,
    order_count    BIGINT,
    update_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='品类销售分析结果';

-- 2. 商品 Top10 结果表
CREATE TABLE IF NOT EXISTS sales_product_top_result (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    product_id     VARCHAR(50),
    product_name   VARCHAR(200),
    category       VARCHAR(100),
    total_quantity BIGINT,
    total_sales    DECIMAL(18,2),
    order_count    BIGINT,
    rank_no        INT,
    update_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品销量Top10结果';

-- 3. 城市销售结果表
CREATE TABLE IF NOT EXISTS sales_city_result (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    city           VARCHAR(100),
    total_sales    DECIMAL(18,2),
    total_quantity BIGINT,
    order_count    BIGINT,
    update_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='城市销售排行结果';

-- 4. 每日销售趋势结果表
CREATE TABLE IF NOT EXISTS sales_daily_result (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    order_date     DATE,
    total_sales    DECIMAL(18,2),
    total_quantity BIGINT,
    order_count    BIGINT,
    update_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日销售趋势结果';

-- 5. 销量预测结果表
CREATE TABLE IF NOT EXISTS sales_predict_result (
    id               INT PRIMARY KEY AUTO_INCREMENT,
    predict_date     DATE,
    product_id       VARCHAR(50),
    product_name     VARCHAR(200),
    category         VARCHAR(100),
    predict_quantity INT,
    predict_sales    DECIMAL(18,2),
    algorithm        VARCHAR(100),
    update_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Spark销量预测结果';

-- 验证
SHOW TABLES;
