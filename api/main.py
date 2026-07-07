#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 本地 FastAPI 入口
启动: uvicorn api.main:app --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from service.mysql_service import query_list, query_one

app = FastAPI(title='智慧农业大数据分析系统 API', version='1.0')
templates = Jinja2Templates(directory='web/templates')

def success(data=None, message='success'):
    return {'code': 200, 'message': message, 'data': data}

def fail(message='error', data=None):
    return {'code': 500, 'message': message, 'data': data}

# ========== 服务首页 ==========
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# ========== 基础接口 ==========
@app.get('/api/v1/hello')
def hello():
    return success('智慧农业大数据项目接口启动成功')

@app.get('/api/v1/project/info')
def project_info():
    return success({
        'project_name': '智慧农业大数据自动化分析系统',
        'version': '1.0',
        'run_env': 'Linux node01',
        'technology': ['Python', 'FastAPI', 'MySQL', 'Hive', 'HBase', 'Spark', 'HDFS', 'HTML', 'JavaScript']
    })

@app.get('/api/v1/project/status')
def project_status():
    return success({'api': 'running', 'mysql': 'ready', 'frontend': 'ready'})

# ========== 品类销售接口 ==========
@app.get('/api/v1/dashboard/category')
def get_category_sales():
    try:
        sql = '''
        SELECT category, total_sales, total_quantity, order_count
        FROM sales_category_result
        ORDER BY total_sales DESC
        '''
        rows = query_list(sql)
        return success(rows)
    except Exception as e:
        return fail(str(e))

# ========== 商品 Top10 接口 ==========
@app.get('/api/v1/dashboard/product-top')
def get_product_top():
    try:
        sql = '''
        SELECT product_id, product_name, category, total_quantity, total_sales, order_count, rank_no
        FROM sales_product_top_result
        ORDER BY rank_no ASC
        '''
        rows = query_list(sql)
        return success(rows)
    except Exception as e:
        return fail(str(e))

# ========== 城市销售接口 ==========
@app.get('/api/v1/dashboard/city')
def get_city_sales():
    try:
        sql = '''
        SELECT city, total_sales, total_quantity, order_count
        FROM sales_city_result
        ORDER BY total_sales DESC
        '''
        rows = query_list(sql)
        return success(rows)
    except Exception as e:
        return fail(str(e))

# ========== 每日趋势接口 ==========
@app.get('/api/v1/dashboard/daily')
def get_daily_sales():
    try:
        sql = '''
        SELECT order_date, total_sales, total_quantity, order_count
        FROM sales_daily_result
        ORDER BY order_date ASC
        '''
        rows = query_list(sql)
        return success(rows)
    except Exception as e:
        return fail(str(e))

# ========== 销量预测接口 ==========
@app.get('/api/v1/dashboard/predict')
def get_predict_sales():
    try:
        sql = '''
        SELECT predict_date, product_id, product_name, category, predict_quantity, predict_sales, algorithm
        FROM sales_predict_result
        ORDER BY predict_date ASC
        '''
        rows = query_list(sql)
        return success(rows)
    except Exception as e:
        return fail(str(e))

# ========== AI 报告接口 ==========
@app.get('/api/v1/dashboard/ai-report')
def get_ai_report():
    try:
        sql = '''
        SELECT id, report_date, report_title, sales_summary, prediction_summary,
               stock_advice, marketing_advice, risk_warning, created_time
        FROM ai_decision_report
        ORDER BY id DESC LIMIT 1
        '''
        row = query_one(sql)
        return success(row)
    except Exception as e:
        return fail(str(e))
