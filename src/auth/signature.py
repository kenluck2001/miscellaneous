from keccak import Shake128
import random

############################################
############################################
############################################

class Signature(object):

    def __init__(self, settings=None):
        if settings:
            self.settings = settings
        #self.LIMIT = 100000
        self.LIMIT = 10000

    def __GetPrime(self, lowerBound = 100, higherBound = 200):
        randVal = random.randint(lowerBound, higherBound)
        isPrime = self.__CheckIfProbablyPrime(randVal)
        while not isPrime:
            randVal = random.randint(lowerBound, higherBound)
            isPrime = self.__CheckIfProbablyPrime(randVal)
        return randVal

    def __CheckIfProbablyPrime(self, x):
        return pow(2, x-1, x) == 1

    def GetQValues(self, n):
        lowerBound = int(pow(n, 5.5))
        higherBound = lowerBound + self.LIMIT
        qVal = self.__GetPrime(lowerBound, higherBound)
        return qVal

    def SampleVector(self, bound, size):
        limit = int(bound)
        rfield = self.__sampleVector(limit, size)
        return rfield

    def __sampleVector(self, bound, size):
        randList=[]
        for i in range(size):
            cVal = random.randint(-bound, bound)
            randList.append(cVal)
        return randList

    def __hashTupleOrString(self, msgTxt):
        hashSize = 128
        if type(msgTxt) is tuple:
            hashVal = hash (msgTxt)
        else:
            hashVal = int(Shake128().update(msgTxt).hexdigest(hashSize), 16)
        return hashVal

    def HashMsg(self, msgTxt):
        qVal = self.settings.q
        nVal = self.settings.n
        hashVal = self.__hashTupleOrString(msgTxt)
        hashVal = hashVal % (qVal - 1)
        hashVal = hashVal - (qVal - 1)//2
        #hashVal = 1.0 * hashVal / (pow(hashVal, nVal) + 1)
        return hashVal

    def HashComm(self, msgTxt, n=None):
        nVal = self.settings.n
        hashVal = self.__hashTupleOrString(msgTxt)
        nnVal = n if n else (1 << nVal) 
        hashVal = hashVal % nnVal
        return hashVal

    def hashedSignature(self, signature, n=None):
        zHatVec, eplison = signature
        zHatVec.append(eplison)
        return self.HashComm(tuple(zHatVec), n)


