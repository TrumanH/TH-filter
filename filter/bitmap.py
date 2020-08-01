#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : workflow.py
# Author: Truman He
# Date  : 2020/5/15

import logging
from connection import get_redis, params
from filter import Filter
from settings import FILTER_BIT, FILTER_HASH_NUMBER
from filter.log import Logger


# 提供其它Filter/Logger选择机会
# Contains all bitmap related operations


class Bitmap(object):
    def __init__(self, filtercls, get_redis_func=get_redis, redis_params=params, settings=None):
        self.filtercls = filtercls  # filtercls.from_filter()
        self.redis = get_redis_func(**redis_params)
        if isinstance(settings, dict) or settings is None:
            # settings = Settings(settings)
            pass

    @property
    def logger(self):
        """self.logger """
        logger = Logger.from_logger("bitmap").get_logger()
        return logger
        # return logging.LoggerAdapter(logger, {"project": self})

    def log(self, message, level = logging.DEBUG, **kw):
        """log 为自定义（推荐） 同时会有定制handler输出到控制台等， self.logger 则为基础全局收集，仅输出到文件"""
        # 定义输出格式
        formatter = logging.Formatter('console: %(asctime)s - %(name)s - %(levelname)s - %(message)s')

        """
        # 另外单独一份仅用于写入文件, 先要(用函数)从模块导入设置参数 到self.attributes
        print("log lever: {}, log file: {}".format(self.attributes["LogLevel"], self.attributes["LogFile"]))
        fh = logging.FileHandler(self.attributes["LogFile"])  # log_file为日志文件路径，eg: './filter.log''
        fh.setLevel(self.attributes["LogLevel"])
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.removeHandler(fh)
        """

        # 同时用于输出到控制台
        console_handler = logging.StreamHandler()
        # consoleHandler.setLevel(self.attributes["LogLevel"])
        console_handler.setLevel(logging.INFO)  # 控制台默认为 INFO 等级
        console_handler.setFormatter(formatter)

        # 给logger add handler ,attach handler to logger.

        self.logger.addHandler(console_handler)
        self.logger.log(level, message, **kw)
        # remember to delete handler after use it
        self.logger.removeHandler(console_handler)

    # 没用
    def generateBitmap(self, key, content="", expire_time=None):
        """
        Genarate a new Bitmap with given contents
        :param key: str, key name .eg: "key_name0"
        :param content: str, content of the key ,eg: "content0"
        :param expire_time: int, sets an expire flag on key ``name`` for ``ex`` seconds., eg: 10
        :return: key_name if success, Exception if exist.
        """
        try:
            self.redis.set(name=key, value=content, nx=True, ex=expire_time)
            self.logger.info("Generate a new bitmap: {}".format(key))
        except Exception as e:
            # print(e)
            self.logger.error("When generate a new bitmap: {}, some thing went wrong!".format(key), e)

    # 持久化，存为本地文件
    def saveBitmap(self, bitmap_key_name, local_file_name):
        """
        Get redis bitmap and storage into local file
        :param redis: redis client instance
        :param bitmap_key_name: bitmap key name
        :param local_file_name: local file name
        :return:
        """
        try:
            content = self.redis.get(bitmap_key_name)
            with open(local_file_name, 'w') as file:
                file.write(content.decode())
            self.logger.info("Save bitmap '{}' into local file'{}'".format(bitmap_key_name, local_file_name))
            return True
        except Exception as e:
            # print(e)
            self.logger.error("When bitmap '{}' into local file'{}', something went wrong!".format(bitmap_key_name, local_file_name), e)
            return False

    # Get bitmap from local file and set into redis
    def generateBitmapFromLocal(self, key_name, local_file_name):
        """
        Get bitmap from local file and set it into redis
        :param key_name: key name of bitmap
        :param local_file_name:  local file
        :return:
        """
        try:
            with open(local_file_name, 'r') as f:
                content = f.read()
            self.redis.set(key_name, content)
            self.logger.info("Set in a bitmap '{}' which contents from local file '{}'".format(key_name, local_file_name))
            return True
        except Exception as e:
            # print(e)
            self.logger.error("When setting in a bitmap '{}' which contents from local '{}', something went wrong".format(key_name, local_file_name), e)
            return False

    def as_filter(self, key, bit=FILTER_BIT, hash_number=FILTER_HASH_NUMBER):
        """
        Generate a new filter from key name
        :param key:
        :param bit:
        :param hash_number:
        :return:
        """
        try:
            _filter = self.filtercls.from_filter(self.redis, key, bit, hash_number)
            self.logger.info("Generate a new filter from key name:'{}'".format(key))
            return _filter
        except Exception as e:
            self.logger.error("When Generating a new filter from key name:'{}', something went wrong!".format(key), e)


# bellow for test
if __name__ == '__main__':
    map = Bitmap(Filter)
    with open("./file0", "w") as f:
        f.write("just a test")
    map.redis.set("bitmap0", "test")
    map.saveBitmap("bitmap0", "./file0")  # storage into local file
    map.logger.info("Storage into local file: bitmap0")
    new_filter = map.as_filter(key="bitmap0", bit=6, hash_number=4)  # 根据传入filtercls转换成对应Filter
    output = new_filter.output("content")
    print(output)
    new_filter.insert("content")   # filter 操作
    res = new_filter.exists("content")
    print(res)
    map.log("log: info test", level=logging.INFO)
    map.log("log: warn test", level=logging.WARNING)
    

# Add log operations, modified and tested, so far so good  -- 2020/8/1
