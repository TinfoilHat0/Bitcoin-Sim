#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, t, r, p, pF, hashFracs, txRate=5, k=16, avgOver=1):
        '''
        n: number of nodes
        t: number of corrupt nodes
        p: pr. of the system mining a block in a round
        pF: pr. of the system mining a fruit in a round
        hashFracs: hash power fraction of each node
        txRate: number of txs supplied each round
        k: maximum hanging distance for a fruit
        avgOver: number of time this simulation runs with corresponding parameters
        '''
        self.n = n
        self.t = t
        self.r = r
        self.p = p
        self.pF = pF
        self.hashFracs = hashFracs
        self.txRate = txRate
        self.k = k
        self.avgOver = avgOver

        self.rewardLog = defaultdict(list) # <K, V> = ID of node, its statistics
        self.statsLog = [] # log to keep some stats regarding the blockchain

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.txRate, self.k, self.r) # Environment selects a leader each round for mining
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes, self.t)

    def run(self, filename):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            for j in range(1, self.r+1):
                self.environment.step(j)
                if j%50000 == 0:
                    print('Round:' + str(j) + ' has finished.')
            print('Simulation for r='+str(self.r)+ ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            # Save reward related statistics
            for node in self.nodes:
                self.rewardLog[node.id].append( (node.nBlocksMined, node.nFruitsMined, node.totalBitcoinReward, node.totalFruitchainReward) )
            # Save other statistics
            self.statsLog.append( (self.environment.avgFruitPerBlock, self.environment.avgNormalFruitReward, self.environment.avgFTCPerFruit, self.environment.avgFTCPerBlock) )
            self.saveUtilityData(filename)
        print('Writing results to file: ' + filename)
        # self.saveRewardsData(filename)
        # self.saveStatsData(filename)
        print("Finished!")

    def saveRewardData(self, filename):
        file = open(filename + "RewardData", 'w')
        file.write("# n:" + str(self.n) + " t:" + str(self.t) + " r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# id," + "HashFrac," +  "nBlocksMined,"  + "nFruitsMined,"  +  "totalBitcoinReward," + "totalFruitchainReward" + "\n")

        for node in self.environment.nodes:
            avgStats = [0, 0, 0, 0]
            for tmp in self.rewardLog[node.id]:
                for i in range(len(tmp)):
                    avgStats[i] += tmp[i]
            for i in range(len(avgStats)):
                avgStats[i] = ceil(avgStats[i] / self.avgOver)

            file.write(str(node.id) + "," + str(node.hashFrac) + "," + str(avgStats[0]) + ","
            + str(avgStats[1]) + "," + str(avgStats[2]) + "," + str(round(avgStats[3])) + "\n")
        file.close()

    def saveStatsData(self, filename):
        file = open(filename + "StatsData", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Avg. number of fruits per block, Avg. normal fruit reward, Avg. reward per fruit, Avg. reward per block. First line is theoretical expectations." + "\n")

        file.write(str(self.environment.expFruitPerBlock) + "," + str(self.environment.expNormalFruitReward) + "," + str(self.environment.expFTCPerFruit) + "," + str(self.environment.expFTCPerBlock) + "\n")
        for log in self.statsLog:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

    def saveUtilityData(self, filename):
        file = open(filename + "UtilityDataBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(BTC) by round for each node, seperated by commas. First line is thresholds." + "\n")

        thresholds = []
        for node in self.nodes:
            thresholds.append( node.threshold )
        file.write(",".join(map(str, thresholds)) + "\n")
        for i in range(self.r):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogBTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()

        file = open(filename + "UtilityDataFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(FTC) by round for each node, seperated by commas. First line is thresholds." + "\n")

        thresholds = []
        for node in self.nodes:
            thresholds.append( node.threshold )
        file.write(",".join(map(str, thresholds)) + "\n")
        for i in range(self.r):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogFTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()
