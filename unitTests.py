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


class TestEnvironment(unittest.TestCase):

    def test_initializeNodes(self):
        '''
        Initialize an environment by corrupting some number of nodes,
        check if size of corrupt nodes/honest nodes are correct
        '''
        env = Environment(0.2, 0.5)
        nodes = [Node(1, 0.3), Node(2, 0.2), Node(3, 0.5)]
        # Corrupt a node
        env.initializeNodes(nodes, 1)
        self.assertEqual(env.nodes, nodes)
        self.assertEqual(env.corruptNodes, [nodes[i] for i in range(2, 3)])
        self.assertEqual(env.honestNodes, [nodes[i] for i in range(0, 2)])

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

        # node should have mined only a block)
        self.assertEqual(f, None)
        self.assertEqual(b.minerID, 1)
        self.assertEqual(b.mineRound, 1)
        self.assertEqual(node.blockChain.length, 2)


    def test_defaultTxSelection(self):
        '''
        Generate 105 txs in a round,
        have a node process them
        '''

        env = Environment()
        node = Node(1)
        env.initializeNodes([node])

        # Generate 105 txs in a round 1
        env.txRate = 105
        env.generateTxs(1)
        self.assertEqual(len(env.unprocessedTxs), 105)
        # Node mines a block in rnd2 which should contain b.size txs
        node.mineBlock(2)
        b = node.blockChain[1]
        remainingTxs = max(0, 105 - b.size)
        self.assertEqual(len(b.txs) , min(b.size, 105))
        self.assertEqual(len(env.processedTxs), min(b.size, 105))
        self.assertEqual(len(env.unprocessedTxs), remainingTxs)

        # Node mines the next block in rnd3 which should contain remainingTxs
        node.mineBlock(3)
        b = node.blockChain[2]
        self.assertEqual(len(b.txs), remainingTxs)
        self.assertEqual(len(env.processedTxs), 105)
        self.assertEqual(len(env.unprocessedTxs), 0)

    def test_rewardFruitchain(self):
        '''
        Test algorithm in the following chain:
        genesis <- b1 <- b2 <-b3

        b1 has a single fruit. Hangs from genesis.
        b2 has a 2 fruits. They both hang from genesis.
        b3 has 100 tx fee.
        Let k = 2 and have a different miner for each fruit/block.

        TODO: Fix this acc. to new delivery scheme
        '''

        nodes = []
        for i in range(0, 6):
            nodes.append(Node(i))
        env = Environment()
        env.initializeNodes(nodes)
        env.k = 2

        # miner0 mines f1, miner1 mines b1 and puts it in it
        f1 = Fruit(0, 1, 0)
        f1.contBlockHeight = 2
        b1 = Block(1, 0, {f1})

        # miner2 mines f2, miner3 mines f3, miner4 mines b2 and puts fruits in it
        f2, f3 = Fruit(2, 1, 0), Fruit(3, 1, 0)
        f2.contBlockHeight = 3
        f3.contBlockHeight = 3
        b2 = Block(4, 0, {f2, f3})

        # miner3 mines b3 which has a total fee of 100
        b3 = Block(5)
        b3.totalFee = 100

        chain = Blockchain()
        chain.append(b1)
        chain.append(b2)
        chain.append(b3)
        
        env.rewardFruitchain(chain)

        # The following values are calculated by hand acc. to Fig 4 in Fruitchain Impl. paper
        self.assertEqual(round(nodes[0].totalFruitchainReward, 3), 18.018)
        self.assertEqual(round(nodes[1].totalFruitchainReward, 3), 21.582)
        self.assertEqual(round(nodes[2].totalFruitchainReward, 2), 17.82)
        self.assertEqual(round(nodes[3].totalFruitchainReward, 2), 17.82)
        self.assertEqual(round(nodes[4].totalFruitchainReward, 2), 23.76)
        self.assertEqual(nodes[5].totalFruitchainReward, 1)

if __name__ == '__main__':
    unittest.main()
