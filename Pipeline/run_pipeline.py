#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧农业大数据 Pipeline 一键调度脚本
"""

import subprocess
import os
import sys
from datetime import datetime

PROJECT_ROOT = "/opt/project/agri-ai"
os.chdir(PROJECT_ROOT)

LOG_FILE = f"/opt/project/agri-ai/logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def run_cmd(cmd, description):
    log(f">> 开始执行: {description}")
    log(f"   命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, universal_newlines=True, timeout=600)
        if result.stdout:
            log(f"   输出: {result.stdout.strip()[:500]}")
        if result.stderr and result.returncode != 0:
            stderr_clean = '\n'.join([l for l in result.stderr.split('\n')
                           if l and 'WARN' not in l and 'SLF4J' not in l and 'INFO' not in l][:10])
            if stderr_clean.strip():
                log(f"   错误: {stderr_clean}")
        if result.returncode != 0:
            log(f"   ❌ 失败: {description} (返回码: {result.returncode})")
            return False
        else:
            log(f"   ✅ 成功: {description}")
            return True
    except subprocess.TimeoutExpired:
        log(f"   ⏱️ 超时: {description}")
        return False
    except Exception as e:
        log(f"   ❌ 异常: {description} - {e}")
        return False

def main():
    log("=" * 60)
    log("智慧农业大数据 Pipeline 启动")
    log("=" * 60)

    steps = [
        ("python3 pipeline/01_generate_orders.py", "1.生成农业订单数据"),
        ("python3 pipeline/02_clean_orders.py", "2.清洗订单数据"),
        ("python3 pipeline/03_build_dw_files.py", "3.构建数仓分层文件"),

        # HDFS 上传
        ("hdfs dfs -mkdir -p /agri/ods/order /agri/dim/product /agri/dim/user /agri/dwd/fact_order",
         "4.创建HDFS目录"),
        ("hdfs dfs -put -f data/clean/orders_clean.csv /agri/ods/order/", "4.1上传ODS"),
        ("hdfs dfs -put -f data/dim/dim_product.csv /agri/dim/product/", "4.2上传商品维表"),
        ("hdfs dfs -put -f data/dim/dim_user.csv /agri/dim/user/", "4.3上传用户维表"),
        ("hdfs dfs -put -f data/fact/fact_order.csv /agri/dwd/fact_order/", "4.4上传事实表"),

        # Hive 建表与分析 (使用 beeline)
        ("beeline -u jdbc:hive2://node01:10000 -n bigdata --silent=true -f sql/01_hive_create_tables.sql",
         "5.Hive建表"),
        ("beeline -u jdbc:hive2://node01:10000 -n bigdata --silent=true -f sql/02_hive_analysis.sql",
         "6.Hive销售分析"),

        # MySQL 建表与导入
        ("mysql -uagri -pAgri@123456 agri_ai < sql/03_mysql_result_tables.sql", "7.1创建MySQL结果表"),
        ("python3 pipeline/04_load_hive_to_mysql.py", "7.2加载Hive结果到MySQL"),

        # HBase
        ("echo \"create 'agri_order_detail', 'base', 'product', 'pay'\" | hbase shell -n 2>/dev/null; echo 'ok'",
         "8.1创建HBase表"),
        ("python3 pipeline/05_load_hbase.py", "8.2加载订单明细到HBase"),

        # Spark 预测
        ("spark-submit --master local[*] spark/01_sales_predict.py", "9.Spark销量预测"),
    ]

    failed = []
    for cmd, desc in steps:
        if not run_cmd(cmd, desc):
            failed.append(desc)

    log("=" * 60)
    if failed:
        log(f"Pipeline 完成，{len(failed)}个步骤失败:")
        for s in failed:
            log(f"  - {s}")
        log(f"日志: {LOG_FILE}")
        sys.exit(1)
    else:
        log("所有步骤执行成功！Pipeline 完成！")
        log(f"日志: {LOG_FILE}")
        sys.exit(0)

if __name__ == "__main__":
    main()
