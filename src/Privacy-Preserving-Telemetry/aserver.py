from collections import namedtuple
import random
import numpy as np
from scipy.linalg import hadamard
import math
import helper

SEED = 2023
random.seed(SEED)
np.random.seed(SEED)

class AServer:
    """
        This is for server for counting the records sent from the client.
        Reference: https://docs-assets.developer.apple.com/ml-research/papers/learning-with-privacy-at-scale.pdf
    """
    def __init__(self):
        self.Param = namedtuple('Param', ['k', 'm', 'epsilon'])
        # Adding settings
        self.settings = self.Param(65536, 1024, 4)
        self.dataSize = None
        self.helper = helper.Helper(self.settings, SEED)

    def SetNoise(self, epsilon=4):
        #self.settings.epsilon = epsilon
        self.settings = self.Param(65536, 1024, epsilon)

    def SketchHCMS(self, snapshotLst):
        '''
            See Algorithm 7: sketch-HCMS
            input: 
                snapshotLst is list of snapshotLst
            output: sketch matrix
        '''
        k = self.settings.k
        m = self.settings.m
        epsilon = self.settings.epsilon
        cepsilon = (math.exp(epsilon) + 1) / (math.exp(epsilon) - 1)
        n = len (snapshotLst)
        self.dataSize = n # save data size in settings

        xlst = [0] * n
        for i in range (n):
            snapshot = snapshotLst[i]
            xlst[i] = k * cepsilon * snapshot.hatw

        mHmat = np.zeros((k, m))
        hadamardMatrix = hadamard(m)
        for i in range (n):
            snapshot = snapshotLst[i]
            j = snapshot.j
            l = snapshot.l
            mHmat[j][l]  = mHmat[j][l] +  xlst[i]

        mHmat = np.matmul(mHmat, hadamardMatrix.T)

        return mHmat

    def __histogram (self, event, mHmat, hashFamily):
        k = self.settings.k
        m = self.settings.m
        n = self.dataSize
        #print ("(k: {}, m: {}, n: {})".format(k,m,n))
        sumVal = 0
        dataVal = self.helper.CreateMsgRepresentation (event)

        for l in range(0, k):
            pos = self.helper.HashMsg (hashFamily[l], dataVal)
            sumVal += mHmat[l][pos]

        avgVal = sumVal / k
        freq = (m / (m - 1)) * (avgVal - (n / m))

        return freq

    def Histogram (self, eventLst, mHmat, hashFamily):
        '''
            See Algorithm 4:
            input: 
                eventLst is list of predefined event to calculate their frequency
                mHmat is hadamard matrices
                hashfamily is a set of hash functions
            output: resDict of frequency of events
        '''    
        resDict = {}

        for event in eventLst:
            freq = self.__histogram (event, mHmat, hashFamily)
            # possible to have negative because hadamard matrices has negative entries
            resDict[event] = int(math.ceil ( abs(freq) ))

        return resDict


