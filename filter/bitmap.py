#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : workflow.py
# Author: Truman He
# Date  : 2020/5/15

# import redis
import logging
from connection import get_redis, params
from filter import Filter
# from functools import update_wrapper
from settings import FILTER_BIT, FILTER_HASH_NUMBER
from filter.log import Logger


# tod:  consider to add compress logic, add more safety process to catch exception ?
#  bitmap 所有主要操作（考虑后面将filter集成进来然后迁移至主模块中？）：生成，持久化到本地保存，获取等
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
        logger = Logger.from_logger("bitmap").get_logger()
        return logger
        # return logging.LoggerAdapter(logger, {"project": self})

    def log(self, message, level = logging.DEBUG, **kw):
        self.logger.log(level, message, **kw)

    def genarateBitmap(self, key, content, expire_time=None):
        """
        Genarate a new Bitmap with given contents
        :param key: str, key name .eg: "key_name0"
        :param content: str, content of the key ,eg: "content0"
        :param expire_time: int, sets an expire flag on key ``name`` for ``ex`` seconds., eg: 10
        :return: key_name if success, Exception if exist.
        """
        try:
            self.redis.set(name=key, value=content,ex=expire_time)
        except Exception as e:
            print(e)

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
            with open(local_file_name, 'w') as f:
                f.write(content.decode())
            return True
        except Exception as e:
            print(e)
            return False

    def getBitmap(self, key):
        """
        Get bitmap from Redis with given key name
        :param key: key name, str
        :return: content of key
        """
        return self.redis.get(name=key)

    # Get bitmap from local file and set into redis
    def getBitmapFromLocal(self, local_file_name):
        """
        Get bitmap from local file and set it into redis
        :param redis: redis client instance
        :param local_file_name:  local file name
        :return:
        """
        try:
            with open(local_file_name, 'r') as f:
                content = f.read()
            self.redis.set(local_file_name, content)
            return True
        except Exception as e:
            print(e)
            return False

    def as_filter(self, key, bit=FILTER_BIT, hash_number=FILTER_HASH_NUMBER):
        """
        Generate a new filter from key name
        :param key:
        :param bit:
        :param hash_number:
        :return:
        """
        _filter = self.filtercls.from_filter(self.redis, key, bit, hash_number)
        return _filter


# bellow for test
if __name__ == '__main__':
    map = Bitmap(Filter)
    with open("./file0", "w") as f:
        f.write("just a test")
    map.redis.set("bitmap0", "test")
    print(map.getBitmap("bitmap0"))  # Not exist
    map.saveBitmap("bitmap0", "./file0")  # storage into local file
    map.logger.info("Storage into local file: bitmap0")
    new_filter = map.as_filter(key="bitmap0", bit=6, hash_number=4)
    new_filter.insert("content")
    print(map.getBitmap("bitmap0"))
    

# so far so good  -- 2020/7/6
