import numpy as np
import matplotlib.pyplot as plt


def plotUtility(filename):
    """
        First line is thresholds: thresholdOfNode1,.., thresholdOfNodeN
        row format: utilityOfNode1, .., utilityofNodeN
    """
    # 1. Extract data
    log = np.loadtxt(filename + "UtilityDataBTC", delimiter=",")
    nNodes = len(log[0])
    colors = ['-r', '-g', '-b']
    thresholds = []

    utilityValsBTC = [ [] for i in range(nNodes) ]
    thresholds = log[0]
    for row in log[1:]:
        for i in range(nNodes):
            utilityValsBTC[i].append(row[i])

    log = np.loadtxt(filename + "UtilityDataFTC", delimiter=",")
    thresholds = []
    utilityValsFTC = [ [] for i in range(nNodes) ]
    thresholds = log[0]
    for row in log[1:]:
        for i in range(nNodes):
            utilityValsFTC[i].append(row[i])

    # 2. Plot data
    plt.figure(figsize=(10,10))
    for i in range(len(thresholds)):
        plt.axhline(y=thresholds[i], color='k', linestyle='-')
    for i in range(len(utilityValsBTC)):
        plt.plot(utilityValsBTC[i], colors[i%3], label='Node_' + str(i) )
    plt.xlabel("Rounds")
    plt.ylabel("Value of utility")
    plt.legend()
    plt.savefig(filename + "BTCUtility.png")
    plt.close()

    plt.figure(figsize=(10,10))
    for i in range(len(thresholds)):
        plt.axhline(y=thresholds[i], color='k', linestyle='-')
    for i in range(len(utilityValsFTC)):
        plt.plot(utilityValsFTC[i], colors[i%3], label='Node_' + str(i) )
    plt.xlabel("Rounds")
    plt.ylabel("Value of utility")
    plt.legend()
    plt.savefig(filename + "FTCUtility.png")
    plt.close()


def plotStats(filename):
    """
        row format: fruitPerBlock, normalFruitReward
        with first row being theoretical expectations
    """
    log = np.loadtxt(filename + "StatsData", delimiter=",")

    measuredFruitPerBlock = []
    measuredNormalFruitReward = []
    measuredRewardPerFruit = []
    measuredRewardPerBlock = []

    expectedFruitPerBlock = []
    expectedNormalFruitReward = []
    expectedRewardPerFruit = []
    expectedRewardPerBlock = []


    for row in log[1:]:
        measuredFruitPerBlock.append(row[0])
        measuredNormalFruitReward.append(row[1])
        measuredRewardPerFruit.append(row[2])
        measuredRewardPerBlock.append(row[3])

        expectedFruitPerBlock.append(log[0][0])
        expectedNormalFruitReward.append(log[0][1])
        expectedRewardPerFruit.append(log[0][2])
        expectedRewardPerBlock.append(log[0][3])


    plt.figure(figsize=(10,10))
    axes = plt.gca()
    axes.set_ylim([0, 3*expectedFruitPerBlock[0]])
    #axes.set_xlim([1, len(expectedFruitPerBlock)])
    plt.plot(expectedFruitPerBlock, '-b', label='Expected')
    plt.plot(measuredFruitPerBlock, '-r', label='Measured')
    plt.xlabel("Experiments")
    plt.ylabel("Fruits per block")
    plt.legend()
    plt.savefig(filename + "Lemma3.png")
    plt.close()

    plt.figure(figsize=(10,10))
    axes = plt.gca()
    axes.set_ylim([0, 3*expectedNormalFruitReward[0]])
    #axes.set_xlim([1, len(expectedNormalFruitReward)])
    plt.plot(expectedNormalFruitReward, '-b', label='Expected')
    plt.plot(measuredNormalFruitReward, '-r', label='Measured')
    plt.xlabel("Experiments")
    plt.ylabel("Normal reward per fruit")
    plt.legend()
    plt.savefig(filename + "Corollary2.png")
    plt.close()

    plt.figure(figsize=(10,10))
    axes = plt.gca()
    axes.set_ylim([0, 3*expectedRewardPerFruit[0]])
    #axes.set_xlim([1, len(expectedRewardPerFruit)])
    plt.plot(expectedRewardPerFruit, '-b', label='Expected')
    plt.plot(measuredRewardPerFruit, '-r', label='Measured')
    plt.xlabel("Experiments")
    plt.ylabel("Reward per fruit")
    plt.legend()
    plt.savefig(filename + "Lemma4.png")
    plt.close()

    plt.figure(figsize=(10,10))
    axes = plt.gca()
    axes.set_ylim([0, 3*expectedRewardPerBlock[0]])
    #axes.set_xlim([1, len(expectedRewardPerBlock)])
    plt.plot(expectedRewardPerBlock, '-b', label='Expected')
    plt.plot(measuredRewardPerBlock, '-r', label='Measured')
    plt.xlabel("Experiments")
    plt.ylabel("Reward per block")
    plt.legend()
    plt.savefig(filename + "Lemma5.png")
    plt.close()



