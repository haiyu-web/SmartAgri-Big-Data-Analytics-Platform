#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

MYSQL_CONFIG = {
    "host": "192.168.56.101",
    "port": 3306,
    "user": "agri",
    "password": "Agri@123456",
    "database": "agri_ai",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**MYSQL_CONFIG)

def query_list(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()

def query_one(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row
    finally:
        conn.close()

def execute(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
    finally:
        conn.close()
