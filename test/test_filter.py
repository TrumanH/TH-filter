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

server = get_redis(**params)


class TestMethod(unittest.TestCase):
    def test_get_01(self):
        res = server.get("filter:today")
        print(res)
        self.assertTrue(res, msg="Get failed!")


if __name__ == '__main__':
    unittest.main()


"""So far so good 2020/05/17"""