#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, p, pF, r, hashFracs, avgOver=1):
        '''
        n: number of nodes
        r: number of rounds
        p: pr. of the system mining a block in a round
        pF: pr. of the system mining a fruit in a round
        hashFracs: hash rate fraction of each node
        avgOver: number of time this simulation runs with corresponding parameters
        '''
        self.n = n
        self.p = p
        self.pF = pF
        self.r = r
        self.hashFracs = hashFracs
        self.avgOver = avgOver

        self.fairnessLogFTC = []
        self.fairnessLogBTC = []
        self.sustainabilityLogBTC = []
        self.sustainabilityLogFTC = []

        self.fruitPerBlockLog = []
        self.FTCPerFruitLog = []
        self.FTCPerBlockLog = []
        self.avgGainPerRoundFTCLog = []
        self.avgGainPerRoundBTCLog = []

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.r)
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes)

    def run(self, filename=''):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            for j in range(1, self.r+1):
                self.environment.step(j)
                if j%50000 == 0:
                    print('Round:' + str(j) + ' has finished.')
            print('Simulation for r=' + str(j) + ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            #self.logValidationData()
            #self.logMetricData()
        print("All simulations have finished!")
        print('Writing results to file: ' + filename)
        #self.writeValidationData(filename)
        #self.writeMetricData()
        print("Finished!")

    def logValidationData(self):
        # Fruit per block
        fruitPerBlock = self.environment.totalNetworkFruitMined / self.environment.totalNetworkBlockMined
        self.fruitPerBlockLog.append( (fruitPerBlock, self.environment.expFruitPerBlock) )
        # Reward per fruit
        FTCPerFruit = self.environment.totalNetworkFTCFromFruits / self.environment.totalNetworkFruitMined
        self.FTCPerFruitLog.append( (FTCPerFruit, self.environment.expFTCPerFruit) )
        # Reward per block
        FTCPerBlock = self.environment.totalNetworkFTCFromBlocks / self.environment.totalNetworkBlockMined
        self.FTCPerBlockLog.append( (FTCPerBlock , self.environment.expFTCPerBlock) )

    def writeValidationData(self, filename):
        # Fruit per block
        file = open(filename + "FruitPerBlock", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        for log in self.fruitPerBlockLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()
        # Reward per fruit
        file = open(filename + "RewardPerFruit", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        for log in self.FTCPerFruitLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()
        # Reward per block
        file = open(filename + "RewardPerBlock", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        for log in self.FTCPerBlockLog:
            file.write(','.join(map(str, log)) + "\n")
        file.close()

    def logMetricData(self):
        # Unfairness metric
        fairBTC, fairFTC = 0, 0
        for node in self.nodes:
            fairBTC += node.fairnessBTC
            fairFTC += node.fairnessFTC
        fairBTC /= self.n
        fairFTC /= self.n
        self.fairnessLogBTC.append(fairBTC)
        self.fairnessLogFTC.append(fairFTC)
        # Sustainability metric
        sustBTC, sustFTC = 0, 0
        for node in self.nodes:
            sustBTC += node.sustainabilityBTC
            sustFTC += node.sustainabilityFTC
        sustBTC /= self.n
        sustFTC /= self.n
        self.sustainabilityLogBTC.append(sustBTC)
        self.sustainabilityLogFTC.append(sustFTC)

    def writeMetricData(self, filename):
        # Fairness metric
        # 1. BTC data
        file = open(filename + "FairnessMetricBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# Fairness metric of system\n" )
        for log in self.fairnessLogBTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()
        # 2.FTC data
        file = open(filename + "FairnessMetricFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("#  Fairness metric of system \n" )
        for log in self.fairnessLogFTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()
        # Sustainability metric
        # 1. BTC data
        file = open(filename + "SustainabilityMetricBTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# Sustainability of system \n" )
        for log in self.sustainabilityLogBTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()
        # 2.FTC data
        file = open(filename + "SustainabilityMetricFTC", 'w')
        file.write("#r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# Sustainability of system \n" )
        for log in self.sustainabilityLogFTC:
            file.write( str(np.mean(log)) + "\n")
        file.close()
