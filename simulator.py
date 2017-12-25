#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, t, r, p, pF, hashFracs, txRate=5, k=16):
        '''
        n: number of nodes
        t: number of corrupt nodes
        p: pr. of the system mining a block in a round
        pF: pr. of the system mining a fruit in a round
        hashFracs: hash power fraction of each node
        txRate: number of txs supplied each round
        k: maximum hanging distance for a fruit
        '''
        self.n = n
        self.t = t
        self.r = r
        self.p = p
        self.pF = pF
        self.hashFracs = hashFracs
        self.txRate = txRate
        self.k = k

        self.environment = Environment(p, pF, txRate, k) # Environment selects a leader each round for mining
        self.nodes = []
        for i in range(n):
            self.nodes.append(Node(i, hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes, self.t)
        self.log = []

    def run(self, filename):
        """ Runs the simulation for r rounds """
        for i in range(1, self.r+1):
            self.environment.step(i)
            self.log.append( (i, len(self.environment.unprocessedTxs), len(self.environment.processedTxs), self.environment.poolHashFraction,
                self.environment.nodes[0].totalBitcoinReward, self.environment.nodes[0].totalFruitchainReward) )
            if i%50000 == 0:
                print('Round:' + str(i) + ' has finished.')
        print('Simulation for r='+str(self.r)+ ' rounds has finished!')
        print('Writing results to file: ' + filename)
        self.saveData(filename)
        print("Finished!")

    def saveData(self, filename):
        """ Save simulation data """
        # 1. Save (roundNum, nProcessed, nUnprocessed, miningPoolHashFraction)
        file = open(filename + "_stats", 'w')
        file.write("# n:" + str(self.n) + " t:" + str(self.t) + " r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# HashFracs:" + ",".join(map(str, self.hashFracs)) + "\n")
        file.write("# RoundNum," + "unprocessedTxs," + "processedTxs,"
         + "poolHashFraction" +"," + "bitcoinReward" + "," + "fruitchainReward" + "\n")
        for item in self.log:
            file.write(str(item[0]) + "," + str(item[1]) + "," + str(item[2]) + ","
            + str(item[3]) + "," + str(item[4]) + "," + str(round(item[5])) + "\n")
        file.close()

        # 2. Save (hashFrac, totalBitcoinReward, totalFruitchainReward)
        file = open(filename + "_rewards", 'w')
        file.write("# n:" + str(self.n) + " t:" + str(self.t) + " r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# id," + "HashFrac," + "totalBitcoinReward," + "totalFruitchainReward" + "\n")
        for node in self.environment.nodes:
            file.write(str(node.id) + "," + str(node.hashFrac) + "," + str(node.totalBitcoinReward) + "," + str(round(node.totalFruitchainReward)) + "\n")
        file.close()
