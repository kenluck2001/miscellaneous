 # -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from joblib import Parallel, delayed
import random
#import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from collections import namedtuple
from textProcessing import TEXTHANDLER
plt.style.use('ggplot')
from bfilter import BloomFilter
from ultrafilter import UltraFilter

WORD_LENGTH = 50
TOTAL_NUM_OF_ELEMENTS = 1<<21  # double the value for positive and negative elments, size of bloom filter = 2^20, then we multiply by 2
#TOTAL_NUM_OF_ELEMENTS = 50  # double the value for positive and negative elments, size of bloom filter = 2^20, then we multiply by 2
NUM_OF_PROCESSES = 6
MAX_NUM_OF_HASHES = 50

Param = namedtuple('Param', ['m', 'n', 'l', 'hashSize'])

def getSummaryMetrics(TP, FN, FP, TN):
    FPR = 1.0 * FP / (FP + TN)
    FNR = 1.0 * FN / (FN + TP)
    FI = (2.0 * TP) / ((2.0 * TP) + FP + FN)
    RESULT = {
        "fpr": FPR,
        "fnr": FNR,
        "f1score": FI
    }
    return RESULT


def createData(size, word_size = 8):
    txt_Handler = TEXTHANDLER()
    text_Lst =  [txt_Handler.GetRandomAlphabetWords(word_size) for _ in range(size)]
    return text_Lst


def summaryConfusionMatrix (positiveLst, negativeLst, epsilon=0, isRandom=True, settings=None):
    TP, FN, FP, TN = 0, 0, 0, 0 
    bf = UltraFilter() if isRandom else BloomFilter()

    if settings: bf.SetParam(settings)

    for word in positiveLst:
        bf.Insert(word)

    if isRandom: bf.Randomize(epsilon)

    for word in positiveLst:
        if bf.Lookup(word):
            TP += 1
        else:
            FN += 1

    for word in negativeLst:
        if bf.Lookup(word):
            FP += 1
        else:
            TN += 1
    #print("Settings: {}".format(bf.GetSettings()))
    return TP, FN, FP, TN


def getDataByAttributeList(aggDataDict, fKey ="fpr"):
    res = []
    for key in sorted(aggDataDict.keys()):
        m_val = aggDataDict[key][fKey]
        res.append (m_val)
    return res



