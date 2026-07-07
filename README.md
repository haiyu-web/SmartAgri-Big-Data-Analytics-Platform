# 🌾 智慧农业大数据分析与预测系统
*(SmartAgri Big Data Analytics Platform)*

## 📖 项目背景与目标

本项目是一个完整的智慧农业大数据自动化分析系统。以“智慧农业电商平台”为业务背景，打通了从数据生成、清洗、数仓分层、入湖分析、明细存储到智能预测与可视化展示的全链路流程。

通过提取海量农产品订单数据价值，系统不仅能输出多维度的业务指标分析，还能结合大模型生成 AI 经营报告，为农业电商的数字化运营提供底层支撑。

---

## 🛠 技术架构与核心组件

项目融合了目前主流的大数据技术栈及大模型 API：
* **数据开发与采集**：Python
* **分布式存储与协调**：HDFS、HBase、ZooKeeper
* **数仓建模与离线计算**：Hive
* **智能分析与算法**：Spark、通义千问 AI (Qwen)
* **业务数据存储**：MySQL
* **服务接口与前端展现**：FastAPI、ECharts

**系统链路流转图**：
`数据生成 → 清洗 → 数仓分层 → HDFS入湖 → Hive分析 → MySQL入库 → HBase明细存储 → Spark销量预测 → FastAPI接口 → Dashboard可视化 → 通义千问 AI 经营分析报告`

---

## 📈 关键数据统计与业务概况

系统处理并分析了真实的模拟电商业务数据，当前数据概况如下：
* **商品规模**：共 12 种商品（涵盖茶叶 4 种、水果 4 种、干货 4 种）。
* **数据量级**：原始订单 1000 条，经过数据清洗（消除异常/重复/空值）后保留健康订单约 776 条。
* **地域覆盖**：涵盖 6 个主要城市（福州、厦门、泉州、杭州、广州、上海）。
* **时间跨度**：订单数据覆盖 2026-01-01 至 2026-05-31，产出共 148 天的每日销售趋势数据。
* **预测规模**：通过 Spark 输出 12 种商品未来 7 天的销量预测结果（共 84 条）。
* **营收洞察**：在测试数据中，茶叶品类销售额约 88,849 元（占比最高），干货约 25,473 元，水果约 14,035 元。

---

## 📂 核心目录结构

项目分为 Windows 本地开发环境与 Linux 虚拟机部署环境两部分。Linux 核心业务代码位于 `node01` 节点的 `/opt/project/agri-ai/` 目录下：

```text
/opt/project/agri-ai/
├── api/                        # FastAPI 接口代码
│   └── main.py                 # FastAPI 接口入口
├── service/                    # 业务逻辑服务[cite: 2]
│   └── mysql_service.py        # MySQL 查询服务[cite: 1, 2]
├── web/templates/              # 前端页面代码[cite: 2]
│   └── index.html              # Dashboard 可视化页面[cite: 1, 2]
├── pipeline/                   # Python 数据管道脚本 (生成/清洗/入库等)[cite: 1, 2]
│   ├── 01_generate_orders.py   # 数据生成脚本[cite: 2]
│   ├── 02_clean_orders.py      # 数据清洗脚本[cite: 2]
│   └── ...                     
├── spark/                      # Spark & AI 计算脚本[cite: 1, 2]
│   ├── 01_sales_predict.py     # Spark 销量预测脚本[cite: 2]
│   └── 06_qwen_ai_report.py    # 通义千问 AI 报告生成脚本[cite: 1, 2]
├── sql/                        # 数据库建表与分析脚本[cite: 1, 2]
│   ├── 01_hive_create_tables.sql  # Hive 建表[cite: 2]
│   └── ...
├── data/                       # 数据集 (包含 raw/clean/dim/fact)[cite: 1, 2]
└── output/                     # 输出结果目录 (包含 AI 生成的 JSON 报告)[cite: 1, 2]
