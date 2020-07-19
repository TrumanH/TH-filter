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


# 基础默认设置
logging.basicConfig(level=logging.DEBUG,
                    format='glob: %(asctime)s - %(name)-s - %(levelname)-s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename=settings.LogFile,
                    filemode='a',  # 追加模式，'w' 则覆盖写
                    )


class Logger(object):
    def __init__(self, log_name):
        self.logger = logging.getLogger(log_name)
        self.frozen = False
        self.attributes = {}
        self.setmodule("settings")

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
    logger.debug("Just a test--2020/7/6")
    # logger.warn("why")
    logger.info("info")

    # so far so good 2020/7/6













