"""
Evaluation source code
"""
import pandas as pd
import numpy as np
from collections import defaultdict
import math
import random
#import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE

SEED = 65535
np.random.seed(SEED) # MAKE EXPERIMENTS REPRODUCIBLE

avg = lambda xs : sum(xs) / len(xs)
uFunc2 = lambda xs, y : abs(avg(xs) - y) # ranking function

def getSensistivity(dataLst):
    '''
        Calculate sensitivity
        input:
            dataLst: list of element (raw data), 1D 
        Output:
            return sensitivity in float
    '''
    maxVal = float ('-inf')
    for xVal in dataLst:
        for yVal in dataLst:
            curDiff = abs (xVal - yVal)
            if maxVal < curDiff:
                maxVal = curDiff
    return maxVal


def getSensistivityOpt(sortLst):
    '''
        Calculate sensitivity (optimized)
        input:
            sortLst: sorted list of element (raw data), 1D 
        Output:
            return sensitivity in float
    '''
    left = 0
    right = len (sortLst) - 1
    maxVal = float ('-inf')

    while left <= right:
        xVal, yVal = sortLst[left], sortLst[right]
        curDiff = abs (xVal - yVal)
        if maxVal < curDiff:
            maxVal = curDiff
        left = left + 1
        right = right - 1
    return maxVal


def ExponentialMech(x, R, u, sensitivity, epsilon):
    '''
        Exponential mechanism
        input:
            x: list of element (raw data), 1D
            R: set of element (raw data), 1D  
            u: ranking functor
            sensitivity: sensitivity of data
            epsilon: magnitude of noise
        Output:
            noisy response from exponential machanism
    '''
    # Calculate the score for each element of R
    scores = [u(x, r) for r in R]
    # Calculate the probability for each element, based on its score
    probabilities = [np.exp(epsilon * score / (2 * sensitivity)) for score in scores]
    # Normalize the probabilties so they sum to 1
    probabilities = probabilities / np.linalg.norm(probabilities, ord=1)
    # Choose an element from R based on the probabilities
    return np.random.choice(R, 1, p=probabilities)[0]


def permutationEntropy(sLst, nPattern):
    entropy = 0.0
    nLen = len(sLst)
    patternProb = defaultdict(int)
    for i in range(0, nLen-nPattern+1):
        start = i
        end = i + nPattern
        cLst = sLst[start: end]
        sortLst = sorted(range(len(cLst)), key=lambda k: cLst[k])
        patternProb[tuple(sortLst)] += 1
    denom = nLen - nPattern + 1
    for num in patternProb.values():
        prob = (1.0 * num / denom)
        entropy -=  prob * math.log(prob, 2)
    return entropy


def GetMaxSensistivity(df):
    maxSentivity = float ('-inf')
    for column in df._get_numeric_data():
        columnLst = df[column].to_list()
        maxSentivity = max(maxSentivity, getSensistivity(columnLst))
    return maxSentivity


def GetExponentialMechDataFrame(df, uFunc2, sensitivity, epsilon):
    '''
        sensitivity: max sensitivity across all columns
    '''
    data = {}
    for column in df._get_numeric_data():
        columnLst = df[column].to_list()
        noisyExpLst = [ExponentialMech(columnLst, columnLst, uFunc2, sensitivity, epsilon) for _ in range(len(columnLst))]
        data[column] = noisyExpLst

    df = pd.DataFrame(data)
    return df


def ReduceDim(df, nComponents=1):
    dfMat = df._get_numeric_data().values
    dfvec = TSNE(n_components=nComponents, perplexity=7).fit_transform(dfMat).ravel()
    return dfvec


def ObtainPrivacyRisk(df, uFunc2, epsilon):
    '''
        returns tuple of degree of anomymity for original data, transformed data, pattern length, and amplification
    '''
    sensitivity = GetMaxSensistivity(df)
    noisydf =  GetExponentialMechDataFrame(df, uFunc2, sensitivity, epsilon)
    dfLst = ReduceDim(df)
    noisydfLst = ReduceDim(noisydf)
    patternLenlst = range(1, 25)
    # corresponding y axis values
    entropylst = [permutationEntropy(dfLst, nPattern) for nPattern in patternLenlst]
    index = entropylst.index(max(entropylst))
    print ("max entropy: {}".format(entropylst[index]))
    print ("pattern length with max entropy: {}".format(patternLenlst[index]))
    nPattern = patternLenlst[index]
    e1 = permutationEntropy(dfLst, nPattern) / math.log(len(dfLst), 2)
    e2 = permutationEntropy(noisydfLst, nPattern) / math.log(len(noisydfLst), 2)
    gamma = e2 * (1.0 - e1) / (e1 * (1.0 - e2))
    return e1, e2, nPattern, gamma


def ObtainPrivacyRiskNonPriv(df):
    '''
        returns tuple of degree of anomymity for original data, transformed data, pattern length, and amplification
    '''
    sensitivity = GetMaxSensistivity(df)
    dfLst = ReduceDim(df)
    noisydfLst = range(len(df))
    patternLenlst = range(1, 25)
    # corresponding y axis values
    entropylst = [permutationEntropy(dfLst, nPattern) for nPattern in patternLenlst]
    index = entropylst.index(max(entropylst))
    print ("max entropy: {}".format(entropylst[index]))
    print ("pattern length with max entropy: {}".format(patternLenlst[index]))
    nPattern = patternLenlst[index]
    e1 = permutationEntropy(dfLst, nPattern) / math.log(len(dfLst), 2)
    e2 = permutationEntropy(noisydfLst, nPattern) / math.log(len(noisydfLst), 2)
    gamma = e2 * (1.0 - e1) / (e1 * (1.0 - e2))
    return e1, e2, nPattern, gamma


