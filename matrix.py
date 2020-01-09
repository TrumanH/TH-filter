
from .filter import 


# 向计数矩阵中偏移位加一
def insert(self, value):
    """
    add value to bloom
    :param value:
    :return:
    """
    for f in self.maps:
        offset = f.hash(value)
        self.matrix.add(self.key, offset, 1)
