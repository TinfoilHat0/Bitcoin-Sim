#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, p, pF, hashFracs, k=16, avgOver=1):
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
        self.p = p
        self.pF = pF
        self.hashFracs = hashFracs
        self.k = k
        self.avgOver = avgOver
        self.roundCtr = 1

        self.distanceLogBTC = []
        self.distanceLogFTC = []

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.k) # Environment selects a leader each round for mining
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes)
        self.roundCtr = 1

    def run(self, filename):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            while self.environment.nPassedThreshold < self.n:
                self.environment.step(self.roundCtr)
                if self.roundCtr%50000 == 0:
                    print('Round:' + str(self.roundCtr) + ' has finished.')
                self.roundCtr += 1
            self.saveStabilityData()
            print('Simulation for r='+str(self.roundCtr)+ ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            self.writeStabilityData(filename)
            #self.writeUtilityData(filename)
        print('Writing results to file: ' + filename)
        print("Finished!")


    def saveStabilityData(self):
        """
        Distance from expected rounds to pass threshold in terms of %. Can be negative. Node_1, ..., Node_n .
        """
        distancesBTC, distancesFTC = [], []
        for node in self.nodes:
            distancesBTC.append(node.dFromExpectedThresholdBTC)
            distancesFTC.append(node.dFromExpectedThresholdFTC)
        self.distanceLogBTC.append(distancesBTC)
        self.distanceLogFTC.append(distancesFTC)


    def writeStabilityData(self, filename):
        # 1. BTC data
        file = open(filename + "StabilityDataBTC", 'w')
        file.write("#r:" + str(self.roundCtr) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected rounds to pass threshold. Node_1, ...,\n" )

        for log in self.distanceLogBTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

        # 2. FTC data
        file = open(filename + "StabilityDataFTC", 'w')
        file.write("#r:" + str(self.roundCtr) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Relative distance from expected rounds to pass threshold. Node_1, ..., \n")

        for log in self.distanceLogFTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()


    def writeUtilityData(self, filename):
        # 1. BTC data
        file = open(filename + "UtilityDataBTC", 'w')
        file.write("#r:" + str(self.roundCtr) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(BTC) by round for each node, seperated by commas. First line is thresholds. Second line is expected rounds to pass them." + "\n")

        thresholds, expRounds = [], []
        for node in self.nodes:
            thresholds.append( node.threshold )
            expRounds.append( node.expRoundsToPassThresholdBTC )
        file.write(",".join(map(str, thresholds)) + "\n")
        file.write(",".join(map(str, expRounds)) + "\n")

        for i in range(self.roundCtr-1):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogBTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()

        # 2. FTC data
        file = open(filename + "UtilityDataFTC", 'w')
        file.write("#r:" + str(self.roundCtr) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Value of utility function(FTC) by round for each node, seperated by commas. First line is thresholds. Second line is expected rounds to pass them." + "\n")

        thresholds, expRounds = [], []
        for node in self.nodes:
            thresholds.append( node.threshold )
            expRounds.append( node.expRoundsToPassThresholdFTC )
        file.write(",".join(map(str, thresholds)) + "\n")
        file.write(",".join(map(str, expRounds)) + "\n")

        for i in range(self.roundCtr-1):
            roundLog = []
            for node in self.nodes:
                roundLog.append( node.utilityLogFTC[i][0] )
            file.write(",".join(map(str, roundLog)) + "\n")
        file.close()
