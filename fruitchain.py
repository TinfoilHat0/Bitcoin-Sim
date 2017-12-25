#coding: utf-8
from dataStructures import *
from math import ceil
import random
from collections import defaultdict
import numpy as np
import bisect

class Environment:
    def __init__(self, p = 1, pF = 1, txRate = 5, k = 16):
        '''
        p: pr. of mining a block in a rounds
        pF: pr. of mining a fruit in a round
        txRate: # of txs supplied to system each round
        k: determines how far a fruit can hang

        Environment of the protocol. Handles a mining process.
        '''
        self.p = p
        self.pF = pF
        self.txRate = txRate
        self.k = k
        self.nodes = []
        self.honestNodes = []
        self.corruptNodes = []

        # Mining pool related params
        self.miningPool = set()
        self.poolHashFraction = 0
        self.rewardTime = defaultdict(int) # <K, V> = <Node id, Round num. of last reward>

        # Keep track of txs
        self.unprocessedTxs = []
        self.processedTxs = []

        # Fruitchain related params.
        self.c1 = 1/100
        self.c2 = 1/10
        self.c3 = 1/100
        self.nFruitsInWindow = 0

    def initializeNodes(self, nodes, t = 0):
        '''
        nodes: list of nodes which are in the environment
        t: number of corrupt nodes

        Initialize nodes by putting t of them to corrupt nodes' list
        and (n-t) of them to honest node's list
        '''
        self.nodes = nodes
        self.n = len(nodes)
        self.t = t
        self.blockLeaderProbs = []
        self.fruitLeaderProbs = []
        for i in range(self.n):
            self.blockLeaderProbs.append(self.p*nodes[i].hashFrac)
            self.fruitLeaderProbs.append(self.pF*nodes[i].hashFrac)
            nodes[i].environment = self
            if i < self.n-self.t:
                self.honestNodes.append(nodes[i])
            else:
                self.corruptNodes.append(nodes[i])
        self.blockLeaderProbs.append(1-self.p) # prob. of nobody mines a block in a round
        self.fruitLeaderProbs.append(1-self.pF) # prob. of nobody mines a fruit in a round

    def generateTxs(self, roundNum):
        for i in range(self.txRate):
            fee = 1
            tx = Transaction(roundNum, fee, 1)
            # check this unprocessed txs sorted
            # bisect.insort(self.unprocessedTxs, tx)
            self.unprocessedTxs.append(tx)

    def step(self, roundNum):
        '''
        roundNum: number of the current round
        1. Env. generates txs
        2. Attempt to mine
        3. Send mining results to all nodes
        '''
        #print("Round:" + str(roundNum) + " started.")

        # 1. Generate new txs
        self.generateTxs(roundNum)
        # 2. Check if someone mines
        # Pick an ID for the miner of the block in this round. If ID is n, nobody mines
        blockLeaderID = np.random.choice(self.n+1, 1, p=self.blockLeaderProbs)[0]
        fruitLeaderID = np.random.choice(self.n+1, 1, p=self.fruitLeaderProbs)[0]
        b, f = None, None
        if blockLeaderID != self.n:
            b = self.nodes[blockLeaderID].mineBlock(roundNum)
            self.rewardBitcoin(blockLeaderID, roundNum)
            # self.rewardFruitchain(blockLeaderID, roundNum)
        if fruitLeaderID != self.n and blockLeaderID != fruitLeaderID: # same node can't mine both a block and a fruit
            f = self.nodes[fruitLeaderID-1].mineFruit(roundNum)
        # 3. Broadcast what's been mined
        if b != None or f != None:
            for node in self.nodes:
                node.deliver((b, f))

        # 4. (Optional) update the mining pool
        # self.updateMiningPool(roundNum)

        #print("Round:" + str(roundNum) + " ended.")
        return b, f

    def rewardBitcoin(self, blockLeaderID, roundNum=0):
        """
        blockLeaderID: index of the leader node

        Distributes rewards to miners acc. to Bitcoin rewarding scheme
        If leader is not in pool, he fetches everything from the recently mined head.
        If he's in pool, every member of pool gets a reward w.r.t to their hash fraction
        """
        totalFee = self.nodes[blockLeaderID].blockChain.head.totalFee
        if blockLeaderID not in self.miningPool:
            self.nodes[blockLeaderID].totalBitcoinReward += totalFee
            self.rewardTime[blockLeaderID] = roundNum
            return
        for i in self.miningPool:
            node = self.nodes[i]
            node.totalBitcoinReward += round(totalFee * (node.hashFrac / self.poolHashFraction))
            self.rewardTime[i] = roundNum

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
            self.nodes[blockLeaderID].totalFruitchainReward += (self.c1)*x
            R = (1-self.c1)*x
            # 2. Calculate 'normal' reward
            n0 = R / self.nFruitsInWindow
            # 3. Iterate over last k blocks and distribute rewards to miners
            for b in blockChain[-self.k-1:-1]:
                for f in b.fruits:
                    l = f.contBlockHeight - f.hangBlockHeight - 1 # number of blocks between hanging and containing block]
                    dL = self.c3 * (1 - l/(self.k-1))
                    self.nodes[f.minerID].totalFruitchainReward += n0*(1 - self.c2 + dL)
                    self.nodes[b.minerID].totalFruitchainReward += n0*(self.c2 - dL)
                self.nodes[b.minerID].totalFruitchainReward += n0 # reward of the implicit fruit goes to block miner
            # 4. Slide the window and adjust the number of fruits
            self.nFruitsInWindow -= (blockChain[-self.k-1].nFruits + 1)
            self.nFruitsInWindow += (head.nFruits + 1)
        else:
            self.nFruitsInWindow += (head.nFruits + 1) # +1 is the implicit fruit (see paper)

    def updateMiningPool(self, roundNum):
        """
        Have nodes that wait more than their expected time join the mining pool
        """
        for node in self.honestNodes:
            if (node.id not in self.miningPool) and (roundNum - self.rewardTime[node.id]) >= node.expectedBlockInterval:
                node.joinPool()
                self.poolHashFraction += node.hashFrac

