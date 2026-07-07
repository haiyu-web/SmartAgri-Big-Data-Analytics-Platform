#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spark 销量预测 (PySpark 版)
============================
功能:
  1. 从 HDFS 读取订单事实表 (fact_order.csv)
  2. 过滤已支付订单
  3. 按 (product_id, order_date) 聚合销量和销售额
  4. 计算历史日均值 + 趋势
  5. 生成未来 7 天预测
  6. 写入 MySQL sales_predict_result 表

运行: spark-submit --master local[*] spark/01_sales_predict.py
"""

import random
from datetime import datetime, timedelta

import pymysql
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, countDistinct

# ============================================================
# 配置
# ============================================================
MYSQL_CONFIG = {
    "host": "node01",
    "port": 3306,
    "user": "agri",
    "password": "Agri@123456",
    "database": "agri_ai",
    "charset": "utf8mb4"
}

HDFS_FACT = "/agri/dwd/fact_order/fact_order.csv"
HDFS_DIM = "/agri/dim/product/dim_product.csv"
PREDICT_DAYS = 7
LAST_DATE = datetime(2026, 5, 31)


def main():
    print("=" * 60)
    print("  Spark 销量预测 (PySpark)")
    print("=" * 60)

    # --- 1. 创建 SparkSession ---
    spark = SparkSession.builder \
        .appName("agri-sales-predict") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    try:
        # --- 2. 读取 HDFS 数据 ---
        print("\n[1/5] 读取 HDFS 订单事实表...")
        fact_df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(HDFS_FACT)

        print(f"  总行数: {fact_df.count()}")
        print(f"  列: {fact_df.columns}")

        # --- 3. 过滤已支付订单 + 类型转换 ---
        print("\n[2/5] 过滤已支付订单...")
        paid_df = fact_df \
            .filter(col("pay_status") == "已支付") \
            .withColumn("quantity", col("quantity").cast("int")) \
            .withColumn("sales_amount", col("sales_amount").cast("double"))

        paid_count = paid_df.count()
        print(f"  已支付订单: {paid_count} 条")

        # --- 4. 按商品 + 日期聚合 ---
        print("\n[3/5] 按商品+日期聚合...")
        daily_agg = paid_df.groupBy("product_id", "order_date").agg(
            spark_sum("quantity").alias("daily_qty"),
            spark_sum("sales_amount").alias("daily_sales")
        )
        # 收集到 Python 本地计算预测 (数据量小, 收集到 driver 安全)
        daily_rows = daily_agg.orderBy("product_id", "order_date").collect()
        print(f"  聚合后: {len(daily_rows)} 条 (商品×日期)")

        # --- 读取商品维表 (获取 product_name, category) ---
        print("\n  读取商品维表...")
        dim_df = spark.read \
            .option("header", "true") \
            .csv(HDFS_DIM)
        dim_rows = dim_df.collect()
        product_info = {}
        for row in dim_rows:
            pid = row["product_id"].strip() if row["product_id"] else ""
            pname = row["product_name"].strip() if row["product_name"] else pid
            cat = row["category"].strip() if row["category"] else ""
            if pid:
                product_info[pid] = (pname, cat)
        print(f"  商品数: {len(product_info)}")

        # --- 5. 计算预测 ---
        print("\n[4/5] 计算未来 {} 天预测...".format(PREDICT_DAYS))
        predictions = compute_predictions(daily_rows, product_info)

        # --- 6. 写入 MySQL ---
        print("\n[5/5] 写入 MySQL...")
        save_to_mysql(predictions)

        # --- 预览 ---
        print("\n  预览 (每种商品第一条):")
        shown = set()
        for p in predictions:
            if p["product_id"] not in shown:
                shown.add(p["product_id"])
                print("    {} ({}): {} -> {}件, {}元 [{}]".format(
                    p['product_name'], p['category'],
                    p['predict_date'], p['predict_quantity'],
                    p['predict_sales'], p['algorithm']))

    finally:
        spark.stop()

    print("\n" + "=" * 60)
    print("  销量预测完成!")
    print("=" * 60)


def compute_predictions(daily_rows, product_info):
    """基于 Spark 聚合结果计算预测值 (Python 本地计算)"""
    # 组织数据: { product_id: { date: {qty, sales} } }
    daily = {}
    for row in daily_rows:
        pid = row["product_id"].strip()
        odate = row["order_date"].strip()
        qty = int(row["daily_qty"])
        sales = float(row["daily_sales"])

        if pid not in daily:
            daily[pid] = {}
        daily[pid][odate] = {"qty": qty, "sales": sales}

    # 确保所有商品都在 product_info 中
    for pid in daily:
        if pid not in product_info:
            product_info[pid] = (pid, "")

    # 计算预测
    predictions = []
    random.seed(42)

    for pid, date_map in daily.items():
        pname, cat = product_info.get(pid, (pid, ""))

        dates = sorted(date_map.keys())
        daily_qtys = [date_map[d]["qty"] for d in dates]
        daily_sales_vals = [date_map[d]["sales"] for d in dates]

        avg_qty = sum(daily_qtys) / len(daily_qtys)
        avg_sales = sum(daily_sales_vals) / len(daily_sales_vals)

        # 趋势计算
        mid = len(daily_qtys) // 2
        if mid > 0 and len(daily_qtys) > 2:
            earlier_avg = sum(daily_qtys[:mid]) / mid
            later_avg = sum(daily_qtys[mid:]) / (len(daily_qtys) - mid)
            trend = (later_avg - earlier_avg) / max(earlier_avg, 1)
        else:
            trend = 0.0

        # 预测未来 7 天
        for day_offset in range(1, PREDICT_DAYS + 1):
            pred_date = (LAST_DATE + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            trend_factor = 1.0 + trend * (day_offset / PREDICT_DAYS)
            noise = 1.0 + random.uniform(-0.15, 0.15)

            pred_qty = round(avg_qty * trend_factor * noise)
            pred_sales = round(avg_sales * trend_factor * noise, 2)

            if pred_qty < 1:
                pred_qty = 1
            if pred_sales < avg_sales * 0.5:
                pred_sales = round(avg_sales * 0.5, 2)

            algo = "trend+noise" if abs(trend) > 0.05 else "avg+noise"

            predictions.append({
                "predict_date": pred_date,
                "product_id": pid,
                "product_name": pname,
                "category": cat,
                "predict_quantity": pred_qty,
                "predict_sales": pred_sales,
                "algorithm": algo
            })

    return predictions


def save_to_mysql(predictions):
    """写入 MySQL sales_predict_result 表"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        with conn.cursor() as c:
            c.execute("DELETE FROM sales_predict_result")
            sql = """INSERT INTO sales_predict_result
                     (predict_date, product_id, product_name, category,
                      predict_quantity, predict_sales, algorithm)
                     VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            for p in predictions:
                c.execute(sql, (
                    p["predict_date"], p["product_id"],
                    p["product_name"], p["category"],
                    p["predict_quantity"], p["predict_sales"],
                    p["algorithm"]
                ))
        conn.commit()
        print(f"  写入成功: {len(predictions)} 条预测记录")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
