#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : workflow.py
# Author: Truman He
# Date  : 2020/5/15

import logging
from connection import get_redis, params
# from .main import Filter


# tod:  consider to add compress logic, add more safety process to catch exception ?
#  bitmap 所有主要操作（考虑后面将filter集成进来然后迁移至主模块中？）：生成，持久化到本地保存，获取等

class Bitmap(object):
    def __init__(self):
        self.redis = get_redis(**params)
        # self.logger = from_log() # 继承引入log 功能，并初始化到logger中
        # 通过继承引入 Filter 功能，作为主要工作类？

    # 生成新的 bitmap
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


# bellow for test
if __name__ == '__main__':
    map = Bitmap()
    with open("./file0", "w") as f:
        f.write("just a test")
    print(map.getBitmap("bitmap0"))  # Not exist
    map.saveBitmap("bitmap0", "./file0")  # storage into local file



    
    
    



