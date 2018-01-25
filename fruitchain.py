#coding: utf-8
from dataStructures import *
from math import ceil
import random
from collections import defaultdict
import numpy as np
import bisect

class Environment:
    def __init__(self, p = 1, pF = 1, k = 16, r=100):
        '''
        p: pr. of mining a block in a rounds
        pF: pr. of mining a fruit in a round
        txRate: # of txs supplied to system each round
        k: determines how far a fruit can hang
        r: num. of rounds
        Environment of the protocol. Handles mining process.
        '''
        self.p = p
        self.pF = pF
        self.k = k
        self.r = r
        self.nodes = []

        # Fruitchain related params.
        self.c1 = 1/100
        self.c2 = 1/10
        self.c3 = 1/100
        self.nFruitsInWindow = 0

        # Hard-coded constants taken from real world data of Bitcoin
        self.coinbaseReward = 12.5
        self.networkHashRate = 16 * (10**5) # Th/s
        self.usdToBTC = 9 * (10**-5) # 1 USD = 0.00009 BTC
        self.costPerKWh = 18 * (10**-6) # In France, cost per KWh = 0.2 USD = 0.000018 BTC
        self.deviceHashRate = 14 # TH/s, AntMiner S9
        self.costPerDevice = 0.23 # BTC
        self.consumptionPerDevice = 1.372 # KWh

        # theoretical calculations for fruitchain (see analysis paper), x=self.coinbaseReward is expected block reward
        self.expFruitPerBlock = self.pF / self. p
        self.expNormalFruitReward = (1-self.c1)*self.coinbaseReward / self.k*(self.expFruitPerBlock+1)
        self.expFTCPerFruit = self.k*self.expNormalFruitReward * (1 - self.c2 + self.c3)
        self.expFTCPerBlock = self.c1*self.coinbaseReward + (1-self.c1)*self.coinbaseReward*(self.c2 - self.c3)

        # Stability-Fairness-Validation tests related params
        self.nPassedThreshold = 0
        self.totalRewardBTC = 0
        self.totalRewardFTC = 0
        self.totalBlockMined = 0
        self.totalFruitMined = 0
        self.totalFTCFromFruits = 0
        self.totalFTCFromBlocks = 0

    def initializeNodes(self, nodes):
        '''
        nodes: list of nodes which are in the environment
        set probability of mining for each node
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
        roundNum: number of the current round

        Nodes attempt to mine a fruit and a block independently,
        they broadcast what they have mined
        '''
        # 1. Simulate mining process and broadcast what's been mined
        blockLeaderID = np.random.choice(self.n+1, 1, p=self.blockLeaderProbs)[0]
        fruitLeaderID = np.random.choice(self.n+1, 1, p=self.fruitLeaderProbs)[0]
        b, f = None, None

        if fruitLeaderID != self.n:
            f = self.nodes[fruitLeaderID].mineFruit(roundNum)
            # Bcast the fruit
            for node in self.nodes:
                if node.id != fruitLeaderID:
                    node.deliver(f)

        if blockLeaderID != self.n:
            b = self.nodes[blockLeaderID].mineBlock(roundNum)
            # Trigger reward schemes
            self.rewardBitcoin(blockLeaderID, roundNum)
            self.rewardFruitchain(blockLeaderID, roundNum)
            # log utility whenever a block is mined
            # Bcast the block
            for node in self.nodes:
                if node.id != blockLeaderID:
                    node.deliver(b)

        # 2. Log utility values
        self.logUtility(roundNum)
        #3. Save statistics
        if roundNum == self.r:
            self.saveStatistics()
        return b, f

    def saveStatistics(self):
        """
        Save some statistics at the end of simulation
        """
        for node in self.nodes:
            self.totalRewardBTC += node.totalRewardBTC
            self.totalRewardFTC += node.totalRewardFTC
            self.totalBlockMined += node.nBlocksMined
            self.totalFruitMined += node.nFruitsMined
            self.totalFTCFromBlocks += node.totalFTCFromBlocks
            self.totalFTCFromFruits += node.totalFTCFromFruits
        return

    def logUtility(self, roundNum):
        """
        Log utility values
        """
        for node in self.nodes:
            node.logUtilityBTC(roundNum)
            node.logUtilityFTC(roundNum)
            """
            measuredUtilityBTC = node.utilityLogBTC[-1][0]
            measuredUtilityFTC = node.utilityLogFTC[-1][0]

            if node.nRoundsToThresholdBTC == 0 and measuredUtilityBTC >= node.threshold:
                node.nRoundsToThresholdBTC = roundNum
                node.dFromExpectedThresholdBTC = ( abs(roundNum - node.expRoundsToPassThresholdBTC) / node.expRoundsToPassThresholdBTC ) * 100

            if node.nRoundsToThresholdFTC == 0 and measuredUtilityFTC >= node.threshold:
                node.nRoundsToThresholdFTC = roundNum
                node.dFromExpectedThresholdFTC = ( abs(roundNum - node.expRoundsToPassThresholdFTC) / node.expRoundsToPassThresholdFTC ) * 100

            if node.passedThreshold == False and (node.nRoundsToThresholdFTC > 0 and node.nRoundsToThresholdBTC > 0):
                node.passedThreshold = True
                self.nPassedThreshold += 1
            """
        return

    def rewardBitcoin(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node

        Distributes rewards to miners acc. to Bitcoin rewarding scheme, i.e.,
        miner gets everything
        """
        totalFee = self.nodes[blockLeaderID].blockChain.head.totalFee
        self.nodes[blockLeaderID].totalRewardBTC += totalFee

    def rewardFruitchain(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node

        Distributes rewards to miners according to Fruitchain rewarding scheme
        (see paper)
        """
        head = self.nodes[blockLeaderID].blockChain.head
        blockChain = self.nodes[blockLeaderID].blockChain
        if head.height > self.k + 1: # +1 is due to genesis
            # 1. Fetch the totalFee from head and award its miner
            x = head.totalFee
            self.nodes[blockLeaderID].totalRewardFTC += (self.c1)*x
            self.nodes[blockLeaderID].totalFTCFromBlocks += (self.c1)*x
            R = (1-self.c1)*x
            # 2. Calculate 'normal' reward
            n0 = R / self.nFruitsInWindow
            # 3. Iterate over last k blocks and distribute rewards to miners
            for b in blockChain[-self.k-1:-1]:
                for f in b.fruits:
                    l = f.contBlockHeight - f.hangBlockHeight - 1 # number of blocks between hanging and containing block]
                    dL = self.c3 * (1 - l/(self.k-1))
                    self.nodes[f.minerID].totalRewardFTC += n0*(1 - self.c2 + dL)
                    self.nodes[f.minerID].totalFTCFromFruits += n0*(1 - self.c2 + dL)

                    self.nodes[b.minerID].totalRewardFTC += n0*(self.c2 - dL)
                    self.nodes[b.minerID].totalFTCFromBlocks += n0*(self.c2 - dL)
                self.nodes[b.minerID].totalRewardFTC += n0 # reward of the implicit fruit goes to block miner
                self.nodes[b.minerID].totalFTCFromBlocks += n0
            # 4. Slide the window and adjust the number of fruits
            self.nFruitsInWindow -= (blockChain[-self.k-1].nFruits + 1)
            self.nFruitsInWindow += (head.nFruits + 1)
        else:
            self.nFruitsInWindow += (head.nFruits + 1) # +1 is the implicit fruit (see paper)

class Node:
    def __init__(self, _id=0, hashFrac=1, env=Environment()):
        '''
        _id: unique id of the node
        blockChain: local chain of the node
        validFruits: valid fruits received/mined by the node; <K, V> = <hangBlockPos, setOfFruits>
        fruitsInChain: fruits that are in the blockchain; <K, V> = <fruitHash, block.height>
        hashFrac: fraction of hash power of the node

        environment: environment of the pair (A, Z)
        '''
        self.id = _id
        self.blockChain = Blockchain()
        self.validFruits = defaultdict(set)
        self.fruitsInChain = {}
        self.hashFrac = hashFrac

        self.environment = env
        self.k = self.environment.k
        self.calculateCost()
        self.threshold = self.initialCost

        self.nBlocksMined = 0
        self.nFruitsMined = 0
        self.totalRewardBTC = 0
        self.totalRewardFTC = 0
        self.totalFTCFromFruits = 0
        self.totalFTCFromBlocks = 0
        self.utilityLogBTC = [] # (measured, expected by rounds)
        self.utilityLogFTC = [] # (measured, expected by rounds)

        self.prMiningBlock =  self.environment.p * self.hashFrac
        self.prMiningFruit = self.environment.pF * self.hashFrac
        self.expGainPerRoundBTC = ( self.prMiningBlock*self.environment.coinbaseReward ) - self.costPerRound
        self.expGainPerRoundFTC = ( self.prMiningBlock*self.environment.expFTCPerBlock + self.prMiningFruit*self.environment.expFTCPerFruit ) - self.costPerRound

        self.expRoundsToPassThresholdBTC = ceil( self.threshold  / self.expGainPerRoundBTC )
        self.expRoundsToPassThresholdFTC = ceil( self.threshold / self.expGainPerRoundFTC )
        self.nRoundsToThresholdBTC = 0
        self.nRoundsToThresholdFTC = 0
        self.passedThreshold = False

        self.dFromExpectedThresholdBTC = 0
        self.dFromExpectedThresholdFTC = 0

    def mineFruit(self, roundNum):
        '''
        Mine the structure by updating its mineRound parameter,
        then add it to validFruits and broadcast to network
        '''
        # as close as possible
        hangBlockHeight = self.blockChain.length
        fruit = Fruit(self.id, roundNum, hangBlockHeight)
        self.validFruits[fruit.hangBlockHeight].add(fruit)
        self.nFruitsMined += 1
        return fruit

    def mineBlock(self, roundNum):
        '''
        Append the mined block to chain, process fruits in it by updating their
        includeRound and contBlockHeight params. and broadcast the block
        '''
        # 1. Get fresh fruits
        freshFruits = self.getFreshFruits()
        # 2. Append the block, update fields of included fruits
        block = Block(self.id, roundNum, freshFruits, [])
        self.blockChain.append(block)
        for f in freshFruits:
            f.includeRound = roundNum
            f.contBlockHeight = self.blockChain.length
            self.fruitsInChain[hash(f)] = hash(block)
        self.nBlocksMined += 1
        return block

    def deliver(self, msg):
        '''
        Deliver the received msg and process it according to its type,
        i.e., either put the fruit into the set or add the block to chain
        '''
        if type(msg) is Fruit:
            self.validFruits[msg.hangBlockHeight].add(msg)
        if type(msg) is Block and msg != self.blockChain[-1]: # avoiding duplication in case self-delivery
            self.blockChain.append(msg)
            for fruit in msg.fruits:
                self.fruitsInChain[hash(fruit)] = msg.height

    def getFreshFruits(self):
        '''
        Returns the fruits that are recent w.r.t to chain
        Fresh fruits hang from one the last K blocks and not already in chain,
        i.e., contblockHeight - hangBlockHeight >= k-1
        '''
        fresh = set()
        lastValidHangBlockHeight = max(1, self.blockChain.length - self.k + 1)
        # Fruit can hang from the head of chain
        for pos in range(lastValidHangBlockHeight, self.blockChain.length + 1):
            for f in self.validFruits[pos]:
                if hash(f) not in self.fruitsInChain:
                    fresh.add(f)
        return fresh

    def calculateCost(self):
        hashRate = self.hashFrac * self.environment.networkHashRate
        nDevices = ceil (hashRate / self.environment.deviceHashRate)
        self.initialCost = nDevices * self.environment.costPerDevice
        consumptionPerRound = self.environment.consumptionPerDevice * nDevices * (self.environment.p / 6) # in KWh
        self.costPerRound = consumptionPerRound * self.environment.costPerKWh

    def logUtilityBTC(self, roundNum):
        """
            Measures the value of utility
            and calculates its expected value at roundNum for BTC
        """
        expUtilityVal = roundNum * (self.expGainPerRoundBTC)
        measuredUtilityVal = self.totalRewardBTC  - self.costPerRound*roundNum
        self.utilityLogBTC.append( (measuredUtilityVal, expUtilityVal) )

    def logUtilityFTC(self, roundNum):
        """
            Measures the value of utility
            and calculates its expected value at roundNum for FTC
        """
        expUtilityVal = roundNum * (self.expGainPerRoundFTC)
        measuredUtilityVal = self.totalRewardFTC - self.costPerRound*roundNum
        self.utilityLogFTC.append( (measuredUtilityVal, expUtilityVal) )
