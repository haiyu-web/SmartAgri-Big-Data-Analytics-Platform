#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接从 CSV 重建 product top 10 并写入 MySQL"""

import csv
import pymysql
from collections import defaultdict

# 加载商品维表
products = {}
with open('/opt/project/agri-ai/data/dim/dim_product.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        products[row['product_id']] = (row['product_name'], row['category'])

# 聚合已支付订单
stats = defaultdict(lambda: {'qty': 0, 'sales': 0.0, 'orders': set()})
fact_count = 0
paid_count = 0
with open('/opt/project/agri-ai/data/fact/fact_order.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        fact_count += 1
        if row['pay_status'] != '已支付':
            continue
        paid_count += 1
        pid = row['product_id']
        stats[pid]['qty'] += int(row['quantity'])
        stats[pid]['sales'] += float(row['sales_amount'])
        stats[pid]['orders'].add(row['order_id'])

print(f'事实表总订单: {fact_count}, 已支付: {paid_count}')
print(f'有已支付订单的产品数: {len(stats)}')

# 按销量排序 Top 10
sorted_prods = sorted(stats.items(), key=lambda x: x[1]['qty'], reverse=True)[:10]

# 写入 MySQL
conn = pymysql.connect(
    host='node01', user='agri', password='Agri@123456',
    database='agri_ai', charset='utf8mb4'
)
c = conn.cursor()
c.execute('DELETE FROM sales_product_top_result')

for rank, (pid, s) in enumerate(sorted_prods, 1):
    pname, cat = products.get(pid, (pid, ''))
    c.execute(
        '''INSERT INTO sales_product_top_result
           (product_id, product_name, category, total_quantity, total_sales, order_count, rank_no)
           VALUES (%s,%s,%s,%s,%s,%s,%s)''',
        (pid, pname, cat, s['qty'], round(s['sales'], 2), len(s['orders']), rank)
    )
conn.commit()

# 验证
c.execute('SELECT rank_no, product_name, category, total_quantity, total_sales, order_count FROM sales_product_top_result ORDER BY rank_no')
print('\n=== 商品销量 Top 10 ===')
for row in c.fetchall():
    print(f"  {row[0]}. {row[1]} ({row[2]}): {row[3]}件, {row[4]}元, {row[5]}单")

conn.close()
print('\nDone!')