def obtainEvalSummary(word_lst, size, isRandom, epsilon, param=None):
    posLst, negLst = word_lst[:(size//2)], word_lst[(size//2): size]
    TP, FN, FP, TN = summaryConfusionMatrix (posLst, negLst, epsilon=epsilon, isRandom=isRandom, settings=param)
    summary_eval = getSummaryMetrics(TP, FN, FP, TN)
    return summary_eval


def getDataOccByMetricThread(word_lst, size_ratio, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon):
    size = int(size_ratio * TOTAL_NUM_OF_ELEMENTS)
    summary_eval = obtainEvalSummary(word_lst, size, isRandom, epsilon)
    return summary_eval


def getDataOccupancyByMetric(word_lst, isRandom, epsilon=2):
    occupancy_ratio_lst = [0.2, 0.4, 0.6, 0.8, 1.0]
    # use ratio
    summary_eval_lst = Parallel(n_jobs=NUM_OF_PROCESSES, verbose=10)(delayed(getDataOccByMetricThread)(word_lst, size_ratio, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon) for size_ratio in occupancy_ratio_lst)
    output_dict = dict(zip(occupancy_ratio_lst, summary_eval_lst))
    return output_dict


def getDataNoiseByMetricThread(word_lst, size, isRandom, epsilon):
    summary_eval = obtainEvalSummary(word_lst, size, isRandom, epsilon)
    return summary_eval


def getDataNoiseByMetric(word_lst, isRandom):
    epsilon_lst = [0, 5, 10, 15, 20]
    summary_eval_lst = Parallel(n_jobs=NUM_OF_PROCESSES, verbose=10)(delayed(getDataNoiseByMetricThread)(word_lst, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon) for epsilon in epsilon_lst)
    output_dict = dict(zip(epsilon_lst, summary_eval_lst))
    return output_dict


def getDataNumOfHashesByMetricThread(word_lst, hash_ratio, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon):
    #num_hashes = int(hash_ratio * (TOTAL_NUM_OF_ELEMENTS // 2))
    num_hashes = int(hash_ratio * MAX_NUM_OF_HASHES)
    param = Param(1<<24, 1<<20, num_hashes, 128)
    summary_eval = obtainEvalSummary(word_lst, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon, param)
    return summary_eval


def getDataNumOfHashesByMetric(word_lst, isRandom, epsilon=2):
    Param = namedtuple('Param', ['m', 'n', 'l', 'hashSize'])
    numhashsizes_ratio_lst = [0.2, 0.4, 0.6, 0.8, 1.0]
    summary_eval_lst = Parallel(n_jobs=NUM_OF_PROCESSES, verbose=10)(delayed(getDataNumOfHashesByMetricThread)(word_lst, hash_ratio, TOTAL_NUM_OF_ELEMENTS, isRandom, epsilon) for hash_ratio in numhashsizes_ratio_lst)

    numhashsizes_lst = [int(x*MAX_NUM_OF_HASHES) for x in numhashsizes_ratio_lst]
    output_dict = dict(zip(numhashsizes_lst, summary_eval_lst))

    return output_dict


def experimentOccupancyByMetric(imagefile):
    word_lst = createData(TOTAL_NUM_OF_ELEMENTS, word_size=WORD_LENGTH)
    # UltraFilter
    occupancy_metric_rand = getDataOccupancyByMetric(word_lst, True)
    fpr_randlst = getDataByAttributeList(occupancy_metric_rand, fKey ="fpr")
    fnr_randlst = getDataByAttributeList(occupancy_metric_rand, fKey ="fnr")
    f1score_randlst = getDataByAttributeList(occupancy_metric_rand, fKey ="f1score")

    # BloomFilter
    occupancy_metric = getDataOccupancyByMetric(word_lst, False)
    fpr_lst = getDataByAttributeList(occupancy_metric, fKey ="fpr")
    fnr_lst = getDataByAttributeList(occupancy_metric, fKey ="fnr")
    f1score_lst = getDataByAttributeList(occupancy_metric, fKey ="f1score")

    xlist = sorted(occupancy_metric_rand.keys())
    # log UltraFilter experiment readings
    title = "[UltraFilter] Occupancy rate metric"
    logFile(title, xlist, fpr_randlst, fnr_randlst, f1score_randlst)

    # log BloomFilter experiment readings
    title = "[BloomFilter] Occupancy rate vs Summary metric"
    logFile(title, xlist, fpr_lst, fnr_lst, f1score_lst)

    # plot occupancy vs f1-score
    visDataDict = [  
        {"x" : xlist, "y" : f1score_lst, "color" : '#e66101', "label" : 'BloomFilter'},
        {"x" : xlist, "y" : f1score_randlst, "color" : '#5e3c99', "label" : 'UltraFilter, (ε=2)'} 
    ]

    xlabel, ylabel = "Occupancy Ratio", "F1-score"
    draw(visDataDict, xlabel, ylabel, imagefile=imagefile)
    return 0


def experimentNoiseByMetric(imagefile):
    word_lst = createData(TOTAL_NUM_OF_ELEMENTS, word_size=WORD_LENGTH)
    # UltraFilter
    noise_metric_rand = getDataNoiseByMetric(word_lst, True)
    fpr_randlst = getDataByAttributeList(noise_metric_rand, fKey ="fpr")
    fnr_randlst = getDataByAttributeList(noise_metric_rand, fKey ="fnr")
    f1score_randlst = getDataByAttributeList(noise_metric_rand, fKey ="f1score")

    # BloomFilter
    noise_metric = getDataNoiseByMetric(word_lst, False)
    fpr_lst = getDataByAttributeList(noise_metric, fKey ="fpr")
    fnr_lst = getDataByAttributeList(noise_metric, fKey ="fnr")
    f1score_lst = getDataByAttributeList(noise_metric, fKey ="f1score")

    xlist = sorted(noise_metric_rand.keys())
    # log UltraFilter experiment readings
    title = "[UltraFilter] Noise vs Summary metric"
    logFile(title, xlist, fpr_randlst, fnr_randlst, f1score_randlst)

    # log BloomFilter experiment readings
    title = "[BloomFilter] Noise vs Summary metric"
    logFile(title, xlist, fpr_lst, fnr_lst, f1score_lst)

    # plot occupancy vs f1-score
    visDataDict = [  
        {"x" : xlist, "y" : f1score_lst, "color" : '#e66101', "label" : 'BloomFilter'},
        {"x" : xlist, "y" : f1score_randlst, "color" : '#5e3c99', "label" : 'UltraFilter'} 
    ]

    xlabel, ylabel = "Noise level", "F1-score"
    draw(visDataDict, xlabel, ylabel, imagefile=imagefile)
    return 0

def experimentNumOfHashesByMetric(imagefile):
    word_lst = createData(TOTAL_NUM_OF_ELEMENTS, word_size=WORD_LENGTH)
    # UltraFilter
    num_of_hashes_metric_rand = getDataNumOfHashesByMetric(word_lst, True)
    fpr_randlst = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fpr")
    fnr_randlst = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fnr")
    f1score_randlst = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="f1score")

    # BloomFilter
    num_of_hashes_metric = getDataNumOfHashesByMetric(word_lst, False)
    fpr_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="fpr")
    fnr_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="fnr")
    f1score_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="f1score")

    xlist = sorted(num_of_hashes_metric_rand.keys())
    # log UltraFilter experiment readings
    title = "[UltraFilter] Number of hashes vs Summary metric"
    logFile(title, xlist, fpr_randlst, fnr_randlst, f1score_randlst)

    # log BloomFilter experiment readings
    title = "[BloomFilter] Number of hashes vs Summary metric"
    logFile(title, xlist, fpr_lst, fnr_lst, f1score_lst)

    # plot occupancy vs f1-score
    visDataDict = [  
        {"x" : xlist, "y" : f1score_lst, "color" : '#e66101', "label" : 'BloomFilter'},
        {"x" : xlist, "y" : f1score_randlst, "color" : '#5e3c99', "label" : 'UltraFilter, (ε=2)'} 
    ]

    xlabel, ylabel = "Number of hashes", "F1-score"
    draw(visDataDict, xlabel, ylabel, imagefile=imagefile, isintegertick=True)
    return 0

