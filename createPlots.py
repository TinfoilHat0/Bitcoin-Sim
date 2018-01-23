import numpy as np
import math
import matplotlib.pyplot as plt


def plotFairnessMetric(filename):
    """
    row format: ratio of distance from expected share of reward for  node_1, .. , node_n

    calculate the fairness metric, i.e, std.dev of rows
    """
    # 1. fairness metric for btc
    logBTC = np.loadtxt(filename + "FairnessDataBTC", delimiter=",")
    stdDevsBTC = []
    for distances in logBTC:
        stdDevsBTC.append( np.var(distances) ** (1/2) )
    # 2. fairness metric for ftc
    logFTC = np.loadtxt(filename + "FairnessDataFTC", delimiter=",")
    stdDevsFTC = []
    for distances in logFTC:
        stdDevsFTC.append( np.var(distances) ** (1/2) )
    # 3. plot both in a plot
    plt.figure(figsize=(10,10))
    plt.plot(stdDevsBTC, '-y', label='Bitcoin')
    plt.plot(stdDevsFTC, '-g', label='Fruitchain')
    plt.xlabel("Simulations")
    plt.ylabel("Fairness Metric")
    plt.legend()
    plt.savefig(filename + "fairnessMetric.png")
    plt.close()

def plotStabilityMetric(filename):
    """
    row format: variance of ratio of distance from expected utility value for node_1,..,node_n

    calculate the stability metric, i.e, average std. deviation of rows
    """
    # 1. fairness metric for btc
    logBTC = np.loadtxt(filename + "StabilityDataBTC", delimiter=",")
    avgStdDevBTC = []
    for variances in logBTC:
        avgStdDevBTC.append( np.mean(variances) )
    np.sqrt(avgStdDevBTC)
    # 2. fairness metric for ftc
    logFTC = np.loadtxt(filename + "StabilityDataFTC", delimiter=",")
    avgStdDevFTC = []
    for variances in logFTC:
        avgStdDevFTC.append( np.mean(variances) )
    np.sqrt(avgStdDevBTC)
    # 3. plot both in a plot
    plt.figure(figsize=(10,10))
    plt.plot(avgStdDevBTC, '-y', label='Bitcoin')
    plt.plot(avgStdDevFTC, '-g', label='Fruitchain')
    plt.xlabel("Simulations")
    plt.ylabel("Stability Metric")
    plt.legend()
    plt.savefig(filename + "stabilitiyMetric.png")
    plt.close()
