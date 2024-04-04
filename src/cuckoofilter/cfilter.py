from collections import namedtuple
from keccak import Shake128
import random

'''
References
----------
[1] Cuckoo Filter: Practically Better Than Bloom, https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf
[2] The Dynamic Cuckoo Filter, https://cis.temple.edu/~wu/research/publications/Publication_files/Chen_ICNP_2017.pdf
[3] Cuckoo Hashing, https://www.brics.dk/RS/01/32/BRICS-RS-01-32.pdf
'''

BYTE_SIZE = 8
SEED = 2024
EMPTY = '_'

class CuckooFilter:

    def __init__(self):
        Param = namedtuple('Param', ['m', 'n', 'l', 'hashSize'])
        self.settings = Param(1<<24, 1<<20, 10, 128)
        #self.settings = Param(10, 10, 10, 128)
        m = self.settings.m
        self.bucket = [EMPTY for _ in range(m)]

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

    def Fingerprint(self, hashTxt):
        """
            input:
                hashTxt is alphabetic strings
            output:
                output of hash function in decimal
        """
        hashSize= len(hashTxt) * BYTE_SIZE
        hashHex = Shake128().update(hashTxt).hexdigest(hashSize) 
        return hashHex

    def SetParam(self, param):
        self.settings = param

    def GetSettings (self):
        return self.settings

    def Insert(self, xText, sigText=""):
        m = self.settings.m
        hashSize = self.settings.hashSize
        xTextWithSig = "{}{}".format(xText, sigText)
        fingerprint = self.Fingerprint(xTextWithSig)
        pos_i1 = self.HashFunction(xTextWithSig, hashSize)
        pos_i2 = (pos_i1 ^ self.HashFunction(fingerprint, hashSize)) % m

        # add element if pos_i1 or pos_i2 is empty
        if self.bucket[pos_i1] == EMPTY:
            self.bucket[pos_i1] = fingerprint
            return

        if self.bucket[pos_i2] == EMPTY:
            self.bucket[pos_i2] = fingerprint
            return

        possibleIndexes = [pos_i1, pos_i2]
        ind = random.choice(possibleIndexes)
        MAXNUMKICKS = 100

        for _ in range(MAXNUMKICKS):
            rand = random.uniform(0, 1)
            if rand > 0.5:
                # swap fingerprint and that stoed in entry, e
                bucket[ind], fingerprint = fingerprint, bucket[ind]

            ind = (ind ^ self.HashFunction(fingerprint, hashSize)) % m

            if self.bucket[ind] == EMPTY:
                self.bucket[ind] = fingerprint
                return

        return False

    def Lookup(self, xText, sigText=""):
        m = self.settings.m
        hashSize = self.settings.hashSize
        xTextWithSig = "{}{}".format(xText, sigText)
        fingerprint = self.Fingerprint(xTextWithSig)
        pos_i1 = self.HashFunction(xTextWithSig, hashSize)
        pos_i2 = (pos_i1 ^ self.HashFunction(fingerprint, hashSize)) % m

        # add element if pos_i1 or pos_i2 is empty
        if (self.bucket[pos_i1] == fingerprint) or (self.bucket[pos_i2] == fingerprint):
            return True

        return False

    def Delete(self, xText, sigText=""):
        m = self.settings.m
        hashSize = self.settings.hashSize
        xTextWithSig = "{}{}".format(xText, sigText)
        fingerprint = self.Fingerprint(xTextWithSig)
        pos_i1 = self.HashFunction(xTextWithSig, hashSize)
        pos_i2 = (pos_i1 ^ self.HashFunction(fingerprint, hashSize)) % m

        if (self.bucket[pos_i1] == fingerprint):
            self.bucket[pos_i1] = EMPTY
            return True

        if (self.bucket[pos_i2] == fingerprint):
            self.bucket[pos_i2] = EMPTY
            return True

        return False

if __name__ == '__main__':
    cf = CuckooFilter()
    sigText = "xxx"
    cf.Insert("AAA", sigText)
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA", sigText)))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB", sigText)))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC", sigText)))
    print ("FOUND ACB: {}".format(cf.Lookup("ACB", sigText)))

    cf.Delete("AAA", sigText)
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA", sigText)))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB", sigText)))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC", sigText)))
    print ("FOUND ACB: {}".format(cf.Lookup("ACB", sigText)))

    cf.Insert("AAA", sigText)
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA", sigText)))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB", sigText)))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC", sigText)))
    print ("FOUND ACB: {}".format(cf.Lookup("ACB", sigText)))

    # don't mix signature argument with non-signature argument to prevent undefined results
    cf = CuckooFilter()
    cf.Insert("AAA")
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(cf.Lookup("ACB")))

    cf.Delete("AAA")
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC")))
    print ("FOUND ACB: {}".format(cf.Lookup("ACB")))

    cf.Insert("AAA")
    cf.Insert("KENNETH ODOH")
    print ("=================================")
    print ("FOUND AAA: {}".format(cf.Lookup("AAA")))
    print ("FOUND AAB: {}".format(cf.Lookup("AAB")))
    print ("FOUND AAC: {}".format(cf.Lookup("AAC")))
    print ("FOUND KENNETH ODOH: {}".format(cf.Lookup("KENNETH ODOH")))

