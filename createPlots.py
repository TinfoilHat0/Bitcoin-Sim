import numpy as np
import matplotlib.pyplot as plt



def plotFairness(filename):
    return

def plotStability(filename):
    """
    row format: distance from expected round to pass threshold in terms of % for node_1, .., node_n for sim i
    """
    logBTC = np.loadtxt(filename + "StabilityDataBTC", delimiter=",")
    stdDevsBTC = []
    for log in logBTC:
        stdDevsBTC.append( np.var(log) ** (1/2) )

    logFTC = np.loadtxt(filename + "StabilityDataFTC", delimiter=",")
    stdDevsFTC = []
    for log in logFTC:
        stdDevsFTC.append( np.var(log) ** (1/2) )

    plt.figure(figsize=(10,10))
    plt.plot(stdDevsBTC, '-y', label='BTC')
    plt.plot(stdDevsFTC, '-g', label='FTC')
    plt.xlabel("Simulations")
    plt.ylabel("Standard Deviation")
    plt.legend()
    plt.savefig(filename + "stdDev.png")
    plt.close()


def plotUtility(filename):
    """
        First line is thresholds: thresholdOfNode1,.., thresholdOfNodeN
        row format: utilityOfNode1, .., utilityofNodeN
    """
    # 1. Extract data
    log = np.loadtxt(filename + "UtilityDataBTC", delimiter=",")
    nNodes = len(log[0])
    colors = ['-r', '-g', '-b']

    utilityValsBTC = [ [] for i in range(nNodes) ]
    thresholdsBTC, expRoundsBTC = log[0], log[1]
    for row in log[2:]:
        for i in range(nNodes):
            utilityValsBTC[i].append(row[i])

    log = np.loadtxt(filename + "UtilityDataFTC", delimiter=",")
    thresholdsFTC, expRoundsFTC = log[0], log[1]
    utilityValsFTC = [ [] for i in range(nNodes) ]
    for row in log[2:]:
        for i in range(nNodes):
            utilityValsFTC[i].append(row[i])

    # 2. Plot data
    plt.figure(figsize=(10,10))
    # -- plotting vertical expected rounds line
    for i in range(len(expRoundsBTC)):
        plt.axvline(x=expRoundsBTC[i], color='k', linestyle='-')
    # -- plotting horizontal threshold line
    for i in range(len(thresholdsBTC)):
        plt.axhline(y=thresholdsBTC[i], color='k', linestyle='-')
    # -- plotting utility value vs. rounds
    for i in range(len(utilityValsBTC)):
        plt.plot(utilityValsBTC[i], colors[i%3], label='Node_' + str(i) )
    # -- legend of plot
    plt.xlabel("Rounds")
    plt.ylabel("Value of utility")
    plt.legend()
    plt.savefig(filename + "BTCUtility.png")
    plt.close()

    plt.figure(figsize=(10,10))
    # -- plotting vertical expected rounds line
    for i in range(len(expRoundsFTC)):
        plt.axvline(x=expRoundsFTC[i], color='k', linestyle='-')
    # -- plotting horizontal threshold line
    for i in range(len(thresholdsFTC)):
        plt.axhline(y=thresholdsFTC[i], color='k', linestyle='-')
    # -- plotting utility value vs. rounds
    for i in range(len(utilityValsFTC)):
        plt.plot(utilityValsFTC[i], colors[i%3], label='Node_' + str(i) )
    # -- legend of plot
    plt.xlabel("Rounds")
    plt.ylabel("Value of utility")
    plt.legend()
    plt.savefig(filename + "FTCUtility.png")
    plt.close()
