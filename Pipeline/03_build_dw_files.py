#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块三：数仓分层文件生成 (ODS/DIM/DWD)
======================================
输入: data/clean/orders_clean.csv
输出:
  data/dim/dim_product.csv   — 商品维表 (product_id, product_name, category)
  data/dim/dim_user.csv      — 用户维表 (user_id, province, city)
  data/fact/fact_order.csv   — 订单事实表 (order_id, user_id, product_id, price,
                               quantity, sales_amount, order_time, order_date,
                               month_num, week_num, pay_status)

为什么分层:
  - 商品信息在订单中重复出现 → 拆成维表统一管理
  - 城市信息属于用户维度 → 通过 user_id 关联
  - 订单事实表只保留购买行为 → 通过 product_id / user_id 关联维表

运行: python3 pipeline/03_build_dw_files.py
"""

import csv
import os


def build_dw_files(clean_file="data/clean/orders_clean.csv"):
    """从清洗后订单拆分为维表和事实表"""

    # 确保目录存在
    for d in ["data/dim", "data/fact"]:
        os.makedirs(d, exist_ok=True)

    # 用于去重的字典
    product_map = {}  # key: product_id
    user_map = {}     # key: user_id
    fact_rows = []

    with open(clean_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_id = row.get("product_id", "")
            user_id = row.get("user_id", "")

            # --- 商品维表去重 ---
            if product_id and product_id not in product_map:
                product_map[product_id] = [
                    product_id,
                    row.get("product_name", ""),
                    row.get("category", "")
                ]

            # --- 用户维表去重 ---
            if user_id and user_id not in user_map:
                user_map[user_id] = [
                    user_id,
                    row.get("province", ""),
                    row.get("city", "")
                ]

            # --- 事实表 (所有订单) ---
            fact_rows.append([
                row.get("order_id", ""),
                user_id,
                product_id,
                row.get("price", ""),
                row.get("quantity", ""),
                row.get("sales_amount", ""),
                row.get("order_time", ""),
                row.get("order_date", ""),
                row.get("month_num", ""),
                row.get("week_num", ""),
                row.get("pay_status", "")
            ])

    # --- 写出商品维表 ---
    with open("data/dim/dim_product.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category"])
        for vals in product_map.values():
            writer.writerow(vals)

    print(f"商品维表: data/dim/dim_product.csv -> {len(product_map)} 种商品")

    # --- 写出用户维表 ---
    with open("data/dim/dim_user.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "province", "city"])
        for vals in user_map.values():
            writer.writerow(vals)

    print(f"用户维表: data/dim/dim_user.csv -> {len(user_map)} 个用户")

    # --- 写出事实表 ---
    fact_header = [
        "order_id", "user_id", "product_id", "price", "quantity",
        "sales_amount", "order_time", "order_date", "month_num",
        "week_num", "pay_status"
    ]

    with open("data/fact/fact_order.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fact_header)
        writer.writerows(fact_rows)

    print(f"事实表: data/fact/fact_order.csv -> {len(fact_rows)} 条订单")

    print("\n数仓分层文件生成完毕!")


if __name__ == "__main__":
    build_dw_files()
