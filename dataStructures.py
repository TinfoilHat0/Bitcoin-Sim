import random
#coding: utf-8
class Transaction:
    def __init__(self, bcastRound, fee, size=1):
        self.bcastRound = bcastRound
        self.fee = fee
        self.size = size # in bytes
        self.includeRound = 0 # updated by the miner

    def __eq__(self, other):
        return self.fee / self.size == other.fee / other.size

    def __lt__(self, other):
        return self.fee / self.size < other.fee / other.size

    def __repr__(self):
        return str(self.fee / self.size)


class Fruit:
    def __init__(self, minerID=-1, mineRound=0, hangBlockHeight=0):
        '''
        minerID: id of miner who mined the fruit
        pos: -index- of the block in blockchain which this fruit hangs from
        '''
        self.minerID = minerID
        self.hangBlockHeight = hangBlockHeight # height of the block that this fruit hangs from
        self.mineRound = mineRound
        self.includeRound = 0
        self.contBlockHeight = 0 # height of the block that contains the fruit

    def __hash__(self):
        # minerID||mineRound||0 uniquely determines a fruit where || denotes concatanetion
        # 0 is there to distinct block and fruits
        return hash(str(self.minerID) + str(self.mineRound) + str(0))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return str(self.minerID) + '|' + str(self.mineRound) + '|' + str(0)


class Block:
    def __init__(self, minerID=-1, mineRound=0, fruits=set(), txs=[]):
        self.minerID = minerID
        self.mineRound = mineRound
        self.fruits = fruits
        self.txs = txs
        self.totalFee = 12.5 #random.randint(1, 13) #sum of fees in txs set
        self.height = -1 # height in blockchain

        self.nFruits = len(fruits)
        self.size = 10 # in bytes

    def __hash__(self):
        # minerID||mineRound||1 uniquely determines a block where || denotes concatanetion
        # 1 is there to distinct block and fruits
        return hash(str(self.minerID) + str(self.mineRound) + str(1))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return str(self.minerID) + '|' + str(self.mineRound) + '|' + str(1)


class Blockchain:
    def __init__(self):
        self.chain = [] # just a list, not a tree, can be changed later if we broadcast blocks
        self.length = 0
        self.append(Block()) # every chain starts with the genesis

    def append(self, b):
        self.chain.append(b)
        self.length += 1
        b.height = self.length
        self.head = b

    def __getitem__(self, key):
        return self.chain[key]

    def __eq__(self, other):
        if self.length != other.length:
            return False
        else:
            for i in range(self.length):
                if self.chain[i] != other.chain[i]:
                    return False
        return True

    def __iter__(self):
        self.ctr = 0
        return self

    def __next__(self):
        if self.ctr < self.length:
            b = self.chain[self.ctr]
            self.ctr += 1
            return b
        else:
            raise StopIteration
