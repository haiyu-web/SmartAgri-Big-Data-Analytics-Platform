import csv
import random
from datetime import datetime, timedelta
import os

# --- 1. 基础维度数据定义 ---
# 商品库 (product_id, product_name, category, base_price) - 12种商品
PRODUCTS = [
    ("p001", "武夷岩茶", "茶叶", 199.00),
    ("p002", "安溪铁观音", "茶叶", 150.00),
    ("p003", "平和蜜柚", "水果", 35.50),
    ("p004", "漳州蕉", "水果", 20.00),
    ("p005", "古田银耳", "干货", 68.00),
    ("p006", "莆田桂圆干", "干货", 45.00),
    ("p007", "福鼎白茶", "茶叶", 180.00),
    ("p008", "永春芦柑", "水果", 28.00),
    ("p009", "闽北香菇", "干货", 55.00),
    ("p010", "福州茉莉花茶", "茶叶", 120.00),
    ("p011", "厦门芒果干", "干货", 38.00),
    ("p012", "漳州荔枝", "水果", 42.00)
]

# 城市库 (province, city)
CITIES = [
    ("福建省", "福州"), ("福建省", "厦门"), ("福建省", "泉州"),
    ("浙江省", "杭州"), ("广东省", "广州"), ("上海市", "上海")
]

# 支付状态与概率控制
STATUS_LIST = ["已支付", "已支付", "已支付", "已支付", "未支付", "已退款"]


# --- 2. 核心生成逻辑 ---
def generate_orders(num_records=1000, output_file="data/raw/orders_raw.csv"):
    start_date = datetime(2026, 1, 1)

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "user_id", "product_id", "product_name",
                         "category", "province", "city", "price", "quantity",
                         "order_time", "pay_status"])

        for i in range(1, num_records + 1):
            random_days = random.randint(0, 150)
            random_seconds = random.randint(0, 86400)
            order_time = start_date + timedelta(days=random_days, seconds=random_seconds)

            product = random.choice(PRODUCTS)
            location = random.choice(CITIES)

            order_id = f"{order_time.strftime('%Y%m%d')}{str(i).zfill(5)}"
            user_id = f"u{str(random.randint(1, 200)).zfill(4)}"
            product_id, product_name, category, price = product
            province, city = location

            # 偶尔制造异常数据用于清洗实训
            if random.random() < 0.02:
                price = -10.0
            quantity = random.randint(0, 5) if random.random() > 0.01 else -1

            pay_status = random.choice(STATUS_LIST)

            writer.writerow([order_id, user_id, product_id, product_name,
                             category, province, city, f"{price:.2f}", quantity,
                             order_time.strftime("%Y-%m-%d %H:%M:%S"), pay_status])

    print(f"成功生成 {num_records} 条原始订单数据(12种商品)，已保存至 {output_file}")


if __name__ == "__main__":
    generate_orders(1000, "data/raw/orders_raw.csv")
