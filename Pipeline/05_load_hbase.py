#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将订单明细数据加载到 HBase agri_order_detail 表
RowKey: user_id_order_date_order_id
列族: base, product, pay
"""

import csv
import subprocess
import sys

def run_hbase_shell(cmds):
    """执行 HBase shell 命令"""
    script = '\n'.join(cmds)
    cmd = f"echo '{script}' | hbase shell -n 2>/dev/null"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)
    return result.stdout

def main():
    print("=" * 50)
    print("开始将订单明细加载到 HBase")
    print("=" * 50)

    # 1. 确保 HBase 表存在
    print("\n1. 检查/创建 HBase 表...")
    result = run_hbase_shell(["list"])
    if 'agri_order_detail' not in result:
        print("  创建 agri_order_detail 表...")
        run_hbase_shell([
            "create 'agri_order_detail', 'base', 'product', 'pay'",
            "exit"
        ])
        print("  ✅ 表创建成功")
    else:
        print("  ✅ 表已存在")

    # 2. 读取订单事实表并写入 HBase
    print("\n2. 加载订单数据到 HBase...")
    fact_file = "/opt/project/agri-ai/data/fact/fact_order.csv"

    count = 0
    batch_cmds = []

    with open(fact_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 构造 RowKey: user_id_order_date_order_id
            user_id = row['user_id']
            order_date = row['order_date']
            order_id = row['order_id']
            rowkey = f"{user_id}_{order_date}_{order_id}"

            # base 列族
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'base:order_id', '{order_id}'"
            batch_cmds.append(put_cmd)
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'base:user_id', '{user_id}'"
            batch_cmds.append(put_cmd)
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'base:order_time', '{row['order_time']}'"
            batch_cmds.append(put_cmd)
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'base:pay_status', '{row['pay_status']}'"
            batch_cmds.append(put_cmd)

            # product 列族
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'product:product_id', '{row['product_id']}'"
            batch_cmds.append(put_cmd)
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'product:quantity', '{row['quantity']}'"
            batch_cmds.append(put_cmd)

            # pay 列族
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'pay:price', '{row['price']}'"
            batch_cmds.append(put_cmd)
            put_cmd = f"put 'agri_order_detail', '{rowkey}', 'pay:sales_amount', '{row['sales_amount']}'"
            batch_cmds.append(put_cmd)

            count += 1

            # 每 100 条批量提交一次
            if len(batch_cmds) >= 800:
                run_hbase_shell(batch_cmds + ["exit"])
                print(f"  已处理 {count} 条订单...")
                batch_cmds = []

    # 剩余数据提交
    if batch_cmds:
        run_hbase_shell(batch_cmds + ["exit"])

    print(f"\n✅ HBase 加载完成！共写入 {count} 条订单明细")
    print("=" * 50)

if __name__ == "__main__":
    main()
