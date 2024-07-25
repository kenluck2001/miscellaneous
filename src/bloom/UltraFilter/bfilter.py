from collections import namedtuple
from keccak import Shake128
SEED = 2024
'''
References
----------
[1] Private Membership Test for Bloom Filters, https://www.utupub.fi/bitstream/handle/10024/156300/07345322.pdf
'''

class BloomFilter:

    def __init__(self):
        Param = namedtuple('Param', ['m', 'n', 'l', 'hashSize'])
        self.settings = Param(1<<24, 1<<20, 10, 128)
        #self.settings = Param(10, 10, 10, 128)
        m = self.settings.m
        self.bList = [0 for _ in range(m)]

    def HashFunction(self, hashTxt, hashSize, ind=-1):
        """
            input:
                hashTxt is alphabetic strings
                hashSize is length in byte
                ind is index
            output:
                output of hash function in (0, m)
        """
        m = self.settings.m
        hashHex = Shake128().update(hashTxt).hexdigest(hashSize) 
        if (ind < 0):
            hashTxtWithIndex = "{}{}".format(hashTxt, ind)
            hashHex = Shake128().update(hashTxtWithIndex).hexdigest(hashSize) 
        hashVal = int(hashHex, 16) % m
        return hashVal

    def SetParam(self, param):
        self.settings = param

    def GetSettings (self):
        return self.settings

    def Insert(self, xText):
        l = self.settings.l
        hashSize = self.settings.hashSize
        for ind in range(l):
            pos = self.HashFunction(xText, hashSize, ind)
            self.bList[pos] = 1

    def Lookup(self, xText):
        l = self.settings.l
        hashSize = self.settings.hashSize
        for ind in range(l):
            pos = self.HashFunction(xText, hashSize, ind)
            if not self.bList[pos]:
                return False
        return True

    def GetBitArray(self):
        return self.bList

if __name__ == '__main__':
    bf = BloomFilter()
    bf.Insert("AAA")

    print ("FOUND AAA: {}".format(bf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(bf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(bf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(bf.Lookup("ACB")))


