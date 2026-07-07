CREATE TABLE IF NOT EXISTS ai_decision_report (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'report id',
    report_date DATE COMMENT 'report date',
    report_title VARCHAR(200) COMMENT 'report title',
    sales_summary TEXT COMMENT 'sales summary',
    prediction_summary TEXT COMMENT 'prediction summary',
    stock_advice TEXT COMMENT 'stock advice',
    marketing_advice TEXT COMMENT 'marketing advice',
    risk_warning TEXT COMMENT 'risk warning',
    full_report LONGTEXT COMMENT 'full ai report',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'create time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI decision report table';
