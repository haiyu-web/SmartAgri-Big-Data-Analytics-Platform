#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问 (Qwen) AI + MySQL: 智慧农业 AI 经营分析报告生成

使用 requests 直接调用阿里云 DashScope OpenAI兼容接口
无需依赖 openai SDK，兼容 Python 3.6+

API文档: https://help.aliyun.com/zh/model-studio/openai-compatibility

使用方式:
  cd /opt/project/agri-ai
  python3 spark/06_qwen_ai_report.py
"""

import os
import json
import sys
from datetime import date

import pymysql
import requests

# ============================================================
# 阿里云 DashScope 配置
# ============================================================
QWEN_MODEL = "qwen-plus"  # qwen-turbo / qwen-plus / qwen-max
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# ============================================================
# MySQL 配置
# ============================================================
MYSQL_CONFIG = {
    "host": "node01",
    "port": 3306,
    "user": "agri",
    "password": "Agri@123456",
    "database": "agri_ai",
    "charset": "utf8mb4"
}


def get_connection():
    return pymysql.connect(**MYSQL_CONFIG)


def query_all(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def load_sales_data():
    """从 MySQL 读取所有销售分析结果"""
    data = {}

    data["category_sales"] = query_all("""
        SELECT category, total_sales, total_quantity, order_count
        FROM sales_category_result ORDER BY total_sales DESC
    """)

    data["city_sales"] = query_all("""
        SELECT city, total_sales, total_quantity, order_count
        FROM sales_city_result ORDER BY total_sales DESC
    """)

    data["product_top"] = query_all("""
        SELECT product_id, product_name, category, total_sales, total_quantity
        FROM sales_product_top_result ORDER BY total_sales DESC LIMIT 10
    """)

    data["predict_sales"] = query_all("""
        SELECT predict_date, product_id, product_name, category,
               predict_quantity, predict_sales, algorithm
        FROM sales_predict_result ORDER BY predict_sales DESC LIMIT 10
    """)

    return data


def build_prompt(data):
    """根据销售数据构造发送给大模型的 Prompt"""
    category_text = "\n".join([
        "- {}: {}元, {}件, {}单".format(
            row['category'], row['total_sales'],
            row['total_quantity'], row['order_count'])
        for row in data["category_sales"]
    ])

    city_text = "\n".join([
        "- {}: {}元, {}件, {}单".format(
            row['city'], row['total_sales'],
            row['total_quantity'], row['order_count'])
        for row in data["city_sales"]
    ])

    product_text = "\n".join([
        "- {} ({}/{}): {}元, {}件".format(
            row['product_name'], row['product_id'], row['category'],
            row['total_sales'], row['total_quantity'])
        for row in data["product_top"]
    ])

    predict_text = "\n".join([
        "- {} {} ({}/{}): 预测{}件, {}元 [{}]".format(
            row['predict_date'], row['product_name'],
            row['product_id'], row['category'],
            row['predict_quantity'], row['predict_sales'],
            row['algorithm'])
        for row in data["predict_sales"]
    ])

    prompt = """你是智慧农业数据分析顾问。

背景:
这是一个智慧农业大数据项目，系统已完成 HDFS 数据存储、Hive 数据分析、MySQL 结果入库、Spark 销量预测。

任务:
请根据以下销售分析结果和销量预测结果，生成一份经营分析报告。

要求:
1. 不要编造数据。
2. 所有数字必须来自提供的数据。
3. 如果数据不足，请说明数据不足。
4. 报告面向企业管理者。
5. 建议必须具体、可执行。
6. 必须返回纯 JSON，不要返回 Markdown 代码块。
7. 只返回 JSON，不要任何其他文字。
8. JSON 必须包含以下字段:
   - sales_summary: 销售概况总结
   - prediction_summary: 预测结果解读
   - stock_advice: 补货建议
   - marketing_advice: 营销建议
   - risk_warning: 风险提示
   - full_report: 完整报告文本

【品类销售数据】
{category}

【城市销售数据】
{city}

【商品 Top10 数据】
{product}