def experimentOccupancyByOverNoiseRangeMetric(imagefile):
    word_lst = createData(TOTAL_NUM_OF_ELEMENTS, word_size=WORD_LENGTH)
    # UltraFilter

    occupancy_metric_rand = getDataOccupancyByMetric(word_lst, True, epsilon=1)
    fpr_randlst1 = getDataByAttributeList(occupancy_metric_rand, fKey ="fpr")
    fnr_randlst1 = getDataByAttributeList(occupancy_metric_rand, fKey ="fnr")
    f1score_randlst1 = getDataByAttributeList(occupancy_metric_rand, fKey ="f1score")

    occupancy_metric_rand = getDataOccupancyByMetric(word_lst, True, epsilon=2)
    fpr_randlst2 = getDataByAttributeList(occupancy_metric_rand, fKey ="fpr")
    fnr_randlst2 = getDataByAttributeList(occupancy_metric_rand, fKey ="fnr")
    f1score_randlst2 = getDataByAttributeList(occupancy_metric_rand, fKey ="f1score")

    occupancy_metric_rand = getDataOccupancyByMetric(word_lst, True, epsilon=3)
    fpr_randlst3 = getDataByAttributeList(occupancy_metric_rand, fKey ="fpr")
    fnr_randlst3 = getDataByAttributeList(occupancy_metric_rand, fKey ="fnr")
    f1score_randlst3 = getDataByAttributeList(occupancy_metric_rand, fKey ="f1score")

    occupancy_metric_rand = getDataOccupancyByMetric(word_lst, True, epsilon=4)
    fpr_randlst4 = getDataByAttributeList(occupancy_metric_rand, fKey ="fpr")
    fnr_randlst4 = getDataByAttributeList(occupancy_metric_rand, fKey ="fnr")
    f1score_randlst4 = getDataByAttributeList(occupancy_metric_rand, fKey ="f1score")


    # BloomFilter
    occupancy_metric = getDataOccupancyByMetric(word_lst, False)
    fpr_lst = getDataByAttributeList(occupancy_metric, fKey ="fpr")
    fnr_lst = getDataByAttributeList(occupancy_metric, fKey ="fnr")
    f1score_lst = getDataByAttributeList(occupancy_metric, fKey ="f1score")

    xlist = sorted(occupancy_metric_rand.keys())
    # log UltraFilter experiment readings
    title = "[UltraFilter] Occupancy rate metric , (ε=1)"
    logFile(title, xlist, fpr_randlst1, fnr_randlst1, f1score_randlst1)

    title = "[UltraFilter] Occupancy rate metric , (ε=2)"
    logFile(title, xlist, fpr_randlst2, fnr_randlst2, f1score_randlst2)

    title = "[UltraFilter] Occupancy rate metric , (ε=3)"
    logFile(title, xlist, fpr_randlst3, fnr_randlst3, f1score_randlst3)

    title = "[UltraFilter] Occupancy rate metric , (ε=4)"
    logFile(title, xlist, fpr_randlst4, fnr_randlst4, f1score_randlst4)

    # log BloomFilter experiment readings
    title = "[BloomFilter] Occupancy rate vs Summary metric"
    logFile(title, xlist, fpr_lst, fnr_lst, f1score_lst)

    # plot occupancy vs f1-score
    visDataDict = [  
        {"x" : xlist, "y" : f1score_lst, "color" : '#d73027', "label" : 'BloomFilter'},
        {"x" : xlist, "y" : f1score_randlst1, "color" : '#fc8d59', "label" : 'UltraFilter, (ε=1)'},
        {"x" : xlist, "y" : f1score_randlst2, "color" : '#33a02c', "label" : 'UltraFilter, (ε=2)'},
        {"x" : xlist, "y" : f1score_randlst3, "color" : '#91bfdb', "label" : 'UltraFilter, (ε=3)'},
        {"x" : xlist, "y" : f1score_randlst4, "color" : '#4575b4', "label" : 'UltraFilter, (ε=4)'} 
    ]

    xlabel, ylabel = "Occupancy Ratio", "F1-score"
    draw(visDataDict, xlabel, ylabel, imagefile=imagefile)
    return 0

