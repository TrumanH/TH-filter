#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : test_filter.py
# Author: Truman He
# Date  : 2020/5/16

"""for unit test 单元测试用"""

import six
import unittest
from connection import params, get_redis
from filter import Filter
from filter.bitmap import Bitmap

""" TDD Practise Plan: 1.Test every key method. 2.Then test a whole typical workflow."""

server = get_redis(**params)


class TestBitmap(unittest.TestCase):
    # run before every case
    def setUp(self):
        pass

    # run after every case
    def tearDown(self):
        bitmap = Bitmap(Filter)
        bitmap.redis.delete("bitmapOfFile0")
        bitmap.redis.delete("bitmap0")

    def test_get_01(self):
        """getbit and setbit"""
        res = server.get("today")
        print("today:", res)
        self.assertTrue(res, msg="Get failed!")
        res = server.setbit('today', 5, 1)
        print("res after setbit:", res)
        bit = server.getbit("today", 5)
        print("bit :", bit)
        self.assertTrue(bit == 1)

    def test_output_02(self):
        filter = Bitmap(Filter).as_filter("bitmap0")  # 12, 6
        output = filter.output("content")
        print("output:", output)
        self.assertTrue(output, msg="Not exist?")

    def test_insert_and_exist_03(self):
        filter = Bitmap(Filter).as_filter("bitmap0", bit=6, hash_number=4)  # 默认12, 6 太大
        filter.insert("content")
        res = filter.exists("content")
        self.assertTrue(res, msg="Inserted but not exist!")

    def test_generateBitmap_04(self):
        bitmap = Bitmap(Filter)
        bitmap.generateBitmap(key="bitmap0", content="content")
        self.assertEqual(bitmap.redis.get("bitmap0"), b"content", msg="Not equal!")

    def test_generateBitmapFromLocal_05(self):
        bitmap = Bitmap(Filter)
        with open("./file0.txt", mode="wb") as f:
            f.write(b"content of file0.")

        bitmap.generateBitmapFromLocal(key_name="bitmapOfFile0", local_file_name="./file0.txt")
        res = bitmap.redis.get("bitmapOfFile0")
        self.assertEqual(res, b"content of file0.", msg="generateBitmapFromLocal faild!")


if __name__ == '__main__':
    unittest.main()     # so far so good, all passed. --2020/7/8

    """
    testunit = unittest.TestSuite(TestFilter("test_get_01"))

    testunit.addTest()
    # testunit.addTest()
    html_file = './result.txt'
    file = open(html_file, mode='wb')

    # HTMLTestRunner 需要单独手动安装
    # runner = HTMLTestRunner.HTMLTestRunner(stream=file, title="report", description=u"result")
    runner = unittest.TextTestRunner(stream=file, descriptions=True)
    runner.run(unittest)
    file.close()
    print("end...")
    """

"""So far so good 2020/05/17"""