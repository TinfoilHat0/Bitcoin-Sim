#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, r, p, pF, hashFracs, k=16, avgOver=1, blockRewardSetting=(12.5, 12.5) ):
        '''
        n: number of nodes
        r: number of rounds
        p: pr. of the system mining a block in a round
        pF: pr. of the system mining a fruit in a round
        hashFracs: hash rate fraction of each node
        k: maximum hanging distance for a fruit
        avgOver: number of time this simulation runs with corresponding parameters
        '''
        self.n = n
        self.p = p
        self.pF = pF
        self.hashFracs = hashFracs
        self.k = k
        self.r = r
        self.avgOver = avgOver
        self.blockRewardSetting = blockRewardSetting

        self.fairnessLogFTC = []
        self.fairnessLogBTC = []

        self.rewardGapLogBTC = []
        self.rewardGapLogFTC = []

        self.fruitPerBlockLog = []
        self.FTCPerFruitLog = []
        self.FTCPerBlockLog = []
        self.avgGainPerRoundFTCLog = []
        self.avgGainPerRoundBTCLog = []

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.k, self.r, self.blockRewardSetting)
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes)

    def run(self, filename):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            for j in range(1, self.r+1):
                self.environment.step(j)
                if j%50000 == 0:
                    print('Round:' + str(j) + ' has finished.')
            print('Simulation for r=' + str(j) + ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            #self.saveAvgGainPerRoundData()
            #self.saveFruitPerBlockData()
            #self.saveFTCPerFruitData()
            #self.saveFTCPerBlockData()
            self.saveFairnessData()
            self.saveRewardGapData()
        print("All simulations have finished!")
        print('Writing results to file: ' + filename)
        #self.writeAvgGainPerRoundData(filename)
        #self.writeFruitPerBlockData(filename)
        #self.writeFTCPerFruitData(filename)
        #self.writeFTCPerBlockData(filename)
        self.writeFairnessData(filename)
        self.writeRewardGapData(filename)
        print("Finished!")

    def saveAvgGainPerRoundData(self):
        # Avg. gain of a randomly chosen node
        node = random.choice(self.nodes)
        avgGainBTC = node.totalRewardBTC / self.r
        avgGainFTC = node.totalRewardFTC / self.r
        self.avgGainPerRoundBTCLog.append( (avgGainBTC, node.expGainPerRoundBTC) )
        self.avgGainPerRoundFTCLog.append( (avgGainFTC, node.expGainPerRoundFTC) )

    def saveFruitPerBlockData(self):
        fruitPerBlock = self.environment.totalFruitMined / self.environment.totalBlockMined
        self.fruitPerBlockLog.append( (fruitPerBlock, self.environment.expFruitPerBlock) )

    def saveFTCPerFruitData(self):
        FTCPerFruit = self.environment.totalFTCFromFruits / self.environment.totalFruitMined
        self.FTCPerFruitLog.append( (FTCPerFruit, self.environment.expFTCPerFruit) )

    def saveFTCPerBlockData(self):
        FTCPerBlock = self.environment.totalFTCFromBlocks / self.environment.totalBlockMined
        self.FTCPerBlockLog.append( (FTCPerBlock , self.environment.expFTCPerBlock) )

    # Redundant coding.. redundant coding everywhere
    def writeAvgGainPerRoundData(self, filename):
        file = open(filename + "AvgGainPerRoundBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")

        for log in self.avgGainPerRoundBTCLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

        file = open(filename + "AvgGainPerRoundFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")

        for log in self.avgGainPerRoundFTCLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

    def saveRewardGapData(self):
        avgGapBTC, avgGapFTC = 0, 0
        for node in self.nodes:
            avgGapBTC += node.avgRewardGapBTC
            avgGapFTC += node.avgRewardGapFTC
        avgGapBTC /= self.n
        avgGapFTC /= self.n
        self.rewardGapLogBTC.append(avgGapBTC)
        self.rewardGapLogFTC.append(avgGapFTC)

    def saveFairnessData(self):
        distancesBTC, distancesFTC = [], []
        for node in self.nodes:
            fairRewardBTC = self.environment.totalRewardBTC * node.hashFrac
            fairRewardFTC = self.environment.totalRewardFTC * node.hashFrac
            distancesBTC.append( (abs(node.totalRewardBTC - fairRewardBTC) / fairRewardBTC)*100 )
            distancesFTC.append( (abs(node.totalRewardFTC - fairRewardFTC) / fairRewardFTC)*100 )
        self.fairnessLogBTC.append(distancesBTC)
        self.fairnessLogFTC.append(distancesFTC)

    def writeFruitPerBlockData(self, filename):
        file = open(filename + "FruitPerBlock", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")

        for log in self.fruitPerBlockLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

    def writeFTCPerFruitData(self, filename):
        file = open(filename + "RewardPerFruit", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")

        for log in self.FTCPerFruitLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

    def writeFTCPerBlockData(self, filename):
        file = open(filename + "RewardPerBlock", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")

        for log in self.FTCPerBlockLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

    def writeRewardGapData(self, filename):
        # 1. BTC data
        file = open(filename + "RewardGapBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Reward Gap of system \n" )

        for log in self.rewardGapLogBTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()

        # 2.FTC data
        file = open(filename + "RewardGapFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Reward Gap of system \n" )

        for log in self.rewardGapLogFTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()

    def writeFairnessData(self, filename):
        # 1. BTC data
        file = open(filename + "FairnessMetricBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Fairness metric of system\n" )

        for log in self.fairnessLogBTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()

        # 2.FTC data
        file = open(filename + "FairnessMetricFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("#  Fairness metric of system \n" )

        for log in self.fairnessLogFTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()
