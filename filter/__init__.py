#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : settings.py
# Author: Truman He
# Email : trumanhe0@gmail.com
# Date  : 2020/5/15

from settings import FILTER_BIT, FILTER_HASH_NUMBER

# FILTER_BIT,FILTER_HASH_NUMBER = 12, 6
# bitmap size : 2**FILTER_BIT, number of hash functions(how many times to setbit when insert a new feature): FILTER_HASH_NUMBER
# 如果32，则 2**32 = 4G


# define your HashMap method
class HashMap(object):
    """
    Defines how to insert(method insert) a new feature into bitmap and
    how to judge(method exists) a feature have insert before(already existd)
    """

    def __init__(self, m, seed):
        """
        Initialize a HashMap
        :param m: m = 2 ^ bit ,bitmap's size, max value of offset
        :param seed: type:range,
        """
        self.m = m  # 2**FILTER_BIT ，offset 最大值
        self.seed = seed  # 0~FILTER_HASH_NUMBER

    def hash(self, value):
        """
        Hash Algorithm, could use another algorithm alternatively
        :param value: Value, a feature string,such as: "https://github.com/TrumanH"
        :return: Hash Value, int value,such as: 29778286
        """
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])  # ret每次倍增seed倍后加 ord(value[i])
        return (self.m - 1) & ret  # 按位与(and)运算 ret 到最后一般大于self.m 大千万倍多


class Filter(object):
    def __init__(self, server, key, bit=FILTER_BIT, hash_number=FILTER_HASH_NUMBER):
        """
        Initialize BloomFilter
        :param server: Redis Server
        :param key: Filter Key
        :param bit: m = 2 ^ bit ,bitmap's size
        :param hash_number: the number of hash function, how many time to set bit when insert one feature(map out).
        """
        # default to 1 << 30 = 10,7374,1824 = 2^30 = 128MB, max filter 2^30/hash_number = 1,7895,6970 fingerprints
        self.m = 1 << bit
        self.seeds = range(hash_number)  # FILTER_HASH_NUMBER,default as 6, range(6).
        self.server = server
        self.key = key
        self.maps = [HashMap(self.m, i) for i in self.seeds]  # 多个HashMap:[HashMap(self.m, 0), HashMap(self.m, 1)...]

    @classmethod
    def from_filter(cls, server, key, bit=FILTER_BIT, hash_number=FILTER_HASH_NUMBER):
        """
        Generate a new filter
        :param server: redis server
        :param key: key name
        :param bit:
        :param hash_number:
        :return:
        """
        _filter = cls(server, key, bit, hash_number)
        return _filter

    def exists(self, value):
        """
        if value exists
        :param value: A string feature.
        :return: True or False, self.server.getbit(self.key, offset)只要有一次为False则返回False
        """
        if not value:
            return False
        exist = True
        for map in self.maps:
            offset = map.hash(value)
            # if not self.server.getbit(self.key, offset): return False  # more fast?
            exist = exist & self.server.getbit(self.key, offset)  # True or False
        return exist

    def insert(self, value):
        """
        Insert a new value into (Redis)bitmap, set in置位6次
        :param value: a string feature, eg:"content"
        :return: no return
        """
        for f in self.maps:
            offset = f.hash(value)  # 由映射出的 offset偏置位
            self.server.setbit(self.key, offset, 1)

    def output(self, value):
        """
        Calculate a new value's offsets(number equal to FILTER_HASH_NUMBER)，一个string feature映射出的6个偏置位值
        :param value: fingerprint(a string)
        :return: offsets of a new value would set in
        """
        _offsets = []
        for f in self.maps:
            offset = f.hash(value)
            _offsets.append(offset)
        return _offsets


# import schedule;schedule.every().day.at('17:49').do(job4)

if __name__ == '__main__':
    pass