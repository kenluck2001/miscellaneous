from collections import namedtuple
from textProcessing import TEXTHANDLER
import random
from utils import Vector
from signature import Signature
# Import math Library
import math

"""
References
----------
[1] Lattice-based Blind Signatures, https://eprint.iacr.org/2008/322
[2] Fiat-Shamir With Aborts:Applications to Lattice and Factoring-Based Signatures, https://www.iacr.org/archive/asiacrypt2009/59120596/59120596.pdf
"""

class Signer(Signature):
    '''
        Server component
    '''
    def __init__(self, settings=None):

        super(Signer, self).__init__(settings) 
        if settings:
            self.settings = settings
        self.yHat = None # random vector for signer's commitment
        self.zHatStarVec = None # part of blind signature
        self.eplisonStar = None # challenge from user

    def CreateParams(self):
        Param = namedtuple('Param', ['n', 'd_s', 'c_m', 'm', 'phi', 'psi', 'q', 'limits'])

        nVal = 1<<3
        qVal = self.GetQValues(nVal)
        lowerBound, higherBound = qVal//(8*nVal), qVal//(4*nVal)
        d_sVal = random.randint(lowerBound, higherBound)
        c_mVal = (1.0 / math.log((2 * d_sVal), 2)) + 1
        mVal = int(c_mVal * math.log(qVal, 2)) + 1

        lowerBound, higherBound = 2, 100
        phiVal = random.randint(higherBound, higherBound * higherBound)
        psiVal = random.randint(lowerBound, higherBound)

        # obtain limits
        d_eplisonVal = 1
        d_alphaVal = psiVal * nVal * d_eplisonVal
        d_eplisonStarVal = d_alphaVal - d_eplisonVal
        d_yVal = phiVal * mVal * nVal * nVal * d_sVal * d_eplisonStarVal
        d_GStarVal = d_yVal - (nVal * d_sVal * d_eplisonStarVal)
        d_betaVal = phiVal * mVal * nVal * d_GStarVal
        d_GVal = d_betaVal - d_GStarVal
        d_DVal = d_GStarVal + d_betaVal + (nVal * d_sVal * d_eplisonVal)

        limitDict = {
            "d_eplison" : d_eplisonVal,
            "d_alpha" : d_alphaVal,
            "d_eplisonStar": d_eplisonStarVal,
            "d_y": d_yVal,
            "d_GStar": d_GStarVal,
            "d_beta": d_betaVal,
            "d_G" : d_GVal,
            "d_D" : d_DVal
        }

        self.settings = Param(nVal, d_sVal, c_mVal, mVal, phiVal, psiVal, qVal, limitDict)

    def SetParams(self, settings):
        self.settings = settings

    def GetParams(self):
        return self.settings

    def KeyGen(self):
        """
            Must be replaced with setKeys when necessary
        """
        if not self.settings:
            raise Exception("settings must be provided") 
        d_sVal = self.settings.d_s
        mVal = self.settings.m
        secretVec = self.SampleVector(d_sVal, mVal)
        publicKey = self.HashMsg(tuple(secretVec))

        CryptoKey = namedtuple('CryptoKey', ['secret', 'public'])
        self.CryptoKey = CryptoKey(secretVec, publicKey)
        print ("self.CryptoKey: {}".format(self.CryptoKey))
        return self.CryptoKey

    def SetKey(self, secretVec, publicKey):
        mVal = self.settings.m
        skLen = len(secretVec)
        if (mVal != skLen):
            raise Exception("Ensure secretKey vector is about length: {}".format(skLen)) 
        if not isinstance(publicKey, int):
            raise Exception("Ensure publicKey: {} is an integer".format(publicKey)) 

        CryptoKey = namedtuple('CryptoKey', ['secret', 'public'])
        self.CryptoKey = CryptoKey(secretVec, publicKey) 

    def GetPublicKey(self):
        if self.CryptoKey.public is None:
            raise Exception("KeyGen method must be called") 
        return self.CryptoKey.public

    def CreateCommitment(self):
        if not self.settings:
            raise Exception("settings must be provided") 
        mVal = self.settings.m
        d_yVal = self.settings.limits["d_y"]
        self.yHat = self.SampleVector(d_yVal, mVal)
        hashVal = self.HashMsg(tuple(self.yHat))
        return hashVal

    def CreateBlindedSignature(self, challenge):
        """
            input:
                challenge is D_c^*
        """
        if not self.CryptoKey.public:
            raise Exception("KeyGen method must be called") 
        yHatVec = self.yHat
        sHatVec = self.CryptoKey.secret
        sHatErrorVec = Vector.scalarMul(sHatVec, challenge)
        #print ("sHatErrorVec: {}, yHatVec: {}".format(sHatErrorVec, yHatVec))
        self.zHatStarVec = Vector.add(sHatErrorVec, yHatVec)
        self.eplisonStar = challenge
        return self.zHatStarVec

    def GetSignature(self, commitmentWithMetadata):
        """
            input:
                commitmentWithMetadata is namedtuple (C, alpha, betaVec, eplison) from ConvertBlindToRealSignature method of user class
        """
        CVal, alpha, betaVec, eplison = commitmentWithMetadata.C, commitmentWithMetadata.alpha, commitmentWithMetadata.betaVec, commitmentWithMetadata.eplison
        S = self.CryptoKey.public
        commitmentVal = self.HashMsg(tuple(self.yHat))
        challengeParam = "{}{}".format(commitmentVal - (S * alpha) - self.HashMsg(tuple(betaVec)), CVal)

        if not (((self.eplisonStar + alpha) == eplison) and (self.HashMsg(challengeParam) == eplison)):
            raise Exception("signature don't match") 

        zHatVec = Vector.sub(self.zHatStarVec, betaVec)
        signature = (zHatVec, eplison)
        return signature


