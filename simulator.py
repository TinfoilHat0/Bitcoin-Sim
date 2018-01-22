#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, r, p, pF, hashFracs, k=16, avgOver=1):
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
        self.r = f
        self.avgOver = avgOver
        self.r = 1

        self.fairnessLogBTC = []
        self.fairnessLogFTC = []

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.k, self.r)
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes)
        self.r = 1

    def run(self, filename):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            for j in range(1, self.r+1):
                self.environment.step(j)
                if j%50000 == 0:
                    print('Round:' + str(j) + ' has finished.')
            self.saveStabilityData()
            print('Simulation for r='+str(j) + ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            self.writeStabilityData(filename)
        print('Writing results to file: ' + filename)
        print("Finished!")


    def saveFairnessData(self):
        distancesBTC, distancesFTC = [], []
        for node in self.nodes:
            rewardFractionBTC = node.totalRewardBTC / self.environment.totalRewardBTC
            rewardFractionFTC = node.totalRewardFTC / self.environment.totalRewardFTC
            distancesBTC.append( abs(node.hashFrac - rewardFractionBTC) )
            distancesFTC.append( abs(node.hashFrac - rewardFractionFTC) )
        self.fairnessLogBTC.append(distancesBTC)
        self.distanceLogFTC.append(distancesFTC)

    def writeFairnessData(self):
        # 1. BTC data
        file = open(filename + "FairnessDataBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected reward fraction. Node_1,.,Node_n\n" )

        for log in self.fairnessLogBTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

        # 2.FTC data
        file = open(filename + "FairnessDataFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected reward fraction. Node_1,.,Node_n\n" )

        for log in self.distanceLogFTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

    def saveStabilityData(self):
        """
        Standard deviation from the expected utility curve. Node_1, ..., Node_n .
        """
        for node in self.nodes:
            distancesBTC, distances = []
            for i in len(self.r):
                distance = node.utility

        return


    def writeStabilityData(self, filename):
        # 1. BTC data
        file = open(filename + "StabilityDataBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected rounds to pass threshold. Node_1, ...,\n" )

        for log in self.fairnessLogBTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

        # 2. FTC data
        file = open(filename + "StabilityDataFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected rounds to pass threshold. Node_1, ..., \n")

        for log in self.distanceLogFTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()


    def writeUtilityData(self, filename):
        # 1. BTC data
        file = open(filename + "UtilityDataBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(BTC) by round for each node, seperated by commas. First line is thresholds. Second line is expected rounds to pass them." + "\n")

        thresholds, expRounds = [], []
        for node in self.nodes:
            thresholds.append( node.threshold )
            expRounds.append( node.expRoundsToPassThresholdBTC )
        file.write(",".join(map(str, thresholds)) + "\n")
        file.write(",".join(map(str, expRounds)) + "\n")

        for i in range(self.r-1):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogBTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()

        # 2. FTC data
        file = open(filename + "UtilityDataFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(FTC) by round for each node, seperated by commas. First line is thresholds. Second line is expected rounds to pass them." + "\n")

        thresholds, expRounds = [], []
        for node in self.nodes:
            thresholds.append( node.threshold )
            expRounds.append( node.expRoundsToPassThresholdFTC )
        file.write(",".join(map(str, thresholds)) + "\n")
        file.write(",".join(map(str, expRounds)) + "\n")

        for i in range(self.r-1):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogFTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()
