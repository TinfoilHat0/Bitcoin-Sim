import numpy as np
import matplotlib.pyplot as plt

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


    # 1. Plot txs
    plt.figure(figsize=(10,10))
    plt.plot(processedTxs, '-b', label='Processed Txs')
    plt.plot(unprocessedTxs, '-r', label='Unprocessed Txs')
    plt.xlabel("Rounds")
    plt.ylabel("Number of Txs")
    plt.legend()
    plt.savefig(filename + "_txs.png")
    plt.close()


    # 2. Plot miningPool fractions
    plt.figure(figsize=(10,10))
    plt.plot(soloFrac, '-b', label='Solo Miners')
    plt.plot(miningPoolFrac, '-r', label='Mining Pool')
    plt.xlabel("Rounds")
    plt.ylabel("Hash Power Fraction")
    plt.legend()
    plt.savefig(filename + "_pool.png")
    plt.close()

    # 3. Plot BitcoinReward vs FruitchainReward
    plt.figure(figsize=(10,10))
    plt.plot(bitcoinReward, '-b', label='Bitcoin Reward')
    plt.plot(fruitchainReward, '-r', label='Fruitchain Reward')
    plt.xlabel("Rounds")
    plt.ylabel("Amount of Reward")
    plt.legend()
    plt.savefig(filename + "_bitcoinVsFruitchain.png")
    plt.close()


def plotMinerRewards(filename):
    """ file format: (minerID, hashFracs, rewards) """
    plt.figure(figsize=(10,10))
    filename += "_rewards"
    log = np.loadtxt(filename, delimiter=",")

    hashFracs = []
    bitcoinRewards = []
    fruitchainRewards = []

    for item in log:
        hashFracs.append(item[1])
        bitcoinRewards.append(item[2])
        fruitchainRewards.append(item[3])

    totalBitcoinReward = sum(bitcoinRewards)
    bitcoinRewards = [i/totalBitcoinReward for i in bitcoinRewards]

    totalFruitchainReward = sum(fruitchainRewards)
    fruitchainRewards = [i/totalFruitchainReward for i in fruitchainRewards]

    N = len(hashFracs)
    ind = np.arange(N)
    width = 0.3
    fig = plt.figure()
    ax = fig.add_subplot(111)

    rects1 = ax.bar(ind, hashFracs, width, color='r')
    rects2 = ax.bar(ind+width, bitcoinRewards, width, color='y')
    rects3 = ax.bar(ind+width*2, fruitchainRewards, width, color='g')

    ax.set_ylabel('Fraction')
    ax.set_xlabel('Miners IDs')
    ax.set_xticks(ind+width)

    ax.set_xticklabels( [i for i in range(N)] )
    ax.legend( (rects1[0], rects2[0], rects3[0]), ('HashPow', 'BitcoinReward', 'FruitReward'),
    bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, str(round(h, 2)),
                    ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.savefig(filename + "_hashPowVsRewards.png")