############################################
############################################
############################################


class User(Signature):
    '''
        Client component
    '''
    def __init__(self, settings=None):
        super(User, self).__init__(settings) 
        if settings:
            self.settings = settings
        self.CommitmentWithMetadata = namedtuple('CommitmentWithMetadata', ['C', 'alpha', 'betaVec', 'eplison'])
        self.zHatVec = None # part of signature
        self.txtHandler = TEXTHANDLER()

    def SetParams(self, settings):
        self.settings = settings

    def CreateChallenge(self, message, commitment, S):
        """
            input:
                message in alphabets
                commitment is in integer 
                S is signer's public key in integer
        """
        nVal = self.settings.n
        mVal = self.settings.m
        d_betaVal = self.settings.limits["d_beta"]
        d_alphaVal = self.settings.limits["d_alpha"]
        randText =  self.txtHandler.GetRandomAlphabetWords(nVal//8)
        concatMsg = "{}{}".format(message, randText)
        CVal = self.HashComm(concatMsg)
        alpha = self.SampleVector(d_alphaVal, 2)[0]
        betaVec = self.SampleVector(d_betaVal, mVal)

        challengeParam = "{}{}".format(commitment - (S * alpha) - self.HashMsg(tuple(betaVec)), CVal)
        eplison = self.HashMsg(challengeParam) # challenge
        eplisonStar = eplison - alpha
        self.commitmentWithMetadata = self.CommitmentWithMetadata(CVal, alpha, betaVec, eplison)
        return eplisonStar

    def ConvertBlindToRealSignature(self, zHatStarVec):
        betaVec = self.commitmentWithMetadata.betaVec
        self.zHatVec = Vector.sub(zHatStarVec, betaVec) # part of signature
        return self.commitmentWithMetadata

    def GetSignature(self):
        eplison = self.commitmentWithMetadata.eplison
        signature = (self.zHatVec, eplison)
        return signature

############################################
############################################
############################################

if __name__ == '__main__':
    #############################################
    ########## SERVER <-----> CLIENT ############

    signer = Signer()
    signer.CreateParams()
    signer.KeyGen()

    user = User()

    settings = signer.GetParams()

    # transfer settings to client
    user.SetParams(settings)

    # server commitment (step 1)
    commitment = signer.CreateCommitment()

    # create client challenge
    message = "HELLO WORLD"

    S = signer.GetPublicKey()
    challenge = user.CreateChallenge(message, commitment, S)
    print("client challenge: {}".format(challenge))

    zHatStarVec = signer.CreateBlindedSignature(challenge)
    #print ("signers Blind signature: {}".format(zHatStarVec))

    commitmentWithMetadata = user.ConvertBlindToRealSignature(zHatStarVec)

    ssignature = signer.GetSignature(commitmentWithMetadata)
    print ("signer signature: {}".format(ssignature))

    usignature = user.GetSignature()
    print ("user signature: {}".format(usignature))


    #self.CryptoKey: CryptoKey(secret=[-1326, -987, 1051, -466, 1064, 104, -1604, -1395, -679, -1590, -1273, 616, 475, -1318, 181, 1251, -1415, -906], public=-20644)


    ##############################################################
    ########## SERVER <-----> CLIENT using preset key ############

    print ("##############################################################")

    signer = Signer()
    signer.CreateParams()
    secretVec=[-1326, -987, 1051, -466, 1064, 104, -1604, -1395, -679, -1590, -1273, 616, 475, -1318, 181, 1251, -1415, -906] 
    publicKey=-20644
    signer.SetKey(secretVec, publicKey)

    user = User()
    settings = signer.GetParams()

    # transfer settings to client
    user.SetParams(settings)

    # server commitment (step 1)
    commitment = signer.CreateCommitment()

    # create client challenge
    message = "HELLO WORLD"

    S = signer.GetPublicKey()
    challenge = user.CreateChallenge(message, commitment, S)
    print("client challenge: {}".format(challenge))

    zHatStarVec = signer.CreateBlindedSignature(challenge)
    #print ("signers Blind signature: {}".format(zHatStarVec))

    commitmentWithMetadata = user.ConvertBlindToRealSignature(zHatStarVec)

    ssignature = signer.GetSignature(commitmentWithMetadata)
    print ("signer signature: {}".format(ssignature))

    usignature = user.GetSignature()
    print ("user signature: {}".format(usignature))

    print ("signer's signature hash: {}, client's signature hash: {}".format(signer.hashedSignature(ssignature, n=1<<20), user.hashedSignature(usignature, n=1<<20)))


