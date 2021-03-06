#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : schema.py
# Author: Truman He
# Date  : 2020/7/19

import os
import schedule
# from connection import get_redis, params
from threading import Thread
from settings import today, history, Expire_days, DirectoryOfLocalFile
from filter.bitmap import Bitmap
from filter import Filter
from six import add_metaclass


# add bitmap attribute(attach to class directly,like classmethod)
class AddBitmap(type):
    def __init__(cls, name, bases, dct):
        setattr(cls, "bitmap", Bitmap(Filter))  # if need change to other bitmap or filter, change this line
        super(AddBitmap, cls).__init__(name, bases, dct)


@add_metaclass(AddBitmap)
class Scheme(object):
    _instance = None

    # 单例模式 Singleton mode
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        """
            初始化函数,如Expire_days为3天,则：
            today, history  # setbit
            history_0, history_1, history_2  # set
        """
        # self.bitmap = Bitmap(Filter)
        # self.redis = get_redis(**params)
        # print("keynames", today, history)
        self.bitmap.generateBitmap(today, "")       # redis.setbit(today, 0, 0) # 在已存在的情况下更安全，不破坏
        self.bitmap.generateBitmap(history, "")     # redis.setbit(history, 0, 0)
        """
        for i in range(Expire_days):   # histroy_1, history_2... 常驻内存方案，不使用
            # ex:过期时间(秒),px:过期时间(毫秒);nx:只在键不存在时才对键进行设置操作，默认false;px:只在键已经存在时才对键进行设置操作，默认false
            self.redis.set(history + "_" + str(i), "", ex=None, px=None, nx=True, xx=False)     # 不存在时才对键进行设置操作
        """
        if Expire_days:
            # Initialize a new thread to do cycle schedule transfer work(blocking mode)
            thread = Thread(target=self.cycle_init)
            print("The cycle job thread:", thread)
            thread.start()
            '''
            schedule.every().minute.do(lambda:print("test transfer")) # only for test
            while True:
                schedule.run_pending()
            '''
        self.today_filter = self.bitmap.as_filter(today)
        self.history_filter = self.bitmap.as_filter(history)

    def cycle_init(self):
        print("In cycle_init: Initialize a new thread to execute cycle job.")
        schedule.every().day.at("00:00").do(self.transfer)
        while True:
            schedule.run_pending()

    def transfer(self):
        """ can be optimize"""
        print("start transfer...")
        historys = [history + "_" + str(i) for i in list(range(1, Expire_days+1))[::-1]]  # 3,2,1
        # 本地文件命名更新(+1)处理 : history_2, history_3,...
        os.chdir(DirectoryOfLocalFile)  # 到文件储存文件夹里
        for file in historys:
            new_name = "history_" + str(int(file.split("_")[-1])+1)
            try:
                os.rename(file, new_name)
            except FileNotFoundError as e:
                print(e, "The Origin File Not Exist?")
        # today bitmap 存为本地文件 history_1
        self.bitmap.saveBitmap(today, "history_1")
        # 创建一个新的 today bitmap
        self.bitmap.generateBitmap(key="today")
        self.bitmap.generateBitmap(key="history_new")
        for key in historys:  # ...history_3, history_2, history_1
            ok = self.bitmap.generateBitmapFromLocal(key_name=key, local_file_name=key) # True of False
            if ok:
                print("bitop or history_new {}".format(key))
                self.bitmap.redis.bitop("OR", "history_new", key)
                self.bitmap.redis.delete(key)

        self.bitmap.redis.rename("history_new", history)  # history_new 将原来history 覆盖掉
        print("done transfer ")

    # not recommend in productive use, only for test
    def _insert(self, feature):
        self.today_filter.insert(feature)
        self.history_filter.insert(feature)

    # not recommend in productive use， only for test
    def _exists(self, feature):
        self.today_filter.exists(feature) or self.history_filter.exists(feature)


if __name__ == '__main__':
    s = Scheme()
    s._insert("content")
    s.transfer()

    # so far so good, finish log on next step... 2020/7/19