import random

class Fruit:
    def __init__(self, minerID=-1, mineRound=0, hangBlockHeight=0):
        '''
        minerID: id of miner who mined the fruit
        pos: -index- of the block in blockchain which this fruit hangs from
        '''
        self.minerID = minerID
        self.mineRound = mineRound
        self.hangBlockHeight = hangBlockHeight

        self.includeRound = 0 # round in which fruit is included in a block, consequently in the blockchain
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
    def __init__(self, minerID=-1, mineRound=0, fruits=[]):
        self.minerID = minerID
        self.mineRound = mineRound

        self.reward = 12.5 #total reward a block brings
        self.height = 0 # height in blockchain
        self.fruits = fruits
        self.nFruits = len(fruits)

    def __hash__(self):
        # minerID||mineRound||1 uniquely determines a block where || denotes concatanetion
        # 1 is there to distinct block and fruits
        return hash(str(self.minerID) + str(self.mineRound) + str(1))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return str(self.minerID) + '|' + str(self.mineRound) + '|' + str(1)

class Blockchain:
    def __init__(self, k=16):
        self.chain = []
        self.length = 0
        
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
