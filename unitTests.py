#coding: utf-8
import unittest
from fruitchain import *

class TestDataStructures(unittest.TestCase):

    def test_blockChainEq(self):
        chain1 = Blockchain()
        chain1.append(Block())
        chain2 = Blockchain()

        self.assertNotEqual(chain1, chain2)

        chain2.append(Block())

        self.assertEqual(chain1, chain2)

    def test_blockIterator(self):
        block = Block()
        chain = Blockchain()
        chain.append(block)

        for b in chain:
            self.assertEqual(b, block)

    def test_Transaction(self):
        t = Transaction(1, 10, 5)
        t2 = Transaction(1, 20, 10)
        self.assertEqual(t, t2)
        t2.size = 20
        self.assertNotEqual(t, t2)

class TestNode(unittest.TestCase):

    def test_fruitMining(self):
        '''
        Mine 2 fruits and see if they're correctly
        added to list of valid fruits
        '''
        node = Node(1)

        # mine them in rounds 1 and 2
        node.mineFruit(1)
        f = node.validFruits[1].pop()
        self.assertEqual(f.minerID, 1)
        self.assertEqual(f.hangBlockHeight, 1)
        self.assertEqual(f.mineRound, 1)

        # Bcast in round 2
        node.mineFruit(2)
        f = node.validFruits[1].pop()
        self.assertEqual(f.minerID, 1)
        self.assertEqual(f.hangBlockHeight, 1)
        self.assertEqual(f.mineRound, 2)


    def test_getFreshFruits(self):
        '''
        Mine some fruits, see if they're returned by the function
        '''
        node = Node(1)
        # have node mine 2 fruits(resp. in rounds 1 and 2) that hangs from the genesis
        node.mineFruit(1)
        node.mineFruit(2)

        # They must be recent as we haven't added any block
        freshFruits = node.getFreshFruits()
        self.assertEqual(node.validFruits[1], freshFruits)

        # After adding some blocks, they should lose their recencyc (default k is 16)
        for i in range(16):
            node.blockChain.append(Block())

        freshFruits = node.getFreshFruits()
        self.assertEqual(set(), freshFruits)


    def test_blockMining(self):
        '''
        Mine a block in round 3, see if it's added
        to blockchain with correct parameters
        '''
        node = Node(1)
        # have node mine a fruit
        node.mineFruit(1)
        # gather fruits that hangs from genesis in round 3
        block = node.mineBlock(3)
        self.assertEqual(node.blockChain.length, 2)
        f = node.validFruits[1].pop()
        self.assertEqual(f.hangBlockHeight, 1)
        self.assertEqual(f.contBlockHeight, 2)
        self.assertEqual(f.includeRound, 3)

    def test_calculateCostPerRound(self):
        node = Node(1)
        env = Environment()
        # Hard-coded constants taken from real world data of Bitcoin
        env.coinbaseReward = 12.5
        env.networkHashRate = 16 * (10**5) # Th/s
        env.usdToBTC = 9 * (10**-5) # 1 USD = 0.00009 BTC
        env.costPerKWh = 18 * (10**-6) # In France, cost per KWh = 0.2 USD = 0.000018 BTC
        env.deviceHashRate = 14 # TH/s, AntMiner S9
        env.costPerDevice = 0.23 # BTC
        env.consumptionPerDevice = 1.372 # KWh

        node.environment = env
        node.calculateCost()

        self.assertEqual(node.initialCost, 26285.780000000002)
        self.assertEqual(node.costPerRound, 0.47040117600000003)



class TestEnvironment(unittest.TestCase):

    def test_initializeNodes(self):
        '''
        Initialize an environment by corrupting some number of nodes,
        check if size of corrupt nodes/honest nodes are correct
        '''
        env = Environment(0.2, 0.5)
        nodes = [Node(1, 0.3), Node(2, 0.2), Node(3, 0.5)]
        # Corrupt a node
        env.initializeNodes(nodes)
        # check if hash fractions are correct
        self.assertEqual(env.blockLeaderProbs, [0.06, 0.04000000000000001, 0.1, 0.8]) # 0.2 + 0.2 = 0.400...1 due to floating point arithmatics
        self.assertEqual(env.fruitLeaderProbs, [0.15, 0.1, 0.25, 0.5])


    def test_step(self):
        '''
        Environment runs a round
        '''
        env = Environment()
        node = Node(1)
        node.environment = env
        # env runs round 1
        env.initializeNodes([node])
        b, f = env.step(1)

        # node should have mined a fruit and a block
        self.assertEqual(f, Fruit(1, 1, 0))
        self.assertEqual(b.minerID, 1)
        self.assertEqual(b.mineRound, 1)
        self.assertEqual(node.blockChain.length, 2)

    def test_rewardFruitchain(self):
        '''
        Test algorithm in the following chain:
        genesis <- b1 <- b2 <-b3

        b1 has a single fruit. Hangs from genesis.
        b2 has a 2 fruits. They both hang from genesis.
        b3 has 100 tx fee.
        Let k = 2 and have a different miner for each fruit/block.
        '''
        nodes = []
        for i in range(0, 6):
            nodes.append(Node(i))
        env = Environment()
        env.initializeNodes(nodes)
        env.k = 2

        # Miner0 mines a fruit
        f1 = nodes[0].mineFruit(1)
        f1.contBlockHeight = 2
        f1.hangBlockHeight = 1
        for node in nodes:
            node.deliver(f1)

        # Miner1 mines a b1, puts f1 in it
        b1 = nodes[1].mineBlock(2)
        for node in nodes:
            node.deliver(b1)

        # Resp. miner2 mines f2 and miner3 mines f3
        f2 = nodes[2].mineFruit(3)
        f3 = nodes[3].mineFruit(4)
        f2.contBlockHeight = 3
        f2.hangBlockHeight = 1
        f3.contBlockHeight = 3
        f3.hangBlockHeight = 1
        for node in nodes:
            node.deliver(f2)
        for node in nodes:
            node.deliver(f3)

        # Miner4 mines b2, puts f2 and f3 in it
        b2 = nodes[4].mineBlock(5)
        for node in nodes:
            node.deliver(b2)

        b3 = nodes[5].mineBlock(6)
        for node in nodes:
            node.deliver(b3)

        # Since k = 2 and we mined the 3rd block, rewards should have been distributed
        # We have (1+1) + (2+1) = 5 fruits in this window. +1 is due to implicit fruit.
        b3.totalFee = 100
        env.nFruitsInWindow = 5
        env.rewardFruitchain(5)

        # The following values are calculated by hand acc. to Fig 4 in Fruitchain Implementation paper
        self.assertEqual(round(nodes[0].totalFTCReward, 3), 18.018)
        self.assertEqual(round(nodes[1].totalFTCReward, 3), 21.582)
        self.assertEqual(round(nodes[2].totalFTCReward, 2), 17.82)
        self.assertEqual(round(nodes[3].totalFTCReward, 2), 17.82)
        self.assertEqual(round(nodes[4].totalFTCReward, 2), 23.76)
        self.assertEqual(nodes[5].totalFTCReward, 1)

if __name__ == '__main__':
    unittest.main()
