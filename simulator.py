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
        self.r = r
        self.avgOver = avgOver

        self.fairnessLogBTC = []
        self.stabilityLogBTC = []
        self.fairnessLogFTC = []
        self.stabilityLogFTC = []

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.k, self.r)
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
            self.saveFairnessData()
            # self.saveStabilityData()
        print("All simulations have finished!")
        print('Writing results to file: ' + filename)
        self.writeFairnessData(filename)
        # self.writeStabilityData(filename)
        print("Finished!")

    def saveFairnessData(self):
        distancesBTC, distancesFTC = [], []
        for node in self.nodes:
            fairRewardBTC = self.environment.totalRewardBTC * node.hashFrac
            fairRewardFTC = self.environment.totalRewardFTC * node.hashFrac
            distancesBTC.append( (abs(node.totalRewardBTC - fairRewardBTC) / fairRewardBTC)*100 )
            distancesFTC.append( (abs(node.totalRewardFTC - fairRewardFTC) / fairRewardFTC)*100 )
        self.fairnessLogBTC.append(distancesBTC)
        self.fairnessLogFTC.append(distancesFTC)

    def saveStabilityData(self):
        """
        Standard deviation from the expected utility curve. Node_1,..,Node_n .
        """
        variancesBTC, variancesFTC = [], []
        for node in self.nodes:
            distancesBTC, distancesFTC = [], []
            for i in range(self.r):
                distancesBTC.append( abs(node.utilityLogBTC[i][0] - node.utilityLogBTC[i][1]) / node.utilityLogBTC[i][1] )
                distancesFTC.append( abs(node.utilityLogFTC[i][0] - node.utilityLogFTC[i][1]) / node.utilityLogFTC[i][1] )
            variancesBTC.append( np.var(distancesBTC) )
            variancesFTC.append( np.var(distancesFTC) )
        self.stabilityLogBTC.append(variancesBTC)
        self.stabilityLogFTC.append(variancesFTC)

    def writeFairnessData(self, filename):
        # 1. BTC data
        file = open(filename + "FairnessMetricBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Fairness metric of system\n" )

        for log in self.fairnessLogBTC:
            file.write( str(np.var(log)) + "\n")
        file.close()

        # 2.FTC data
        file = open(filename + "FairnessMetricFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("#  Fairness metric of system \n" )

        for log in self.fairnessLogFTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()

    def writeStabilityData(self, filename):
        # 1. BTC data
        file = open(filename + "StabilityDataBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Variance of ratio of distance from expected utility value for node_1,..,node_n \n" )

        for log in self.stabilityLogBTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()

        # 2. FTC data
        file = open(filename + "StabilityDataFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + " k: " + str(self.k) +
        " c1:" + str(self.environment.c1) + " c2:" + str(self.environment.c2) + " c3:" + str(self.environment.c3) + "\n")
        file.write("# Variance of ratio of distance from expected utility value for node_1,..,node_n \n" )

        for log in self.stabilityLogFTC:
            file.write(",".join(map(str, log)) + "\n")
        file.close()
