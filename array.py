import numpy as np
from .filter import FILTER_BIT,FILTER_HASH_NUMBER

# eg: output = [12, 1023, 265, 435, 687, 9] ,当FILTER_BIT,FILTER_HASH_NUMBER = 10, 6
# 先实现，再优化：expire_array使用更节省空间的方式存储？
"""
expire_array = np.zeros(2**FILTER_BIT, dtype=np.int8)
tatol_array = np.zeros(2**FILTER_BIT, dtype=np.int8)
"""
# server = 

def recordInto(output:list):
    """
    Add a new list(of offsets) into record array and tatol array.
    :param output: A FILTER_HASH_NUMBER long list contains offsets
    :return: 
    """
    expire_array = server.get_expire_array()  # todo: define
    tatol_array = server.get_tatol_array()
    for i in output:
        expire_array[i] += 1
        tatol_array[i] += 1

# 
def expireOperate():
    tatol_array = server.get_tatol_array()
    expire_array = server.get_expire_array()
    tatol_array = tatol_array - expire_array
    server.save_tatol_array(tatol_array)
    



