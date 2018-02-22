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


def plotSelfishMining(hashFracs, rewardFracBTC, rewardFracFTC):
    fName = "sim_results/selfishMiningTests/"
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(hashFracs))]
    yi = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, rewardFracBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
    plt.plot(xi, rewardFracFTC, marker='o', color='b', label='Fruitchain')
    plt.xticks(xi, hashFracs)
    plt.yticks(yi, yi)
    plt.xlabel("Hashrate fraction of selfish-miner")
    plt.ylabel("Reward fraction of selfish-miner")
    plt.legend()
    plt.savefig(fName + "SelfishMining.png")
    plt.close()


def plotValidationData(c0Vals):
    """
    Inputs are required params. to calculate theoretical fit
    row format: fairnessMetric
    """
    fName = "sim_results/validationTests/"
    # 1. Collect data
    measuredFruitPerBlock, expectedFruitPerBlock = [], []
    measuredFTCPerFruit, expectedFTCPerFruit = [], []
    measuredFTCPerBlock, expectedFTCPerBlock = [], []
    measuredAvgGainPerRoundFTC, expectedAvgGainPerRoundFTC = [], []
    measuredAvgGainPerRoundBTC, expectedAvgGainPerRoundBTC = [], []
    for c0 in c0Vals:
        # 1. FruitPerBlock
        sm, expected = 0, 0
        log = np.loadtxt(fName + "c0_" + str(c0) + "_" + "FruitPerBlock", delimiter=",")
        for data in log:
            sm += data[0]
        measuredFruitPerBlock.append( sm/len(log) )
        expectedFruitPerBlock.append( log[0][0] )
        # 2. RewardPerFruit
        sm, expected = 0, 0
        log = np.loadtxt(fName + "c0_" + str(c0) + "_" + "RewardPerFruit", delimiter=",")
        for data in log:
            sm += data[0]
        measuredFTCPerFruit.append( sm/len(log) )
        expectedFTCPerFruit.append( log[0][0] )
        # 3. RewardPerBlock
        sm, expected = 0, 0
        log = np.loadtxt(fName + "c0_" + str(c0) + "_" + "RewardPerBlock", delimiter=",")
        for data in log:
            sm += data[0]
        measuredFTCPerBlock.append( sm/len(log) )
        expectedFTCPerBlock.append( log[0][0] )

    #  Plot FruitPerBlock
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, measuredFruitPerBlock, marker='o', linestyle='--', color='r', label='Measured')
    plt.plot(xi, expectedFruitPerBlock, marker='o', linestyle='--', color='b', label='Expected')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Avg. number of fruits per block")
    plt.legend()
    plt.savefig(fName + "FruitPerBlock.png")
    plt.close()

    # Plot RewardPerFruit
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, measuredFTCPerFruit, marker='o', linestyle='--', color='r', label='Measured')
    plt.plot(xi, expectedFTCPerFruit, marker='o', linestyle='--', color='b', label='Expected')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Reward per fruit (BTC)")
    plt.legend()
    plt.savefig(fName + "RewardPerFruit.png")
    plt.close()

    #  Plot RewardPerFruit
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, measuredFTCPerBlock, marker='o', linestyle='--', color='r', label='Measured')
    plt.plot(xi, expectedFTCPerBlock, marker='o', linestyle='--', color='b', label='Expected')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Reward per block (BTC)")
    plt.legend()
    plt.savefig(fName + "RewardPerBlock.png")
    plt.close()


def plotSustainabilityMetric():
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
        plt.xlabel("Number of Rounds")
        plt.ylabel("Sustainability Metric")
        plt.legend()
        plt.savefig(filename + "SustainabilityLength.png")
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
        plt.ylabel("Sustainability Metric")
        plt.legend()
        plt.savefig(filename + "SustainabilityHashSetting.png")
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
        plt.ylabel("Sustainability Metric")
        plt.legend()
        plt.savefig(filename + "SustainabilityBlockSetting.png")
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
        plt.xlabel("Number of Rounds")
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
