import numpy as np
import math
import matplotlib.pyplot as plt


def plotHashFracsLog(filename, hashFracsLog):
    ctr = 0
    for hashFracs in hashFracsLog:
        ctr2 = 1
        minerIDs, tmp = [], []
        for hashFrac in hashFracs:
            if hashFrac != 0:
                minerIDs.append(ctr2)
                tmp.append(hashFrac)
            ctr2 += 1
        labels = ['Miner' + str(id) for id in minerIDs]
        plt.pie(tmp, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.savefig(filename + 'hashFracs_' + str(ctr) + '.png')
    plt.close()


def plotStabilityMetric(lengths=[], hashSettings=[]):
    """
    row format: stability metric
    """
    filename = "sim_results/metricTests/"
    # 1. length tests
    fName = filename + "lengthTests/"
    metricLengthBTC, metricLengthFTC = [], []
    for length in lengths:
        btcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "StabilityMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "length_" + str(length) + "_" + "StabilityMetricFTC", delimiter=",")
        metricLengthBTC.append( sum(btcLog) / len(btcLog) )
        metricLengthFTC.append( sum(ftcLog) / len(ftcLog) )
    # 2. hashSettings tests
    fName = filename + "hashTests/"
    metricHashBTC, metricHashFTC = [], []
    for i in range(len(hashSettings)):
        btcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "StabilityMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "hashSetting_" + str(i+1) + "_" + "StabilityMetricFTC", delimiter=",")
        metricHashBTC.append( sum(btcLog) / len(btcLog) )
        metricHashFTC.append( sum(ftcLog) / len(ftcLog) )

    # 1. Plot length tests
    if len(lengths) > 0:
        plt.figure(figsize=(8,8))
        xi = [i for i in range(len(lengths))]
        #plt.ylim(0, 2 * max(metricLengthBTC))
        plt.plot(xi, metricLengthBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricLengthFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, lengths)
        plt.xlabel("Window Length(days)")
        plt.ylabel("Stability Metric")
        plt.legend()
        plt.savefig(filename + "stabilityMetricLength.png")
        plt.close()
    # 2. Plot hash fraction setting tests
    if len(hashSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(hashSettings))]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricHashBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricHashFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Hash Rate Setting ID")
        plt.ylabel("Stability Metric")
        plt.legend()
        plt.savefig(filename + "stabilityMetricHashSetting.png")
        plt.close()

def plotFairnessMetric(lengths=[], hashSettings=[]):
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

    # 1. Plot length tests
    if len(lengths) > 0:
        # 1. Plot length tests
        plt.figure(figsize=(8,8))
        xi = [i for i in range(len(lengths))]
        #plt.ylim(0, 2 * max(metricLengthBTC))
        plt.plot(xi, metricLengthBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricLengthFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, lengths)
        plt.xlabel("Window Length(days)")
        plt.ylabel("Fairness Metric")
        plt.legend()
        plt.savefig(filename + "fairnessMetricLength.png")
        plt.close()
    # 2. Plot hash fraction setting tests
    if len(hashSettings) > 0:
        plt.figure(figsize=(8,8))
        xi = [i+1 for i in range(len(hashSettings))]
        #plt.ylim(0, 2 * max(metricHashBTC))
        plt.plot(xi, metricHashBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
        plt.plot(xi, metricHashFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
        plt.xticks(xi, xi)
        plt.xlabel("Hash Rate Setting ID")
        plt.ylabel("Fairness Metric")
        plt.legend()
        plt.savefig(filename + "fairnessMetricHashSetting.png")
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
        # 4. avg reward per round FTC
        sm, expected = 0, 0
        log = np.loadtxt(fName + "c0_" + str(c0) + "_" + "AvgGainPerRoundFTC", delimiter=",")
        for data in log:
            sm += data[0]
        measuredAvgGainPerRoundFTC.append( sm/len(log) )
        expectedAvgGainPerRoundFTC.append( log[0][0] )
        # 5. avg reward per round BTC
        sm, expected = 0, 0
        log = np.loadtxt(fName + "c0_" + str(c0) + "_" + "AvgGainPerRoundBTC", delimiter=",")
        for data in log:
            sm += data[0]
        measuredAvgGainPerRoundBTC.append( sm/len(log) )
        expectedAvgGainPerRoundBTC.append( log[0][0] )




    # Plot AvgGainPerRoundFTC
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, measuredAvgGainPerRoundFTC, marker='o', linestyle='--', color='r', label='Measured')
    plt.plot(xi, expectedAvgGainPerRoundFTC, marker='o', linestyle='--', color='b', label='Expected')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Avg. gain per round (BTC)")
    plt.legend()
    plt.savefig(fName + "AvgGainPerRoundFTC.png")
    plt.close()

    # Plot AvgGainPerRoundFTC
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    # plt.ylim(0, 2 * max(expectedFruitPerBlock))
    plt.plot(xi, measuredAvgGainPerRoundBTC, marker='o', linestyle='--', color='r', label='Measured')
    plt.plot(xi, expectedAvgGainPerRoundBTC, marker='o', linestyle='--', color='b', label='Expected')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Avg. gain per round (BTC)")
    plt.legend()
    plt.savefig(fName + "AvgGainPerRoundBTC.png")
    plt.close()

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
