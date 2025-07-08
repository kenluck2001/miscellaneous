from collections import namedtuple
import random
import numpy as np
from scipy.linalg import hadamard
import math
import helper

SEED = 2023
random.seed(SEED)
np.random.seed(SEED)

class AClient:
    """
        This is used for generating records on the client and making it private.
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

    def getSettings (self):
        return self.settings

    def HCMS(self, dataVal, hashFamily):
        '''
            See Algorithm 6: A client-HCMS
            input: 
                dataVal is input in compressed form
                hashfamily containing k hash as functor
            output: a single snapshot
        '''
        k = self.settings.k
        m = self.settings.m
        epsilon = self.settings.epsilon
        j = random.randint(0, k-1)
        l = random.randint(0, m-1)

        vVec = [0] * m
        pos = self.helper.HashMsg (hashFamily[j], dataVal)
        vVec[pos] = 1

        hadamardMatrix = hadamard(m)
        vVec = np.asarray(vVec)
        wVec = np.matmul(hadamardMatrix, vVec.T)

        b = -1
        prob = math.exp(epsilon) / (math.exp(epsilon) + 1)
        if prob <= random.random():
            b = 1
        hatw = b * wVec[l]
        Snapshot = namedtuple('Snapshot', ['hatw', 'j', 'l'])
        snapshot  = Snapshot(hatw, j, l)

        return snapshot

    def CreateBulkRecords (self, textlist, hashFamily):
        snapshotLst = []
        for text in textlist:
            dataVal = self.helper.CreateMsgRepresentation (text)
            snapshot = self.HCMS(dataVal, hashFamily)
            snapshotLst.append (snapshot)

        return snapshotLst

