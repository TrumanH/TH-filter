#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : log.py
# Author: Truman He
# Date  : 2020/7/6

import os
import six
import settings
from importlib import import_module
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)-s - %(levelname)-s - %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=settings.LogFile,
                    filemode='a'  # 追加模式，'w' 则覆盖写
                    )


class Logger(object):
    def __init__(self, log_name):
        self.logger = logging.getLogger(log_name)
        self.frozen = False
        self.attributes = {}
        self.setmodule("settings")

        # 用于写入文件
        print("log lever: {}, log file: {}".format(self.attributes["LogLevel"], self.attributes["LogFile"]))
        fh = logging.FileHandler(self.attributes["LogFile"])  # log_file为日志文件路径，eg: './filter.log''
        fh.setLevel(self.attributes["LogLevel"])

        # 用于输出到控制台
        console_handler = logging.StreamHandler()
        # consoleHandler.setLevel(self.attributes["LogLevel"])
        console_handler.setLevel(logging.INFO)  # 控制台默认为 INFO 等级
        # 定义输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # 给logger 添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

    @classmethod
    def from_logger(cls, log_name="test"):
        return cls(log_name)

    def set(self, name, value):
        self.attributes[name] = value

    # 从指定模块导入(日志)设置
    def setmodule(self, module):
        """
        Store settings from a module
        This is a helper function
        :param module: the module or the path of the module
        :type module: module object or string
        """
        self._assert_mutability()
        if isinstance(module, six.string_types):
            module = import_module(module)
        for key in dir(module):
            # if key.isupper():
            if key.startswith('Log'):
                self.set(key, getattr(module, key))  # 'LogLevel', 'LogFile'

    def _assert_mutability(self):
        if self.frozen:
            raise TypeError("Trying to modify an immutable Settings object")


if __name__ == '__main__':
    l = Logger.from_logger("test")
    logger = l.get_logger()
    logger.setLevel(logging.DEBUG)
    logger.debug("Just a test--2020/7/6")
    # logger.warn("why")
    logger.info("info")

    # so far so good 2020/7/6













