#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : connection.py
# Author: Truman He
# Date  : 2020/5/16

import settings
"""获取Redis客户端连接并返回 Get and return an redis client"""

SETTINGS_PARAMS_MAP = {
    'REDIS_URL': 'url',
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
    'REDIS_ENCODING': 'encoding',
}
# Redis连接类型,Redis连接参数等
redis_cls = settings.REDIS_CLS
params = settings.REDIS_PARAMS.copy()
for source, destination in SETTINGS_PARAMS_MAP.items():
    val = settings.__dict__.get(source)
    if val:
        params[destination] = val

# print(params)  # 上面已经配置好参数，直接用即可


def get_redis(**kwargs):
    """Returns a redis client instance，default use parameters configured above.
    """
    if settings.redis_url:
        return redis_cls.from_url(url=settings.redis_url, **kwargs)
    else:
        return redis_cls(**kwargs)


if __name__ == '__main__':
    client = get_redis(**params)
    res = client.get("filter:today")
    print(type(res), res)  # b'\x04\x80'


"""Tested ok 2020/05/17 """