def plotMinerRewards(filename):
    """ file format: (minerID, hashFracs, nBlocksMined, bitcoinReward, fruitchainRewards) """
    log = np.loadtxt(filename + "_rewards", delimiter=",")

    hashFracs = []
    blocksMined = []
    fruitsMined = []
    bitcoinRewards = []
    fruitchainRewards = []

    for item in log:
        hashFracs.append(item[1])
        blocksMined.append(item[2])
        fruitsMined.append(item[3])
        bitcoinRewards.append(item[4])
        fruitchainRewards.append(item[5])

    totalBlocksMined = sum(blocksMined)
    blocksMined = [i/totalBlocksMined for i in blocksMined]

    totalFruitsMined = sum(fruitsMined)
    fruitsMined = [i/totalFruitsMined for i in fruitsMined]

    totalBTCReward = sum(bitcoinRewards)
    bitcoinRewards = [i/totalBTCReward for i in bitcoinRewards]

    totalFTCReward = sum(fruitchainRewards)
    fruitchainRewards = [i/totalFTCReward for i in fruitchainRewards]

    N = len(hashFracs)
    ind = np.arange(N)
    width = 0.1
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)

    rects1 = ax.bar(ind, hashFracs, width, color='r')
    rects2 = ax.bar(ind+width, blocksMined, width, color='b')
    rects3 = ax.bar(ind+width*2, blocksMined, width, color='g')
    rects4 = ax.bar(ind+width*3, bitcoinRewards, width, color='y')
    rects5 = ax.bar(ind+width*4, fruitchainRewards, width, color='m')

    ax.set_ylabel('Fraction')
    ax.set_xlabel('Miners IDs')
    ax.set_xticks(ind+width)

    ax.set_xticklabels( [i for i in range(N)] )
    ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('HashPow', 'BlocksMined', 'FruitsMined', 'BitcoinReward', 'FruitReward'),
    bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, str(round(h, 2)),
            ha='center', va='bottom')

    plt.savefig(filename + "_rewards.png", bbox_inches='tight')

    # Also calculate unfairness metric for both rewarding schemes
    unFairnessBitcoin, unFairnessFruit = 0, 0
    for i in range(len(hashFracs)):
        unFairnessBitcoin += abs(hashFracs[i] - bitcoinRewards[i])
        unFairnessFruit += abs(hashFracs[i] - fruitchainRewards[i])

    with open(filename + "fairnessMetric", "a") as myfile:
        myfile.write(str(unFairnessBitcoin) + "," + str(unFairnessFruit) + "\n")

def plotStatistics(filename):
    """ file format: (roundNum, nUnprocessed, nProcessed) """
    filename += "_stats"
    log = np.loadtxt(filename, delimiter=",")

    unprocessedTxs = []
    processedTxs = []

    miningPoolFrac = []
    soloFrac = []

    bitcoinReward = []
    fruitchainReward = []

    for item in log:
        unprocessedTxs.append(item[1])
        processedTxs.append(item[2])

        miningPoolFrac.append(item[3])
        soloFrac.append(1-item[3])

        bitcoinReward.append(item[4])
        fruitchainReward.append(item[5])

    plt.figure(figsize=(10,10))
    plt.plot(processedTxs, '-b', label='Processed Txs')
    plt.plot(unprocessedTxs, '-r', label='Unprocessed Txs')
    plt.xlabel("Rounds")
    plt.ylabel("Number of Txs")
    plt.legend()
    plt.savefig(filename + "_txs.png")
    plt.close()

def plotFairnessMetric(filename):
    """ file format: (FairnessMetricBitcoin, FairnessMetricFruitchain) """
    log = np.loadtxt(filename + "fairnessMetric", delimiter=",")
    fairnessBitcoin = []
    fairnessFruit = []

    for item in log:
        fairnessBitcoin.append(item[0])
        fairnessFruit.append(item[1])

    plt.figure(figsize=(10,10))
    plt.plot(fairnessBitcoin, '-y', label='Bitcoin')
    plt.plot(fairnessFruit, '-g', label='Fruitchain')
    plt.xlabel("Reward variance")
    plt.ylabel("Value of metric")
    plt.legend()
    plt.savefig(filename + "FairnessMetric.png")
    plt.close()
