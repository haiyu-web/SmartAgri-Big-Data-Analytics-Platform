#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块二：订单数据清洗
====================
输入: data/raw/orders_raw.csv
输出: data/clean/orders_clean.csv

清洗规则:
  1. 核心字段 (order_id, user_id, product_id) 不能为空
  2. 订单去重 (按 order_id)
  3. 过滤异常价格 (price <= 0) 和异常数量 (quantity <= 0)
  4. 解析订单时间，提取 order_date, month_num, week_num
  5. 计算销售额: sales_amount = price * quantity
  6. 仅保留已支付订单参与后续分析统计 (pay_status = '已支付')

运行: python3 pipeline/02_clean_orders.py
"""

import csv
import os
from datetime import datetime

# 输入输出路径
INPUT_FILE = "data/raw/orders_raw.csv"
OUTPUT_FILE = "data/clean/orders_clean.csv"


def clean_orders(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """清洗订单数据"""

    seen_order_ids = set()
    clean_rows = []
    total_count = 0
    empty_count = 0
    dup_count = 0
    bad_value_count = 0

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_count += 1

            # --- 1. 核心字段不能为空 ---
            order_id = row.get("order_id", "").strip()
            user_id = row.get("user_id", "").strip()
            product_id = row.get("product_id", "").strip()
            if not order_id or not user_id or not product_id:
                empty_count += 1
                continue

            # --- 2. 按 order_id 去重 ---
            if order_id in seen_order_ids:
                dup_count += 1
                continue
            seen_order_ids.add(order_id)

            # --- 3. 过滤异常 price 和 quantity ---
            try:
                price = float(row.get("price", 0))
                quantity = int(row.get("quantity", 0))
            except (ValueError, TypeError):
                bad_value_count += 1
                continue

            if price <= 0 or quantity <= 0:
                bad_value_count += 1
                continue

            # --- 4. 解析订单时间 ---
            order_time_str = row.get("order_time", "").strip()
            try:
                order_time = datetime.strptime(order_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                bad_value_count += 1
                continue

            order_date = order_time.strftime("%Y-%m-%d")
            month_num = order_time.month
            week_num = order_time.isocalendar()[1]  # ISO 周数

            # --- 5. 计算销售额 ---
            sales_amount = round(price * quantity, 2)

            # --- 6. 构造清洗后的行 ---
            clean_rows.append({
                "order_id": order_id,
                "user_id": user_id,
                "product_id": product_id,
                "product_name": row.get("product_name", ""),
                "category": row.get("category", ""),
                "province": row.get("province", ""),
                "city": row.get("city", ""),
                "price": f"{price:.2f}",
                "quantity": str(quantity),
                "sales_amount": f"{sales_amount:.2f}",
                "order_time": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order_date": order_date,
                "month_num": str(month_num),
                "week_num": str(week_num),
                "pay_status": row.get("pay_status", "")
            })

    # --- 写出清洗结果 ---
    fieldnames = [
        "order_id", "user_id", "product_id", "product_name", "category",
        "province", "city", "price", "quantity", "sales_amount",
        "order_time", "order_date", "month_num", "week_num", "pay_status"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    # --- 统计输出 ---
    print(f"清洗完成:")
    print(f"  原始订单: {total_count} 条")
    print(f"  空值过滤: {empty_count} 条")
    print(f"  重复过滤: {dup_count} 条")
    print(f"  异常值过滤: {bad_value_count} 条")
    print(f"  清洗后: {len(clean_rows)} 条")
    print(f"  输出文件: {output_file}")
    print(f"  新增字段: sales_amount, order_date, month_num, week_num")


if __name__ == "__main__":
    clean_orders()
