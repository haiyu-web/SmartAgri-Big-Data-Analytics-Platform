#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Hive 分析结果表读取数据，写入 MySQL 结果表
"""

import pymysql
import subprocess
import csv
import io

MYSQL_CONFIG = {
    "host": "node01",
    "port": 3306,
    "user": "agri",
    "password": "Agri@123456",
    "database": "agri_ai",
    "charset": "utf8mb4"
}

HIVE_JDBC = "jdbc:hive2://node01:10000"

def beeline_query(sql):
    """通过 beeline 执行 Hive 查询，返回结果行列表"""
    cmd = f"""beeline -u {HIVE_JDBC} -n bigdata --silent=true --outputformat=csv2 -e "{sql}" """
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)
    output = result.stdout.strip()
    lines = [line for line in output.split('\n') if line.strip() and not line.startswith('SLF4J')]
    # 解析 CSV
    rows = []
    if lines:
        reader = csv.DictReader(io.StringIO('\n'.join(lines)))
        for row in reader:
            rows.append(row)
    return rows

def mysql_load(table_name, rows, columns):
    """批量写入 MySQL"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        cursor = conn.cursor()
        # 清空旧数据
        cursor.execute(f"DELETE FROM {table_name}")

        if not rows:
            print(f"  警告: {table_name} 没有数据需要导入")
            return

        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join(columns)
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

        data = []
        for row in rows:
            data.append([row.get(col, None) for col in columns])

        cursor.executemany(sql, data)
        conn.commit()
        print(f"  ✅ {table_name}: 成功导入 {len(data)} 条数据")
    except Exception as e:
        print(f"  ❌ {table_name} 导入失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    print("=" * 50)
    print("开始从 Hive 加载分析结果到 MySQL")
    print("=" * 50)

    # 1. 品类销售
    print("\n1. 加载品类销售数据...")
    rows = beeline_query("USE agri_dw; SELECT * FROM dws_category_sales")
    mysql_load("sales_category_result", rows, ["category", "total_sales", "total_quantity", "order_count"])

    # 2. 商品 Top10
    print("\n2. 加载商品 Top10 数据...")
    rows = beeline_query("USE agri_dw; SELECT * FROM dws_product_top10")
    mysql_load("sales_product_top_result", rows,
              ["product_id", "product_name", "category", "total_quantity", "total_sales", "order_count"])

    # 3. 城市销售
    print("\n3. 加载城市销售数据...")
    rows = beeline_query("USE agri_dw; SELECT * FROM dws_city_sales")
    mysql_load("sales_city_result", rows, ["city", "total_sales", "total_quantity", "order_count"])

    # 4. 每日趋势
    print("\n4. 加载每日销售趋势...")
    rows = beeline_query("USE agri_dw; SELECT * FROM dws_daily_sales")
    mysql_load("sales_daily_result", rows, ["order_date", "total_sales", "total_quantity", "order_count"])

    print("\n" + "=" * 50)
    print("Hive → MySQL 数据导入完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
