#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : workflow.py
# Author: Truman He
# Date  : 2020/5/15

"""
上层的工作流程（过期策略），详细逻辑可见README.md
"""

import schedule
from connection import get_redis, params
from settings import today, history, expire_days  # "today", "history", 3

# 根据settings 中的连接参数建立redis连接 db0
redis = get_redis(**params)


def workflow():
    schedule.every().day.at("00:00").do(daily_transfer)


def initailize():
    """
    初始化函数,如expire_days为3天,则：
    today, history  # setbit
    history_0, history_1, history_2  # set
    """
    print("keynames", today, history)
    redis.set(today, "")   # redis.setbit(today, 0, 0) # 在已存在的情况下更安全，不破坏
    redis.set(history, "")  # redis.setbit(history, 0, 0)
    for i in range(expire_days):
        # ex:过期时间(秒),px:过期时间(毫秒);nx:只在键不存在时才对键进行设置操作，默认false;px:只在键已经存在时才对键进行设置操作，默认false
        redis.set(history+"_"+str(i), "", ex=None, px=None, nx=False, xx=False)
    # for i in range(expire_days):
    #     redis.setbit(history+"_"+str(i), 0, 0)


def daily_transfer():
    """
    每天00：00 所有 bitmap一次周期性大更新
    today : 今天bitmap
    history : 历史bitmap
    :return:
    """
    # 一天前变为2天前，2天前变为3天前,逆序操作...
    historys = [history+"_"+str(i) for i in list(range(expire_days))[::-1]]  # history_0, history_1, history_2...
    for i in list(range(expire_days-1))[::-1]:  # 1,0
        redis.rename(historys[i], historys[i+1])  # 1->2, 0->1
        # 初步合并出 history_new, 后面再将history_0 合并进来
        redis.bitop("OR", history+"_new", historys[i+1])

    # todo:或者省内存占用改为从硬盘中直接加载2天前,3天前... persist.getBitmap

    # 今天的复制为一天前
    redis.rename(today, history+"_0")
    # 新初始化今天的bitmap 不存在才设置,在生产setbit则中不存在则创建，已存在也会setbit
    redis.set(today, '', nx=True)   # 只在键不存在时才设置 由setbit先一步创建的话,此句可能不会执行
    redis.bitop("OR", history+"_new", history+"_0")  # 将最新的history_0 合并进history_new
    redis.rename(history+"_new", history)   # 新的history替换掉旧的

    # todo: persist.saveBitmap将内存中history_0,history_1...硬盘持久化(+1更名)存储为 history_1,history_2...?
    # 实际上只用将内存中history_0 持久化到硬盘中为history_1 (之前先将硬盘中history_1,history_2等全部+1更名)
    # 然后从redis 中删除history_0,history_1...


""" # bitop 函数源码 doc：
bitop(self, operation, dest, *keys)
Perform a bitwise operation using ``operation`` between ``keys`` and
store the result in ``dest``.
"""

# for test
if __name__ == '__main__':
    # 测试 initailze函数
    initailize()
    redis.setbit(history+"_1", 1, 1)
    L = []
    history is not None and L.append(history+"_new")
    # redis.set("history_new", "")
    redis.bitop('OR', "history_new", "histroy_0", "history_1", "history_2")
    # redis.execute_command("BITOP", "OR", "history_new", "histroy_0", "history_1", "history_2")
    # redis.save()
    print(L)
    for key in ["today", "history", "history_new", "history_0", "history_1", "history_2"]:
        redis.delete(key)


