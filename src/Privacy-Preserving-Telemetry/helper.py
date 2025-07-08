import random
import numpy as np
import math
from textProcessing import TEXTHANDLER

class Helper:
    """
        This is for managing textual representation.
    """
    def __init__(self, settings, seed):
        self.settings = settings
        self.txtHandler = TEXTHANDLER()

        random.seed(seed)
        np.random.seed(seed)

    def CreateMsgRepresentation (self, text):
        '''
            Represent text message in numeric form
            input:
                text in alphabetical form
            output:
                val is a decimal
        '''
        textVec = self.txtHandler.GenerateVecFromText(text)
        size = len (textVec)
        val = 0
        for cVal, ind in zip (textVec, range (1, size+1)):
            val += (cVal * ind)

        return val

    def HashFamily (self):
        k = self.settings.k
        m = self.settings.m
        hMat = np.random.randint(0, 1024, size = (k, 3)) # degree 3

        return hMat.astype(int)

    def HashMsg (self, hVec, dataVal):
        '''
            input: 
                hVec is a row of the hash family matrix
                dataVal in compressed form
            output:
                res is integer (pos)
        '''
        m = self.settings.m
        dataVec = [1, dataVal, math.pow(dataVal, 2) ]
        dataVec = np.asarray(dataVec).astype(int)
        res = np.dot(hVec, dataVec) % m

        return res

