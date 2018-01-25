import numpy as np
import math
import matplotlib.pyplot as plt


def plotFairnessMetric(lengths, c0Vals, hashSettings):
    """
    row format: fairnessMetric
    """
    filename = "sim_results/fairnessTests"
    # 1. length tests
    fName = filename + "lengthTests/"
    metricLengthBTC, metricLengthFTC = [], []
    for length in lengths:
        btcLog = np.loadtxt(fName + "length" + str(length) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "length" + str(length) + "_" + "FairnessMetricFTC", delimiter=",")
        metricLengthBTC.append(sum(btcLog) / len(btcLog))
        metricLengthFTC.append(sum(ftcLog) / len(ftcLog))
    # 2. c0 tests
    fName = filename + "c0Tests/"
    metricC0BTC, metricC0FTC = [], []
    for c0 in c0Vals:
        btcLog = np.loadtxt(fName + "c0" + str(c0) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "c0" + str(c0) + "_" + "FairnessMetricFTC", delimiter=",")
        metricC0BTC.append(sum(btcLog) / len(btcLog))
        metricC0FTC.append(sum(ftcLog) / len(ftcLog))
    # 3. hashSettings tests
    fName = filename + "hashFracTests/"
    metricHashBTC, metricHashFTC = [], []
    for i in range(len(hashSettings)):
        btcLog = np.loadtxt(fName + "hashSetting" + str(i) + "_" + "FairnessMetricBTC", delimiter=",")
        ftcLog = np.loadtxt(fName + "hashSetting" + str(i) + "_" + "FairnessMetricFTC", delimiter=",")
        metricHashBTC.append(sum(btcLog) / len(btcLog))
        metricHashFTC.append(sum(ftcLog) / len(ftcLog))


    # 1. Plot length tests
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(lengths))]
    plt.ylim(0, 2 * max(metricLengthBTC))
    plt.plot(xi, metricLengthBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
    plt.plot(xi, metricLengthFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
    plt.xticks(xi, lengths)
    plt.xlabel("Window Length(days)")
    plt.ylabel("Fairness Metric")
    plt.legend()
    plt.savefig(filename + "fairnessMetricLength.png")
    plt.close()
    # 2. Plot c0 tests
    plt.figure(figsize=(8,8))
    xi = [i for i in range(len(c0Vals))]
    plt.ylim(0, 2 * max(metricC0BTC))
    plt.plot(xi, metricC0BTC, marker='o', linestyle='--', color='r', label='Bitcoin')
    plt.plot(xi, metricC0FTC, marker='o', linestyle='--', color='b', label='Fruitchain')
    plt.xticks(xi, c0Vals)
    plt.xlabel("$c_0$")
    plt.ylabel("Fairness Metric")
    plt.legend()
    plt.savefig(filename + "fairnessMetricC0.png")
    plt.close()
    # 3. Plot hash fraction setting tests
    plt.figure(figsize=(8,8))
    xi = [i+1 for i in range(len(hashSettings))]
    plt.ylim(0, 2 * max(metricHashBTC))
    plt.plot(xi, metricHashBTC, marker='o', linestyle='--', color='r', label='Bitcoin')
    plt.plot(xi, metricHashFTC, marker='o', linestyle='--', color='b', label='Fruitchain')
    plt.xticks(xi, xi)
    plt.xlabel("Hash Rate Setting ID")
    plt.ylabel("Fairness Metric")
    plt.legend()
    plt.savefig(filename + "fairnessMetricHashSetting.png")
    plt.close()

def plotFruitPerBlockData(p=1/100, pF=1/10):
    """
    Inputs are required params. to calculate theoretical fit
    row format: fairnessMetric
    """
    filename = "sim_results/validationTests/ValidationData"
    log = np.loadtxt(filename, delimiter=",")
    fruitsPerBlock = []
    for data in log:
        fruitsPerBlock.append(data)

    fruitsPerBlock = np.asarray(fruitsPerBlock)
    sampleStdDev = np.var(fruitsPerBlock) ** 0.5
    mean = np.mean(fruitsPerBlock)
    expected = pF / p

    plt.figure(figsize=(8,8))
    xi = [i+1 for i in range(len(fruitsPerBlock))]
    plt.ylim(0, 2 * expected)
    plt.plot(xi, [expected for i in range(len(xi))], marker='o', color='b', label='Expected')
    plt.plot(xi, fruitsPerBlock, marker='o', color='r', label='Measured')
    plt.xticks(xi, xi)
    plt.xlabel("Simulation runs")
    plt.ylabel("Avg. number of fruits per block")
    plt.legend()
    plt.savefig(filename + "perBlock.png")
    plt.close()
