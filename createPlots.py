import numpy as np
import math
import matplotlib.pyplot as plt

# Figure details
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

def plotReward(BTCReward, FTCReward, Cost):

    xi = [i for i in range(len(Cost))]

    profitBTC, profitFTC = [], []
    for i in range(len(BTCReward)):
        profitBTC.append( BTCReward[i] - Cost[i] )
        profitFTC.append( FTCReward[i] - Cost[i] )

    plt.figure(figsize=(8,8))
    plt.plot(xi, BTCReward, color='g', label='Gain')
    plt.plot(xi, Cost, color='r', label='Cost')
    plt.plot(xi, profitBTC, color='orange', label='Profit')
    plt.xlabel("Rounds")
    plt.ylabel("BTC")
    plt.legend()
    plt.savefig("BTC Profit")
    plt.close()

    plt.figure(figsize=(8,8))
    plt.plot(xi, FTCReward, color='g', label='Gain')
    plt.plot(xi, Cost, color='r', label='Cost')
    plt.plot(xi, profitFTC, color='orange', label='Profit')
    plt.xlabel("Rounds")
    plt.ylabel("BTC")
    plt.legend()
    plt.savefig("FTC Profit")
    plt.close()



def plotFairnessMetric(lengths=[], hashSettings=[], blockSettings=[]):
    """
    row format: fairnessMetric
    """
    filename = "sim_results/metricTests/"
    # 1. length tests
    fName = filename + "lengthTests/"
    metricLengthBTC, metricLengthFTC = [], []
    for length in lengths:
        btcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "FairnessMetricFTC", delimiter=",")
        metricLengthBTC.append(sum(btcLog) / len(btcLog))
        metricLengthFTC.append(sum(ftcLog) / len(ftcLog))
    # 2. hashSettings tests
    fName = filename + "hashTests/"
    metricHashBTC, metricHashFTC = [], []
    for i in range(len(hashSettings)):
        btcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "FairnessMetricFTC", delimiter=",")
        metricHashBTC.append(sum(btcLog) / len(btcLog))
        metricHashFTC.append(sum(ftcLog) / len(ftcLog))
    # 3. blockSettings tests
    fName = filename + "blockTests/"
    metricBlockBTC, metricBlockFTC = [], []
    for i in range(len(blockSettings)):
        btcLog = np.loadtxt(fName + "blockSetting_" + str(i+1) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "blockSetting_" + str(i+1) + "_" + "FairnessMetricFTC", delimiter=",")
        metricBlockBTC.append(sum(btcLog) / len(btcLog))
        metricBlockFTC.append(sum(ftcLog) / len(ftcLog))

    # 1. Plot length tests
    if len(lengths) > 0:
        # 1. Plot length tests
        plt.figure(figsize=(8,8))
        xi = [i for i in range(len(lengths))]
        #plt.ylim(0, 2 * max(metricLengthBTC))
        plt.plot(xi, metricLengthBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricLengthFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, lengths)
        plt.xlabel("Interval Length (rounds)")
        plt.ylabel("Unfairness Metric")
        plt.legend()
        plt.savefig(filename + "UnfairnessLength.png")
        plt.close()
    # 2. Plot hash fraction setting tests
    if len(hashSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(hashSettings))]
        #devs = [round(math.sqrt(np.var(setting)), 2) for setting in hashSettings]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricHashBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricHashFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Hash Setting ID")
        plt.ylabel("Unfairness Metric")
        plt.legend()
        plt.savefig(filename + "UnfairnessHashSetting.png")
        plt.close()
    # 3. Plot block reward settings tests
    if len(blockSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(blockSettings))]
        #devs = [round(math.sqrt(np.var(setting)), 2) for setting in blockSettings]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricBlockBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricBlockFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Block Reward Setting ID")
        plt.ylabel("Unfairness Metric")
        plt.legend()
        plt.savefig(filename + "UnfairnessBlockSetting.png")
        plt.close()

def plotSustainabilityMetric(lengths=[], hashSettings=[], blockSettings=[]):
    """
    row format: sustainability metric
    """
    filename = "sim_results/metricTests/"
    # 1. length tests
    fName = filename + "lengthTests/"
    metricLengthBTC, metricLengthFTC = [], []
    for length in lengths:
        btcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "SustainabilityMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "SustainabilityMetricFTC", delimiter=",")
        metricLengthBTC.append( sum(btcLog) / len(btcLog) )
        metricLengthFTC.append( sum(ftcLog) / len(ftcLog) )
    # 2. hashSettings tests
    fName = filename + "hashTests/"
    metricHashBTC, metricHashFTC = [], []
    for i in range(len(hashSettings)):
        btcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "SustainabilityMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "SustainabilityMetricFTC", delimiter=",")
        metricHashBTC.append( sum(btcLog) / len(btcLog) )
        metricHashFTC.append( sum(ftcLog) / len(ftcLog) )
    # 3. blockSettings tests
    fName = filename + "blockTests/"
    metricBlockBTC, metricBlockFTC = [], []
    for i in range(len(blockSettings)):
        btcLog = np.loadtxt(fName + "blockSetting_" + str(i+1) + "_" + "SustainabilityMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "blockSetting_" + str(i+1) + "_" + "SustainabilityMetricFTC", delimiter=",")
        metricBlockBTC.append( sum(btcLog) / len(btcLog) )
        metricBlockFTC.append( sum(ftcLog) / len(ftcLog) )

    # 1. Plot length tests
    if len(lengths) > 0:
        plt.figure(figsize=(8,8))
        xi = [i for i in range(len(lengths))]
        #plt.ylim(0, 2 * max(metricLengthBTC))
        plt.plot(xi, metricLengthBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricLengthFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, lengths)
        plt.xlabel("Interval Length (rounds)")
        plt.ylabel("Profitability Metric")
        plt.legend()
        plt.savefig(filename + "ProfLength.png")
        plt.close()
    # 2. Plot hash fraction setting tests
    if len(hashSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(hashSettings))]
        #devs = [round(math.sqrt(np.var(setting)), 2) for setting in hashSettings]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricHashBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricHashFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Hash Setting ID")
        plt.ylabel("Profitability Metric")
        plt.legend()
        plt.savefig(filename + "ProfHashSetting.png")
        plt.close()
    # 3. Plot block reward settings tests
    if len(blockSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(blockSettings))]
        #devs = [math.sqrt(np.var(setting)) for setting in blockSettings]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricBlockBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricBlockFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Block Reward Setting ID")
        plt.ylabel("Profitability Metric")
        plt.legend()
        plt.savefig(filename + "ProfBlockSetting.png")
        plt.close()
