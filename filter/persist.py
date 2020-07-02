#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : workflow.py
# Author: Truman He
# Date  : 2020/5/15

import logging
from connection import get_redis, params


# todo:  consider to add compress logic, add more safety process to catch exception ?
# save bitmap to local file 保存(持久化)bitmap到本地文件
def saveBitmap(redis, bitmap_key_name, local_file_name):
    """
    Get redis bitmap and storage into local file
    :param redis: redis client instance
    :param bitmap_key_name: bitmap key name
    :param local_file_name: local file name
    :return:
    """
    try:
        content = redis.get(bitmap_key_name)
        with open(local_file_name, 'w') as f:
            f.write(content.decode())
        return True
    except Exception as e:
        print(e)
        return False


# Get bitmap from local file and set into redis
def getBitmap(redis, local_file_name):
    """
    Get bitmap from local file and set it into redis
    :param redis: redis client instance
    :param local_file_name:  local file name
    :return:
    """
    try:
        with open(local_file_name, 'r') as f:
            content = f.read()
        redis.set(local_file_name, content)
        return True
    except Exception as e:
        print(e)
        return False


# bellow for test
if __name__ == '__main__':
    from connection import get_redis, params
    redis = get_redis(**params)
    with open("bitmap0", "w") as f:
        f.write("test_bitmap's_content")
    getBitmap(redis, "bitmap0")  # set into redis
    print(redis.get("bitmap0"))
    saveBitmap(redis, "bitmap0", "bitmap1")  # storage into local file

    # tested ok 2/27


    
    
    