def experimentNumOfHashesByOverNoiseRangeMetric(imagefile):
    word_lst = createData(TOTAL_NUM_OF_ELEMENTS, word_size=WORD_LENGTH)
    # UltraFilter
    num_of_hashes_metric_rand = getDataNumOfHashesByMetric(word_lst, True, epsilon=1)
    fpr_randlst1 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fpr")
    fnr_randlst1 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fnr")
    f1score_randlst1 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="f1score")

    num_of_hashes_metric_rand = getDataNumOfHashesByMetric(word_lst, True, epsilon=2)
    fpr_randlst2 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fpr")
    fnr_randlst2 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fnr")
    f1score_randlst2 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="f1score")

    num_of_hashes_metric_rand = getDataNumOfHashesByMetric(word_lst, True, epsilon=3)
    fpr_randlst3 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fpr")
    fnr_randlst3 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fnr")
    f1score_randlst3 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="f1score")

    num_of_hashes_metric_rand = getDataNumOfHashesByMetric(word_lst, True, epsilon=4)
    fpr_randlst4 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fpr")
    fnr_randlst4 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="fnr")
    f1score_randlst4 = getDataByAttributeList(num_of_hashes_metric_rand, fKey ="f1score")

    # BloomFilter
    num_of_hashes_metric = getDataNumOfHashesByMetric(word_lst, False)
    fpr_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="fpr")
    fnr_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="fnr")
    f1score_lst = getDataByAttributeList(num_of_hashes_metric, fKey ="f1score")

    xlist = sorted(num_of_hashes_metric_rand.keys())
    # log UltraFilter experiment readings

    title = "[UltraFilter] Number of hashes vs Summary metric , (ε=1)"
    logFile(title, xlist, fpr_randlst1, fnr_randlst1, f1score_randlst1)

    title = "[UltraFilter] Number of hashes vs Summary metric , (ε=2)"
    logFile(title, xlist, fpr_randlst2, fnr_randlst2, f1score_randlst2)

    title = "[UltraFilter] Number of hashes vs Summary metric , (ε=3)"
    logFile(title, xlist, fpr_randlst3, fnr_randlst3, f1score_randlst3)

    title = "[UltraFilter] Number of hashes vs Summary metric , (ε=4)"
    logFile(title, xlist, fpr_randlst4, fnr_randlst4, f1score_randlst4)


    # log BloomFilter experiment readings
    title = "[BloomFilter] Number of hashes vs Summary metric"
    logFile(title, xlist, fpr_lst, fnr_lst, f1score_lst)

    # plot occupancy vs f1-score
    visDataDict = [  
        {"x" : xlist, "y" : f1score_lst, "color" : '#d73027', "label" : 'BloomFilter'},
        {"x" : xlist, "y" : f1score_randlst1, "color" : '#fc8d59', "label" : 'UltraFilter, (ε=1)'},
        {"x" : xlist, "y" : f1score_randlst2, "color" : '#33a02c', "label" : 'UltraFilter, (ε=2)'},
        {"x" : xlist, "y" : f1score_randlst3, "color" : '#91bfdb', "label" : 'UltraFilter, (ε=3)'},
        {"x" : xlist, "y" : f1score_randlst4, "color" : '#4575b4', "label" : 'UltraFilter, (ε=4)'} 
    ]

    xlabel, ylabel = "Number of hashes", "F1-score"
    draw(visDataDict, xlabel, ylabel, imagefile=imagefile, isintegertick=True)
    return 0

