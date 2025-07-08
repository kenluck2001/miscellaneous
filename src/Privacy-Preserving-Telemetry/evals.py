import random
import bisect
from aserver import AServer
from aclient import AClient
from helper import Helper
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt
plt.style.use('ggplot')

SEED = 2023

def __sampleRandomEvent(event_lst, prob_lst):
    '''
        event_lst is a set of events
        prob_lst is a list of probability of occurence of each event, 
        same length for event_lst and prob_lst
    '''
    cumprob_lst = list(prob_lst)
    n = len(prob_lst)
    for i in range (1, n):
        cumprob_lst[i] = cumprob_lst[i - 1] + prob_lst[i]
    rand = random.uniform(0, 1)
    idx = bisect.bisect_left(cumprob_lst, rand)
    while idx == -1:
        rand = random.uniform(0, 1)
        idx = bisect.bisect_left(cumprob_lst, rand)
    return event_lst[idx]

def sampleRandomEvent(event_lst, prob_lst, size):
    '''
        event_lst is a set of events
        prob_lst is a list of probability of occurence of each event, 
        same length for event_lst and prob_lst
        size is the number of generated events
    '''
    res_lst = []
    for _ in range(size):
        cevent = __sampleRandomEvent(event_lst, prob_lst)
        res_lst.append (cevent)
    return res_lst

def getDataProportion(sampled_event_lst):
    output_dict = {}
    for event in sampled_event_lst:
        if event not in output_dict:
            output_dict[event] = 1
        else:
            output_dict[event] += 1
    return output_dict

def experimentSizeByProportion():
    size_lst = [10000, 20000, 30000, 40000, 50000]
    prob_lst = [0.6, 0.3, 0.1] 
    event_lst = ["walking", "running", "sleeping"] 
    output_dict = {}
    server = AServer()
    client = AClient()
    settings = client.getSettings()
    helper = Helper(settings, SEED)
    hashFamily = helper.HashFamily()
    for size in size_lst:
        sampled_event_lst = sampleRandomEvent(event_lst, prob_lst, size)
        original_proportion = getDataProportion(sampled_event_lst)
        clientRandomizedData = client.CreateBulkRecords (sampled_event_lst, hashFamily)
        mHmat = server.SketchHCMS(clientRandomizedData)
        freqDict = server.Histogram (event_lst, mHmat, hashFamily)
        output_dict[size] = {"original" : original_proportion, "random" : freqDict}
    return output_dict

def experimentNoiseByProportion():
    size = 10000
    epsilon_lst = [4, 8, 12, 16, 20]
    prob_lst = [0.6, 0.3, 0.1] 
    event_lst = ["walking", "running", "sleeping"] 
    output_dict = {}
    server = AServer()
    client = AClient()
    settings = client.getSettings()
    helper = Helper(settings, SEED)
    hashFamily = helper.HashFamily()
    for epsilon in epsilon_lst:
        sampled_event_lst = sampleRandomEvent(event_lst, prob_lst, size)
        original_proportion = getDataProportion(sampled_event_lst)
        client.SetNoise(epsilon)
        clientRandomizedData = client.CreateBulkRecords (sampled_event_lst, hashFamily)
        server.SetNoise(epsilon)
        mHmat = server.SketchHCMS(clientRandomizedData)
        freqDict = server.Histogram (event_lst, mHmat, hashFamily)
        output_dict[epsilon] = {"original" : original_proportion, "random" : freqDict}
    return output_dict

def getDataByAttributeList(aggDataDict, level1 ="random", level2 ="walking"):
    res = []
    for key in sorted(aggDataDict.keys()):
        cDataDict = aggDataDict[key][level1]
        res.append (cDataDict[level2])
    return res

def draw(aggDataDict, xlabel, ylabel, imagefile):
    # set width of bar 
    barWidth = 0.25
    fig = plt.subplots(figsize =(12, 8)) 
    # set height of bar 
    walking_lst = getDataByAttributeList(aggDataDict, level1 ="random", level2 ="walking")
    running_lst = getDataByAttributeList(aggDataDict, level1 ="random", level2 ="running") 
    sleeping_lst = getDataByAttributeList(aggDataDict, level1 ="random", level2 ="sleeping") 
    # Set position of bar on X axis 
    br1 = range(len(walking_lst)) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2] 
    # Make the plot
    plt.bar(br1, walking_lst, color ='r', width = barWidth, 
		    edgecolor ='grey', label ='Walking') 
    plt.bar(br2, running_lst, color ='g', width = barWidth, 
		    edgecolor ='grey', label ='Running') 
    plt.bar(br3, sleeping_lst, color ='b', width = barWidth, 
		    edgecolor ='grey', label ='Sleeping') 
    # Adding Xticks 
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15) 
    plt.ylabel(ylabel, fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(walking_lst))], 
		    sorted(aggDataDict.keys()))
    plt.legend()
    plt.savefig(imagefile)
    plt.close()


if __name__ == '__main__':
    # experiment for impact of size on randomized proportion
    xlabel = 'Size of Original data before Randomization'
    ylabel = 'Size proportions of data by label after Randomization'
    imagefile = "sizebyproportion2.png"
    res_map = experimentSizeByProportion()
    draw(res_map, xlabel, ylabel, imagefile)

    # experiment for impact of noise on randomized proportion
    xlabel = 'Noise level'
    ylabel = 'Size proportions of data by label after Randomization'
    imagefile = "noisebyproportion2.png"
    res_map = experimentNoiseByProportion()
    draw(res_map, xlabel, ylabel, imagefile)