【Spark 预测数据】
{predict}
""".format(
        category=category_text,
        city=city_text,
        product=product_text,
        predict=predict_text
    )
    return prompt


def call_qwen(prompt):
    """调用阿里云通义千问 API (通过 requests 直接调用)"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError(
            "请先设置环境变量 DASHSCOPE_API_KEY\n"
            "获取 API Key: https://help.aliyun.com/zh/model-studio/get-api-key\n"
            "配置方式: bash pipeline/setup_qwen_env.sh"
        )

    url = DASHSCOPE_BASE_URL + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }

    body = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一名严谨的智慧农业数据分析顾问。你必须基于用户提供的数据分析，不得编造数字。你必须只返回 JSON，不要返回任何其他内容。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2500
    }

    print("  使用模型: " + QWEN_MODEL)
    print("  API 地址: " + url)
    print("  正在调用通义千问 API...")

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120)
    except requests.exceptions.Timeout:
        raise Exception("API 请求超时，请检查网络")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接到 DashScope API，请检查网络")

    if resp.status_code != 200:
        error_info = resp.text[:500]
        raise Exception(
            "API 返回错误 (HTTP {}): {}".format(resp.status_code, error_info)
        )

    result = resp.json()
    content = result["choices"][0]["message"]["content"]

    # Token 使用情况
    usage = result.get("usage", {})
    print("========== Token 使用情况 ==========")
    print("  输入 Token: " + str(usage.get("prompt_tokens", "N/A")))
    print("  输出 Token: " + str(usage.get("completion_tokens", "N/A")))
    print("  总计 Token: " + str(usage.get("total_tokens", "N/A")))

    # 清理可能的 Markdown 代码块标记
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    return json.loads(content)


def save_ai_report(report):
    """将 AI 报告保存到 MySQL"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO ai_decision_report
            (report_date, report_title, sales_summary, prediction_summary,
             stock_advice, marketing_advice, risk_warning, full_report)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (
                date.today(),
                "通义千问({}) 智慧农业 AI 辅助经营决策报告".format(QWEN_MODEL),
                report.get("sales_summary", ""),
                report.get("prediction_summary", ""),
                report.get("stock_advice", ""),
                report.get("marketing_advice", ""),
                report.get("risk_warning", ""),
                report.get("full_report", "")
            ))
        conn.commit()
        print("\n[OK] AI 报告已保存到 MySQL ai_decision_report 表")
    except Exception as e:
        print("\n[ERROR] 保存失败: " + str(e))
        conn.rollback()
    finally:
        conn.close()


def main():
    print("=" * 60)
    print("  通义千问 AI 经营分析报告生成 (模型: {})".format(QWEN_MODEL))
    print("=" * 60)

    # 1. 读取数据
    print("\n[1/4] 读取 MySQL 分析结果...")
    data = load_sales_data()
    print("  品类数据: {} 条".format(len(data['category_sales'])))
    print("  城市数据: {} 条".format(len(data['city_sales'])))
    print("  商品Top10: {} 条".format(len(data['product_top'])))
    print("  预测数据: {} 条".format(len(data['predict_sales'])))

    # 2. 构造 Prompt
    print("\n[2/4] 构造 Prompt...")
    prompt = build_prompt(data)
    print("=" * 40 + " Prompt 预览 " + "=" * 40)
    print(prompt[:600] + "...")
    print("=" * 92)

    # 3. 调用千问
    print("\n[3/4] 调用通义千问 API...")
    try:
        report = call_qwen(prompt)
    except ValueError as e:
        print("\n[ERROR] 配置错误: " + str(e))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print("\n[ERROR] JSON 解析失败: " + str(e))
        print("模型可能返回了非 JSON 格式的内容")
        sys.exit(1)
    except Exception as e:
        print("\n[ERROR] API 调用失败: " + str(e))
        sys.exit(1)

    print("\n" + "=" * 40 + " 千问返回结果 " + "=" * 40)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("=" * 92)

    # 4. 保存结果
    print("\n[4/4] 保存报告...")
    save_ai_report(report)

    # 同时保存本地 JSON 文件
    output_dir = "/opt/project/agri-ai/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = output_dir + "/qwen_ai_report_" + str(date.today()) + ".json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("  报告已保存到: " + output_file)

    print("\n" + "=" * 60)
    print("  通义千问 AI 报告生成完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