def drawChart(xlst, ylst, xlabelTxt = 'x - axis', ylabelTxt = 'y - axis', titleTxt = 'My first graph!', imagefile = "out.png"):
    # plotting the points 
    plt.plot(xlst, ylst)

    # naming the x axis
    plt.xlabel(xlabelTxt)
    # naming the y axis
    plt.ylabel(ylabelTxt)

    # giving a title to my graph
    plt.title(titleTxt)
    plt.grid(axis='both', alpha=.3)

    # Remove borders
    plt.gca().spines["top"].set_alpha(0.0)    
    plt.gca().spines["bottom"].set_alpha(0.3)
    plt.gca().spines["right"].set_alpha(0.0)    
    plt.gca().spines["left"].set_alpha(0.3)   

    # function to show the plot
    #plt.show()

    plt.legend()
    plt.savefig(imagefile)
    plt.close()


def ExperimentRandomGenValues():
    epsilon = 0.337
    delta = 0.1
    MAX_COUNT = 10000  # use for real data
    physicsLst = [random.randint(1,100) for _ in range (MAX_COUNT)]
    sensitivity = getSensistivity(physicsLst) # sensitivity of physics
    print ("sensitivity : {}".format(sensitivity))

    print ("#########################################")
    print ("###########Exponential Mechanism#########")
    print ("#########################################")

    noisyExpPhysics = [ExponentialMech(physicsLst, physicsLst, uFunc2, sensitivity, epsilon) for _ in range(len(physicsLst))]
    nPattern = 11
    e1 = permutationEntropy(physicsLst, nPattern) / math.log(len(physicsLst), 2)
    e2 = permutationEntropy(noisyExpPhysics, nPattern) / math.log(len(noisyExpPhysics), 2)

    gamma = e2 * (1.0 - e1) / (e1 * (1.0 - e2))

    ceplison = math.log(gamma)

    print ("input prob: {}, noisy prob: {}, eplison: {}".format(e1, e2, ceplison))
    print("entropy value: {}".format(permutationEntropy(physicsLst, nPattern)))
    
    # x axis values
    patternLenlst = range(1, MAX_COUNT, 5)
    # corresponding y axis values
    entropylst = [permutationEntropy(physicsLst, nPattern) for nPattern in patternLenlst]

    drawChart(patternLenlst, entropylst, xlabelTxt = 'Pattern Length', ylabelTxt = 'Permutation Entropy', titleTxt = 'Graph of Permutation entropy vs Pattern Length', imagefile = "patternlengthvsentropy2.png")
    index = entropylst.index(max(entropylst))
    print("Maximum index present in the entropy: {}".format(index) )
    print ("pattern length with max entropy: {}".format(patternLenlst[index]))
    print ("max entropy: {}".format(entropylst[index]))

    print("max degree of anonymity value: {}".format(permutationEntropy(physicsLst, patternLenlst[index]) / math.log(len(physicsLst), 2)))


def ExperimentOnPublicData():
    #https://www.kaggle.com/datasets/umerrtx/machine-failure-prediction-using-sensor-data [machine-prediction.csv]
    #https://www.kaggle.com/datasets/rabieelkharoua/predict-customer-purchase-behavior-dataset [customer-purchase.csv]
    #https://www.kaggle.com/datasets/mrsimple07/employee-attrition-data-prediction [employee-attrition.csv]

    epsilon = 0.337
    delta = 0.1
    datasetNamesLst = ["machine-prediction.csv", "customer-purchase.csv", "employee-attrition.csv"]
    for dataset in datasetNamesLst:
        df = pd.read_csv('./data/{}'.format(dataset))  
        e1, e2, nPattern, gamma = ObtainPrivacyRisk(df, uFunc2, epsilon)
        print("# dataset: {}, size: {}, pattern length: {}, e1: {}, e2: {}, gamma: {}".format(dataset, len(df), nPattern, e1, e2, gamma))
        print("################################################")


def ExperimentOnNonPrivate():
    #https://www.kaggle.com/datasets/umerrtx/machine-failure-prediction-using-sensor-data [machine-prediction.csv]
    #https://www.kaggle.com/datasets/rabieelkharoua/predict-customer-purchase-behavior-dataset [customer-purchase.csv]
    #https://www.kaggle.com/datasets/mrsimple07/employee-attrition-data-prediction [employee-attrition.csv]

    epsilon = 0.337
    delta = 0.1
    datasetNamesLst = ["machine-prediction.csv", "customer-purchase.csv", "employee-attrition.csv"]
    for dataset in datasetNamesLst:
        df = pd.read_csv('./data/{}'.format(dataset))  
        e1, e2, nPattern, gamma = ObtainPrivacyRiskNonPriv(df)
        print("# dataset: {}, size: {}, pattern length: {}, e1: {}, e2: {}, gamma: {}".format(dataset, len(df), nPattern, e1, e2, gamma))
        print("################################################")

if __name__ == '__main__':
    #ExperimentRandomGenValues()
    print ("privacy-preserving cases")
    ExperimentOnPublicData()
    print ("blatantly private cases")
    ExperimentOnNonPrivate()

    