def draw(visDataDict, xlabel, ylabel, imagefile="experiment.png", isintegertick=False):
    """
        visDataDict: is a list of dicts
    """
    xvalues_lst = []
    for vis in visDataDict:
        xlist, ylist, color, label = vis["x"], vis["y"], vis["color"], vis["label"]
        xvalues_lst.extend(xlist)
        plt.plot(xlist, ylist, color=color, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(0, 1.02)
    tol = 0.01
    dmin, dmax = min(xvalues_lst) - tol, max(xvalues_lst) + tol
    plt.xlim(dmin, dmax)
    if isintegertick: plt.xticks(visDataDict[0]["x"], visDataDict[0]["x"])  
    plt.legend()
    plt.savefig(imagefile)
    plt.close()


def logFile(title, xlist, fpr_randlst, fnr_randlst, f1score_randlst, log="result.txt"):
    with open(log, "a") as file:
        file.write (title)
        file.write ("\nx-axis list: {}".format(xlist))
        file.write ("\nfpr scores: {}".format(fpr_randlst))
        file.write ("\nfnr scores: {}".format(fnr_randlst))
        file.write ("\nf1  scores: {}".format(f1score_randlst))
        file.write ("\n============================\n")

if __name__ == '__main__':
    #experimentNoiseByMetric("NoiseByMetric.png")
    #experimentOccupancyByOverNoiseRangeMetric("OccupancyByOverNoiseRange.png")
    experimentNumOfHashesByOverNoiseRangeMetric("NumOfHashesByOverNoiseRange.png")
    experimentOccupancyByMetric("OccupancyByMetric.png")
    experimentNumOfHashesByMetric("NumOfHashesByMetric.png")


    #func_lst = [(experimentNoiseByMetric, "NoiseByMetric.png"), (experimentOccupancyByOverNoiseRangeMetric, "OccupancyByOverNoiseRange.png"),    (experimentNumOfHashesByOverNoiseRangeMetric, "NumOfHashesByOverNoiseRange.png"), (experimentOccupancyByMetric, "OccupancyByMetric.png"), (experimentNumOfHashesByMetric, "NumOfHashesByMetric.png") ]

    #result_lst = Parallel(n_jobs=NUM_OF_PROCESSES, verbose=10)(delayed(func)(imagefile) for func, imagefile in func_lst)



