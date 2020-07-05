#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : test_filter.py
# Author: Truman He
# Date  : 2020/5/16

"""for unit test 单元测试用"""

import six
import unittest
from connection import params, get_redis
from filter import main


""" TDD Practise Plan: 1.Test every key method. 2.Then test a whole typical workflow."""

server = get_redis(**params)


class TestMethod(unittest.TestCase):
    def test_get_01(self):
        res = server.get("today")
        print(res)
        self.assertTrue(res, msg="Get failed!")
        res = server.setbit(5, 1)
        print(res)
        bit = server.getbit("today", 5)
        self.assertTrue(bit == 1)

    def test_get_02(self):
        pass


if __name__ == '__main__':
    unittest.main()


"""So far so good 2020/05/17"""