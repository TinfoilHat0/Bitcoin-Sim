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
        self.totalNetworkBlockMined = 0
        self.totalNetworkFruitMined = 0
        self.totalNetworkFTCFromFruits = 0
        self.totalNetworkFTCFromBlocks = 0

        # Parameters related with FTC rewarding scheme
        self.k = 16
        self.c1 = 1/100
        self.c2 = 1/10
        self.c3 = 1/100
        self.nFruitsInWindow = 0

        # Parameters about pool tests
        self.poolTestStartRound = 0
        self.poolLog = [] # ([nodes in BTC], [nodes in FTC])

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

        self.runPoolTest(roundNum)

        # save statistics at the end of last round
        if roundNum == self.r:
            self.saveStatistics()
        return b, f

    def runPoolTest(self, roundNum=0, t=125000, th=0.85):
        """
        t: snapshot interval length
        th: switch threshold
        """
        # Initialize nodes when block length is k
        if self.poolTestStartRound == 0 and self.blockChain.length == self.k:
            self.poolTestStartRound = roundNum
            nodesInBTC, nodesInFTC = [], []
            for node in self.nodes:
                node.poolReward = 0
                # initially, all nodes are in BTC
                node.poolID = 0
                nodesInBTC.append(node)
            self.poolLog.append( (nodesInBTC, nodesInFTC) )
        # pool switching
        elif self.blockChain.length > self.k and (roundNum-self.poolTestStartRound)%t == 0:
            print('!')
            nodesInBTC, nodesInFTC = [], []
            for node in self.nodes:
                expReward = t*node.expRewardPerRound
                print(node.hashFrac, node.poolID, node.totalPoolReward, expReward)
                # do pool switches
                if node.totalPoolReward < expReward*th:
                    if node.poolID == 0:
                        node.poolID = 1
                    else:
                        node.poolID = 0
                # update the log
                if node.poolID == 0:
                    nodesInBTC.append(node)
                else:
                    nodesInFTC.append(node)
                node.totalPoolReward = 0
            self.poolLog.append( (nodesInBTC, nodesInFTC) )


    def awardBTC(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node
        Distributes rewards to miners acc. to Bitcoin rewarding scheme, i.e.,
        miner gets everything
        """
        reward = self.blockChain.head.reward
        self.nodes[blockLeaderID].totalRewardBTC += reward
        self.nodes[blockLeaderID].rewardRoundBTC.add(roundNum)

        # pool experiment
        if self.nodes[blockLeaderID].poolID == 0:
            self.nodes[blockLeaderID].totalPoolReward += reward

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
            self.nodes[blockLeaderID].totalFTCFromBlocks += self.c1*x
            self.nodes[blockLeaderID].rewardRoundFTC.add(roundNum)
            # pool experiment
            if self.nodes[blockLeaderID].poolID == 1:
                self.nodes[blockLeaderID].totalPoolReward += self.c1*x
            # compute normal reward per fruit
            R = (1-self.c1)*x
            n0 = R / self.nFruitsInWindow
            # iterate over last k blocks and distribute window reward
            for b in blockChain[-self.k-1:-1]:
                for f in b.fruits:
                    l = f.contBlockHeight-f.hangBlockHeight-1 # number of blocks between hanging and containing block of fruit
                    dL = self.c3*(1-l/(self.k-1))
                    # award fruit miners
                    self.nodes[f.minerID].totalRewardFTC += n0*(1 - self.c2 + dL)
                    self.nodes[f.minerID].totalFTCFromFruits += n0*(1 - self.c2 + dL)
                    self.nodes[f.minerID].rewardRoundFTC.add(roundNum)
                    if self.nodes[f.minerID].poolID == 1:
                        self.nodes[f.minerID].totalPoolReward += n0*(1 - self.c2 + dL)
                    # award block miners
                    self.nodes[b.minerID].totalRewardFTC += n0*(self.c2 - dL)
                    self.nodes[b.minerID].totalFTCFromBlocks += n0*(self.c2 - dL)
                    self.nodes[b.minerID].rewardRoundFTC.add(roundNum)
                    if self.nodes[b.minerID].poolID == 1:
                        self.nodes[b.minerID].totalPoolReward += n0*(self.c2 - dL)

                self.nodes[b.minerID].totalRewardFTC += n0 # reward of the implicit fruit goes to block miner
                self.nodes[b.minerID].totalFTCFromBlocks += n0
                self.nodes[b.minerID].rewardRoundFTC.add(roundNum)
                if self.nodes[b.minerID].poolID == 1:
                    self.nodes[b.minerID].totalPoolReward += n0
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
            self.totalNetworkBlockMined += node.nBlocksMined
            self.totalNetworkFruitMined += node.nFruitsMined
            self.totalNetworkFTCFromBlocks += node.totalFTCFromBlocks
            self.totalNetworkFTCFromFruits += node.totalFTCFromFruits
            # compute metrics for nodes, d_i/s_i
            if len(node.rewardRoundBTC) == 1: # if no reward earned, reward gap is r
                node.avgRewardGapBTC = self.environment.r
            else:
                node.avgRewardGapBTC = sum( np.diff(list(node.rewardRoundBTC)) ) / len( np.diff(list(node.rewardRoundBTC)) )
            if len(node.rewardRoundFTC) == 1:
                node.avgRewardGapFTC = self.environment.r
            else:
                node.avgRewardGapFTC = sum( np.diff(list(node.rewardRoundFTC)) ) / len( np.diff(list(node.rewardRoundFTC)) )
            node.sustainabilityBTC = node.totalRewardBTC / node.avgRewardGapBTC
            node.sustainabilityFTC = node.totalRewardFTC / node.avgRewardGapFTC
        # After computing the total reward, compute fairness metric
        for node in self.nodes:
            fairRewardBTC = self.totalNetworkRewardBTC * node.hashFrac
            fairRewardFTC = self.totalNetworkRewardFTC * node.hashFrac
            node.fairnessBTC = ( (abs(node.totalRewardBTC - fairRewardBTC) / fairRewardBTC)*100 )
            node.fairnessFTC = ( (abs(node.totalRewardFTC - fairRewardFTC) / fairRewardFTC)*100 )

    def logRewardByRound(self):
        """
        log total reward of each node both for BTC and FTC after every round
        """
        for node in self.nodes:
            node.totalRewardByRoundBTC.append(node.totalRewardBTC)
            node.totalRewardByRoundFTC.append(node.totalRewardFTC)
        return


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
        self.totalFTCFromFruits = 0
        self.totalFTCFromBlocks = 0
        self.totalRewardByRoundBTC = []
        self.totalRewardByRoundFTC = []
        # rounds in which node earned a reward
        self.rewardRoundBTC = set({0})
        self.rewardRoundFTC = set({0})
        self.avgRewardGapBTC = -1
        self.avgRewardGapFTC = -1
        # metric values of node, i.e di and si(see paper)
        self.sustainabilityBTC = -1
        self.fairnessBTC = -1
        self.sustainabilityFTC = -1
        self.fairnessFTC = -1

        # theoretical results
        self.expRewardPerRound = self.environment.p*self.hashFrac*self.environment.coinbaseReward
        # pool experiment parameters
        self.poolID = None
        self.totalPoolReward = 0

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
