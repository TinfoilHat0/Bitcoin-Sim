#coding: utf-8
from dataStructures import *
from math import ceil
import random
from collections import defaultdict
import numpy as np
import bisect

class Environment:
    def __init__(self, p = 1, pF = 1, r=100):
        '''
        p: pr. of mining a block in a rounds
        pF: pr. of mining a fruit in a round
        r: num. of rounds
        Environment of the protocol. Encapsulates our network.
        '''
        # Simulation parameters
        self.r = r

        # Network parameters
        self.nodes = []
        self.p = p
        self.pF = pF
        self.blockChain = Blockchain()
        self.fruitSet = []
        self.coinbaseReward = 12.5
        self.totalNetworkRewardBTC = 0
        self.totalNetworkRewardFTC = 0

        # Parameters related with FTC rewarding scheme
        self.k = 16
        self.c1 = 1/100
        self.c2 = 1/10
        self.c3 = 1/100
        self.nFruitsInWindow = 0

        # formulas to test validity of implementation
        self.expFruitPerBlock = self.pF/self. p
        self.expNormalFruitReward = ((1-self.c1)*self.coinbaseReward) / (self.k*(self.expFruitPerBlock+1))
        self.expFTCPerFruit = self.k*self.expNormalFruitReward*(1-self.c2+self.c3)
        self.expFTCPerBlock = self.c1*self.coinbaseReward + self.k*(self.expNormalFruitReward + self.expFruitPerBlock*self.expNormalFruitReward*(self.c2-self.c3))

         # Hard-coded constants taken from real world data of Bitcoin
        self.coinbaseReward = 12.5
        self.networkHashRate = 16 * (10**5) # Th/s
        self.usdToBTC = 9 * (10**-5) # 1 USD = 0.00009 BTC
        self.costPerKWh = 18 * (10**-6) # In France, cost per KWh = 0.2 USD = 0.000018 BTC
        self.deviceHashRate = 14 # TH/s, AntMiner S9
        self.costPerDevice = 0.23 # BTC
        self.consumptionPerDevice = 1.372 # KWh

        self.startRound = 0

    def initializeNodes(self, nodes):
        '''
        nodes: list of nodes which are in the environment
        '''
        self.nodes = nodes
        self.n = len(nodes)
        self.blockLeaderProbs = []
        self.fruitLeaderProbs = []
        for i in range(self.n):
            self.blockLeaderProbs.append(self.p*nodes[i].hashFrac)
            self.fruitLeaderProbs.append(self.pF*nodes[i].hashFrac)
            nodes[i].environment = self
        self.blockLeaderProbs.append(1-self.p) # prob. of nobody mines a block in a round
        self.fruitLeaderProbs.append(1-self.pF) # prob. of nobody mines a fruit in a round

    def step(self, roundNum):
        '''
        roundNum: current round number

        Nodes attempt to mine a fruit and a block independently.
        If a miner is succesful, he broadcasts and others immediately deliver
        '''
        # select leaders for round, id = n means nothing is mined
        blockLeaderID = np.random.choice(self.n+1, 1, p=self.blockLeaderProbs)[0]
        fruitLeaderID = np.random.choice(self.n+1, 1, p=self.fruitLeaderProbs)[0]
        b, f = None, None
        if fruitLeaderID != self.n:
            f = self.nodes[fruitLeaderID].mineFruit(roundNum)
        if blockLeaderID != self.n:
            b = self.nodes[blockLeaderID].mineBlock(roundNum)
            # Trigger reward schemes
            self.awardBTC(blockLeaderID, roundNum)
            self.awardFTC(blockLeaderID, roundNum)

        if self.blockChain.length == self.k:
            self.startRound = roundNum
            for node in self.nodes:
                node.rewardBTC = 0
                node.rewardFTC = 0
        if self.blockChain.length > self.k:
            self.logRewardByRound(roundNum)


        # save statistics at the end of last round
        #if roundNum == self.r:
        #    self.saveStatistics()
        return b, f


    def logRewardByRound(self, roundNum):
        for node in self.nodes:
            node.rewardByRoundBTC.append(node.totalRewardBTC)
            node.rewardByRoundFTC.append(node.totalRewardFTC)

            node.costByRound.append(node.costPerRound* (roundNum-self.startRound))

    def awardBTC(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node
        Distributes rewards to miners acc. to Bitcoin rewarding scheme, i.e.,
        miner gets everything
        """
        reward = self.blockChain.head.reward
        self.nodes[blockLeaderID].totalRewardBTC += reward
        self.nodes[blockLeaderID].rewardRoundBTC.append(roundNum)

    def awardFTC(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node
        Distributes rewards to miners according to Fruitchain rewarding scheme
        (see paper)
        """
        head = self.blockChain.head
        blockChain = self.blockChain
        if head.height > self.k:
            # direct reward
            x = head.reward
            self.nodes[blockLeaderID].totalRewardFTC += self.c1*x
            self.nodes[blockLeaderID].rewardRoundFTC.append(roundNum)
            # compute normal reward per fruit
            R = (1-self.c1)*x
            n0 = R / self.nFruitsInWindow
            # iterate over last k blocks and distribute window reward
            for b in blockChain[-self.k-1:-1]:
                for f in b.fruits:
                    dL = self.c3
                    # award fruit miners
                    self.nodes[f.minerID].totalRewardFTC += n0*(1 - self.c2 + dL)
                    if self.nodes[f.minerID].rewardRoundFTC[-1] != roundNum:
                        self.nodes[f.minerID].rewardRoundFTC.append(roundNum)
                    # award block miners
                    self.nodes[b.minerID].totalRewardFTC += n0*(self.c2 - dL)
                    if self.nodes[b.minerID].rewardRoundFTC[-1] != roundNum:
                        self.nodes[b.minerID].rewardRoundFTC.append(roundNum)

                self.nodes[b.minerID].totalRewardFTC += n0 # reward of the implicit fruit goes to block miner
            # slide the window and adjust the number of fruits
            self.nFruitsInWindow -= (blockChain[-self.k-1].nFruits + 1)
            self.nFruitsInWindow += (head.nFruits + 1)
        else:
            self.nFruitsInWindow += (head.nFruits + 1) # +1 is the implicit fruit (see paper)

    def saveStatistics(self):
        """
        Save some statistics at the end of simulation
        """
        # Compute statistics and sustainability metric for individial nodes
        for node in self.nodes:
            # network's reward as a whole
            self.totalNetworkRewardBTC += node.totalRewardBTC
            self.totalNetworkRewardFTC += node.totalRewardFTC
            # compute metrics for nodes, d_i/s_i
            if len(node.rewardRoundBTC) == 1: # if no reward earned, reward gap is r
                node.avgRewardGapBTC = self.r
            else:
                node.avgRewardGapBTC = sum( np.diff(node.rewardRoundBTC) ) / (len(node.rewardRoundBTC)-1)
            if len(node.rewardRoundFTC) == 1:
                node.avgRewardGapFTC = self.r
            else:
                node.avgRewardGapFTC = sum( np.diff(node.rewardRoundFTC) ) / (len(node.rewardRoundFTC)-1)

        # After computing the total reward, compute fairness metric
        for node in self.nodes:
            fairRewardBTC = self.totalNetworkRewardBTC * node.hashFrac
            fairRewardFTC = self.totalNetworkRewardFTC * node.hashFrac
            node.fairnessBTC = ( (abs(node.totalRewardBTC - fairRewardBTC) / fairRewardBTC)*100 )
            node.fairnessFTC = ( (abs(node.totalRewardFTC - fairRewardFTC) / fairRewardFTC)*100 )

            node.sustainabilityBTC = node.totalRewardBTC / node.avgRewardGapBTC
            node.sustainabilityFTC = node.totalRewardFTC / node.avgRewardGapFTC

class Node:
    def __init__(self, _id=0, hashFrac=1, env=Environment()):
        '''
        _id: unique id of the node
        hashFrac: fraction of hash power of the node
        environment: environment of the network that the node belongs to
        '''
        self.environment = env
        self.id = _id
        self.hashFrac = hashFrac
        # statistics of node
        self.nBlocksMined = 0
        self.nFruitsMined = 0
        self.totalRewardBTC = 0
        self.totalRewardFTC = 0
        # rounds in which node earned a reward
        self.rewardRoundBTC = [0]
        self.rewardRoundFTC = [0]
        self.avgRewardGapBTC = -1
        self.avgRewardGapFTC = -1
        # metric values of node, i.e di and si(see paper)
        self.sustainabilityBTC = -1
        self.fairnessBTC = -1

        self.sustainabilityFTC = -1
        self.fairnessFTC = -1


        self.rewardByRoundBTC = []
        self.rewardByRoundFTC = []
        # theoretical results
        p = self.environment.p
        pF = self.environment.pF
        h = self.hashFrac
        x = self.environment.coinbaseReward
        k = self.environment.k
        c0 = p / pF
        self.expRewardPerRound = p*h*x
        self.expRewardGapBTC = 1 / (p*h)

        denom = (1-h)**(k+1+k*c0)
        self.expRewardGapFTC = 1 / p*(1-denom)

        #self.calculateCost()

        self.costPerRound = p*12.5*h*0.1
        self.costByRound = []

    def mineFruit(self, roundNum):
        '''
        create a fruit, add it to fruitset of environment and return it
        '''
        # by default, fruit hangs from head of chain (i.e maximum freshness bonus)
        hangBlockHeight = self.environment.blockChain.length
        fruit = Fruit(self.id, roundNum, hangBlockHeight)
        self.environment.fruitSet.append(fruit)
        self.nFruitsMined += 1
        return fruit

    def mineBlock(self, roundNum):
        '''
        create a block, add it to blockchain and return it
        '''
        fruits = self.environment.fruitSet
        self.environment.fruitSet = []
        block = Block(self.id, roundNum, fruits)
        self.environment.blockChain.append(block)
        for f in fruits:
            f.includeRound = roundNum
            f.contBlockHeight = self.environment.blockChain.length
        self.nBlocksMined += 1
        return block

    def __repr__(self):
        return str(self.id) + '|' + str(self.hashFrac)

    def calculateCost(self):
        hashRate = self.hashFrac * self.environment.networkHashRate
        nDevices = ceil (hashRate / self.environment.deviceHashRate)
        self.initialCost = nDevices * self.environment.costPerDevice
        consumptionPerRound = self.environment.consumptionPerDevice * nDevices * (self.environment.p / 6) # in KWh
        self.costPerRound = consumptionPerRound * self.environment.costPerKWh
