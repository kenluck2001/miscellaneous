import random
import math
from collections import namedtuple
from keccak import Shake128
from bfilter import BloomFilter
 
SEED = 2024

class UltraFilter:

    def __init__(self):
        self.bf = BloomFilter()
        self.settings = self.bf.GetSettings()
        m = self.settings.m
        self.hatbList = [0 for _ in range(m)]

    def SetParam(self, param):
        self.settings = param

    def GetSettings (self):
        return self.settings

    def Insert(self, xText):
        """
            insert element into bit-array for Standard Bloom Filter
        """
        self.bf.Insert(xText)

    def Lookup(self, xText):
        """
            Lookup element from randomized bit-array for UltraFilter
        """
        l = self.settings.l
        hashSize = self.settings.hashSize
        for ind in range(l):
            pos = self.bf.HashFunction(xText, hashSize, ind)
            if not self.hatbList[pos]:
                return False
        return True

    def Randomize(self, epsilon):
        bList = self.bf.GetBitArray()
        m = self.settings.m
        rnd = 1.0 * math.exp(epsilon) / (math.exp(epsilon) + 1)
        probLst = [1 if random.uniform(0, 1) < rnd else 0 for _ in range(m)]
        self.hatbList = [(x * y) for x, y in zip(bList, probLst)]

if __name__ == '__main__':
    bf = UltraFilter()
    bf.Insert("AAA")

    epsilon = 2
    bf.Randomize(epsilon)

    print ("FOUND AAA: {}".format(bf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(bf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(bf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(bf.Lookup("ACB")))

    bf = UltraFilter()
    bf.Insert("AAA")

    epsilon = 4
    bf.Randomize(epsilon)

    print ("FOUND AAA: {}".format(bf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(bf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(bf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(bf.Lookup("ACB")))

    bf = UltraFilter()
    bf.Insert("AAA")

    epsilon = 20
    bf.Randomize(epsilon)

    print ("FOUND AAA: {}".format(bf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(bf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(bf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(bf.Lookup("ACB")))

