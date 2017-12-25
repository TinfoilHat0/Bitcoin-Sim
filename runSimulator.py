#coding: utf-8

#python3 -m cProfile -s time runSimulator.py 10 0 1000 0.1 0.2
from simulator import *
import sys

# Setup the parameters
n, t, r = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
p, pF = float(sys.argv[4]), float(sys.argv[5])
hashFracs = [1/n for i in range(n)]
# Run the simulation
sim = Simulator(n, t, r, p, pF, hashFracs)
sim.run()
