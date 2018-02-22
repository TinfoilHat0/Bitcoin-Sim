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
        self.coinbaseReward = 12.5
        self.totalNetworkRewardBTC = 0
        self.totalNetworkRewardFTC = 0
        self.totalNetworkBlockMined = 0
        self.totalNetworkFruitMined = 0

        # Parameters related with FTC rewarding scheme
        self.k = 16
        self.c1 = 1/100
        self.c2 = 1/10
        self.c3 = 1/100
        self.nFruitsInWindow = 0

        # Parameters about selfish-mining
        self.privateChain = Blockchain()
        self.publicChain = Blockchain()
        self.attackerFruitSet = []
        self.honestFruitSet = []
        self.state = 0

        # formulas to test validity of implementation
        self.expFruitPerBlock = self.pF/self. p
        self.expNormalFruitReward = ((1-self.c1)*self.coinbaseReward) / (self.k*(self.expFruitPerBlock+1))
        self.expFTCPerFruit = self.k*self.expNormalFruitReward*(1-self.c2+self.c3)
        self.expFTCPerBlock = self.c1*self.coinbaseReward + self.k*(self.expNormalFruitReward + self.expFruitPerBlock*self.expNormalFruitReward*(self.c2-self.c3))

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
        # in selfish, we just have 2 nodes. if ID == honest, else honest
        blockLeaderID = np.random.choice(self.n+1, 1, p=self.blockLeaderProbs)[0]
        fruitLeaderID = np.random.choice(self.n+1, 1, p=self.fruitLeaderProbs)[0]
        b, f = None, None
        if fruitLeaderID != self.n:
            f = self.nodes[fruitLeaderID].mineFruit(roundNum)

        # selfish-mining according to state machine model, see selfish mining paper
        if blockLeaderID != self.n:
            b = self.nodes[blockLeaderID].mineBlock(roundNum)
            # honest finds first block
            if self.state == 0 and blockLeaderID == 0:
                self.publicChain.append(b)
                self.privateChain.adaptChain(self.publicChain)
                self.attackerFruitSet = []
            # attacker finds first block
            elif self.state == 0 and blockLeaderID == 1:
                self.privateChain.append(b)
                self.state = 1
            # attacker has a secret block and honest finds
            elif self.state == 1 and blockLeaderID == 0:
                self.publicChain.append(b)
                self.state = -1
            # we have a fork, attacker finds a block and resolves the fork
            elif self.state == -1 and blockLeaderID == 1:
                self.privateChain.append(b)
                self.publicChain.adaptChain(self.privateChain)
                self.honestFruitSet =[]
                self.state = 0
            # we have a fork, honest finds a block and resolves the fork
            elif self.state == -1 and blockLeaderID == 0:
                # honest picks a chain at random and extends it
                if random.random() < 0.5:
                    self.privateChain.append(b)
                    self.publicChain.adaptChain(self.privateChain)
                else:
                    self.publicChain.append(b)
                    self.privateChain.adaptChain(self.publicChain)
                self.attackerFruitSet = []
                self.state = 0
            # attacker has a lead of 1 and finds a block.
            elif self.state >= 1 and blockLeaderID == 1:
                self.privateChain.append(b)
                self.state += 1
            # attacker has a lead of 2 and honest finds a block
            elif self.state == 2 and blockLeaderID == 0:
                self.publicChain.adaptChain(self.privateChain)
                self.honestFruitSet = []
                self.state = 0
            # attacker has a lead > 2 and honest finds a block
            elif self.state > 2 and blockLeaderID == 0:
                self.publicChain.append(b)
                self.state -= 1

        # save statistics at the end of last round
        if roundNum == self.r:
            # determine public chain
            if self.state > 0:
                self.publicChain.adaptChain(self.privateChain)
            if self.state == -1 and random.random() < 0.5:
                self.publicChain.adaptChain(self.privateChain)

            self.getMineCount(self.publicChain)
            self.awardBTC(self.publicChain)
            self.awardFTC(self.publicChain)

            self.saveStatistics()
        return b, f

    def getMineCount(self, chain):
        """ Compute how many fruits/block each miner mined """
        for b in chain:
            self.nodes[b.minerID].nBlocksMined += 1
            for f in b.fruits:
                self.nodes[f.minerID].nFruitsMined += 1

    def awardBTC(self, chain):
        """
        Distributes rewards to miners acc. to Bitcoin rewarding scheme, i.e.,
        miner gets everything.
        """
        for b in chain:
            self.nodes[b.minerID].totalRewardBTC += b.reward

    def awardFTC(self, chain):
        """
        Distributes rewards to miners according to Fruitchain rewarding scheme
        (see paper)
        """
        if chain.length < self.k+1:
            return

        for b in chain[:self.k+1]:
            self.nFruitsInWindow += b.nFruits + 1 # +1 is the implicity fruit
        for b in chain[self.k:]:
            # direct reward
            x = b.reward
            self.nodes[b.minerID].totalRewardFTC += self.c1*x
            # compute normal reward per fruit
            R = (1-self.c1)*x
            n0 = R / self.nFruitsInWindow
            # iterate over last k blocks and distribute window reward
            for _b in chain[b.height-1-self.k : b.height-1]:
                for f in _b.fruits:
                    dL = 0
                    if _b.minerID == 1:
                        dL = self.c3 # attacker gets maximal freshness bonus
                    self.nodes[f.minerID].totalRewardFTC += n0*(1 - self.c2 + dL)
                    self.nodes[_b.minerID].totalRewardFTC += n0*(self.c2 - dL)
                self.nodes[_b.minerID].totalRewardFTC += n0 # reward of the implicit fruit goes to block miner
            # slide the window and adjust the number of fruits
            self.nFruitsInWindow -= ( chain[b.height-1-self.k].nFruits + 1 )
            self.nFruitsInWindow += ( b.nFruits + 1 )

    def saveStatistics(self):
        """
        Save some statistics at the end of simulation
        """
        # Compute statistics and sustainability metric for individial nodes
        for node in self.nodes:
            # network's reward as a whole
            self.totalNetworkRewardBTC += node.totalRewardBTC
            self.totalNetworkRewardFTC += node.totalRewardFTC
            self.totalNetworkBlockMined += node.nBlocksMined
            self.totalNetworkFruitMined += node.nFruitsMined

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


    def mineFruit(self, roundNum):
        '''
        create a fruit, add it to fruitset of environment and return it
        '''
        fruit = Fruit(self.id, roundNum)
        self.environment.attackerFruitSet.append(fruit)
        self.environment.honestFruitSet.append(fruit)
        return fruit

    def mineBlock(self, roundNum):
        '''
        create a block, add it to blockchain and return it
        '''
        if self.id == 0:
            fruits = self.environment.honestFruitSet
            self.environment.honestFruitSet = []
        else:
            fruits = self.environment.attackerFruitSet
            self.environment.attackerFruitSet = []
        block = Block(self.id, roundNum, fruits)
        return block

    def __repr__(self):
        return str(self.id) + '|' + str(self.hashFrac)
