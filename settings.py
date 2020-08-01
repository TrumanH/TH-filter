#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : settings.py
# Author: Truman He
# Email : trumanhe0@gmail.com
# Date  : 2020/5/15

import os
import redis
import logging

""" Redis连接配置 filter bitmap参数设置等 基本所有(默认)设置均在此文件中定义"""

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# 指定redis数据库的连接参数
redis_url = ''
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
# 指定redis 连接类型 type of redis client
REDIS_CLS = redis.StrictRedis
REDIS_PARAMS = {
    'db': 0,
    # 'password': '',  # 服务器的redis对应密码
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
}


# PIPELINE_KEY = '%(spider)s:items'
# 默认 HashMap个数，由一个feature 映射出来的offset个数
FILTER_HASH_NUMBER = 6
# 决定bitmap大小：size = 2 ** FILTER_BIT
FILTER_BIT = 30

DUPEFILTER_DEBUG = False

# key name of today's bitmap, history's bitmap
today = "today"
history = "history"

# 过期时间(单位：天)，默认为零，代表不采用过期策略。
# expire days(in days), default as 0, means not adopt expire strategy.
Expire_days = 3

# 日志相关设置
# 设置日志等级，从低到高依次为： DEBUG, INFO, WARNING, ERROR, CRITICAL
LogLevel = logging.DEBUG

LogFile = os.path.join(PROJECT_ROOT, './log/', 'filter.log')

# 本地bitmap文件存储文件夹 to storage transfer local file
DirectoryOfLocalFile = "D://BaiduNetdiskDownload//temp"

if __name__ == '__main__':
    print(PROJECT_ROOT, LogFile)
    logging.basicConfig(level=LogLevel, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename=LogFile,filemode='a')
    logger = logging.getLogger('test')
    logger = logging.LoggerAdapter(logger, {'user': 'user0'})
    logger.info("First log for test!")
    try:
        result = 10 / 0  # 此处执行一条非法的语法
    except Exception:
        logger.error('Error content', exc_info=True)

    # so far so good --2020/7/6