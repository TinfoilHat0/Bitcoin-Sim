#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, t, r, p, pF, hashFracs, txRate=5, k=16, avgOver=1, delay=0):
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
        self.delay = delay

        self.log = defaultdict(list) #<K, V> = ID of node, its statistics

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.txRate, self.k, self.delay) # Environment selects a leader each round for mining
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes, self.t)

    def extractData(self):
        """
        We extract all the data from the majority, i.e. consensus, chain.
        Note: We currently assume nodes with highest hashFraction has the majority chain, which is technically not correct.
        """
        # 1. Find the majority chain
        maxHashFrac, majorityChain = -1, None
        for node in self.nodes:
            if node.hashFrac > maxHashFrac:
                maxHashFrac = node.hashFrac
                majorityChain = node.blockChain

        # 2. Find how many block/fruit each node mined
        for b in majorityChain[1:]:
            self.nodes[b.minerID].totalBlockMined += 1
            for f in b.fruits:
                self.nodes[f.minerID].totalFruitMined += 1
                #if f.contBlockHeight - f.hangBlockHeight > self.k:
                #    print("Invalid!!")
                #    return

        # 3. Distribute the rewards to nodes
        self.environment.rewardBitcoin(majorityChain)
        self.environment.rewardFruitchain(majorityChain)


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
            self.extractData()
            for node in self.nodes:
                self.log[node.id].append( (node.totalBlockMined, node.totalFruitMined, node.totalBitcoinReward, node.totalFruitchainReward) )

        print('Writing results to file: ' + filename)
        self.saveData(filename)
        print("Finished!")

    def saveData(self, filename):
        # 1. Save (hashFrac, totalBitcoinReward, totalFruitchainReward)
        file = open(filename + "_rewards", 'w')
        file.write("# n:" + str(self.n) + " t:" + str(self.t) + " r:" + str(self.r) + " p:" +str(self.p) + " pF:" + str(self.pF) + "\n")
        file.write("# id," + "HashFrac," +  "nBlocksMined,"  + "nFruitsMined,"  +  "totalBitcoinReward," + "totalFruitchainReward" + "\n")

        for node in self.environment.nodes:
            avgStats = [0, 0, 0, 0]
            for tmp in self.log[node.id]:
                for i in range(len(tmp)):
                    avgStats[i] += tmp[i]
            for i in range(len(avgStats)):
                avgStats[i] = ceil(avgStats[i]/self.avgOver)

            file.write(str(node.id) + "," + str(node.hashFrac) + "," + str(avgStats[0]) + ","
            + str(avgStats[1]) + "," + str(avgStats[2]) + "," + str(round(avgStats[3])) + "\n")
        file.close()