class Node:
    def __init__(self, _id=0, hashFrac=1, env=Environment()):
        '''
        _id: unique id of the node
        blockChain: local chain of the node
        validFruits: valid fruits received/mined by the node; <K, V> = <hangBlockPos, setOfFruits>
        fruitsInChain: fruits that are in the blockchain; <K, V> = <fruitHash, block.height>
        hashFrac: fraction of hash power of the node

        environment: environment of the pair (A, Z)
        k: security parameter
        '''
        self.id = _id
        self.blockChain = Blockchain()
        self.validFruits = defaultdict(set)
        self.fruitsInChain = {}
        self.hashFrac =  hashFrac

        # simulator related parameters
        self.environment = env
        self.k = self.environment.k
        # total reward received by the node acc. Bitcoin sceheme
        self.totalBitcoinReward = 0
        # total reward received by the node acc. Fruitchain sceheme and other related params
        self.totalFruitchainReward = 0
        # expected # of rounds between any 2 block of this node
        self.expectedBlockInterval = ceil( 1 / ( self.environment.p * self.hashFrac ))

    def mineFruit(self, roundNum):
        '''
        Mine the structure by updating its mineRound parameter,
        then add it to validFruits and broadcast to network
        '''
        hangIndex = max(1, self.blockChain.length - self.k) - 1
        fruit = Fruit(self.id, roundNum, hangIndex)
        self.validFruits[fruit.hangBlockHeight].add(fruit)

        #print("Node:" + str(self.id) + " mined a fruit!" )
        return fruit

    def mineBlock(self, roundNum):
        '''
        Append the mined block to chain, process fruits in it by updating their
        includeRound and contBlockHeight params. and broadcast the block

        TODO:There can be an upper bound on # of fruits per block later
        '''
        # Do tx selection
        freshFruits = self.getFreshFruits()
        block = Block(self.id, roundNum, freshFruits, [])
        self.defaultTxSelection(roundNum, block)
        # Append the block, update fruits in it
        self.blockChain.append(block)
        for f in freshFruits:
            f.includeRound = roundNum
            f.contBlockHeight = self.blockChain.length
            self.fruitsInChain[hash(f)] = hash(block)
        #print("Node:" + str(self.id) + " mined a block!" )
        return block

    def joinPool(self):
        """
        Node joins the mining pool
        """
        self.environment.miningPool.add(self.id)

    def deliver(self, msg):
        '''
        Deliver the received msg and process it according to its type,
        i.e., either put the fruit into the set or add the block to chain
        '''
        b, f = msg[0], msg[1]
        if f != None:
            self.validFruits[f.hangBlockHeight].add(f)
        if b != None and b != self.blockChain[-1]:
            self.blockChain.append(b)
            for fruit in b.fruits:
                self.fruitsInChain[hash(fruit)] = b.height

    def getFreshFruits(self):
        '''
        Returns the fruits that are recent w.r.t to chain
        (i.e., they hang from one the last K blocks and not already in chain)
        '''
        fresh = set()
        lastValidHangBlockHeight = max(1, self.blockChain.length-self.k)
        # Get rid of fruits that lost their recency. Note that a fruit can not become recent once it has lost it. Chain is ever-growing.
        self.validFruits.pop(lastValidHangBlockHeight-1, None)
        # Fruit can hang from the head of chain
        for pos in range(lastValidHangBlockHeight, self.blockChain.length+1):
            for f in self.validFruits[pos]:
                if hash(f) not in self.fruitsInChain:
                    fresh.add(f)
        return fresh

    def selectAllTxs(self, roundNum, block):
        '''
        Put all unprocessed txs to block, ignoring space limitations i.e., blocks
        have unlimited size
        '''
        for tx in self.environment.unprocessedTxs:
            tx.includeRound = roundNum
            block.totalFee += tx.fee
            block.txs.append(tx)
            self.environment.processedTxs.append(tx)
        self.environment.unprocessedTxs = []

    def defaultTxSelection(self, roundNum, block):
        '''
        Simply fetch txs from the unprocessed tx list of environment
        until you can't fill anymore
        Assumes unprocessed txs are sorted
        '''
        spaceLeft = block.size
        txList = self.environment.unprocessedTxs
        for i in range(len(txList)-1, -1, -1):
            tx = txList[i]
            if spaceLeft >= tx.size:
                # update tx include round and total fee of node
                tx.includeRound = roundNum
                block.totalFee += tx.fee
                block.txs.append(tx)
                spaceLeft -= tx.size
                # add tx to block/processed and remove tx from unprocessed
                self.environment.processedTxs.append(tx)
                del txList[i]
            else:
                return
