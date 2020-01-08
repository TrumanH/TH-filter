from .setting import FILTER_BIT,FILTER_HASH_NUMBER

# define your HashMap method
class HashMap(object):
    def __init__(self, m, seed):
        self.m = m
        self.seed = seed
    
    def hash(self, value):
        """
        Hash Algorithm, could use another alternatively
        :param value: Value
        :return: Hash Value
        """
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.m - 1) & ret


class Filter(object):
    def __init__(self, server, key, bit=FILTER_BIT, hash_number=FILTER_HASH_NUMBER):
        """
        Initialize BloomFilter
        :param server: Redis Server
        :param key: Filter Key
        :param bit: m = 2 ^ bit ,bitmap's size
        :param hash_number: the number of hash function, how many time setbit when insert one feature(map out).
        """
        # default to 1 << 30 = 10,7374,1824 = 2^30 = 128MB, max filter 2^30/hash_number = 1,7895,6970 fingerprints
        self.m = 1 << bit
        self.seeds = range(hash_number)
        self.server = server
        self.key = key
        self.maps = [HashMap(self.m, seed) for seed in self.seeds]
    
    def exists(self, value):
        """
        if value exists
        :param value:
        :return:
        """
        if not value:
            return False
        exist = True
        for map in self.maps:
            offset = map.hash(value)
            exist = exist & self.server.getbit(self.key, offset)
        return exist
    
    def insert(self, value):
        """
        add value to bloom
        :param value:
        :return:
        """
        for f in self.maps:
            offset = f.hash(value)
            self.server.setbit(self.key, offset, 1)
