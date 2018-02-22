#coding: utf-8
from fruitchain import *
from random import randint
import math as mt

class Simulator:
    def __init__(self, n, p, pF, r, hashFracs, avgOver=1):
        '''
        n: number of nodes
        r: number of rounds
        p: pr. of the system mining a block in a round
        pF: pr. of the system mining a fruit in a round
        hashFracs: hash rate fraction of each node
        avgOver: number of time this simulation runs with corresponding parameters
        '''
        self.n = n
        self.p = p
        self.pF = pF
        self.r = r
        self.hashFracs = hashFracs
        self.avgOver = avgOver

    def initializeSim(self):
        self.environment = Environment(self.p, self.pF, self.r)
        self.nodes = []
        for i in range(self.n):
            self.nodes.append(Node(i, self.hashFracs[i], self.environment))
        self.environment.initializeNodes(self.nodes)

    def run(self, filename=''):
        """ Runs the simulation for r rounds, averaged over avgOver times """
        for i in range(1, self.avgOver+1):
            self.initializeSim()
            for j in range(1, self.r+1):
                self.environment.step(j)
                if j%50000 == 0:
                    print('Round:' + str(j) + ' has finished.')
            print('Simulation for r=' + str(j) + ' rounds has finished!')
            print("Simulation " + str(i) + " has finished!")
            #self.logValidationData()
            #self.logMetricData()
        print("All simulations have finished!")
        print('Writing results to file: ' + filename)
        #self.writeValidationData(filename)
        #self.writeMetricData()
        print("Finished!")
