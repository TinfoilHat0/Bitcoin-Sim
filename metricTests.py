
# coding: utf-8

# In[1]:


from simulator import *
import createPlots as cp
import numpy as np
import random


# In[2]:


# We fix number of nodes and parameters of fruitchain(c1,c2,c3,k) under all settings. 
n, k = 14, 16
avgOver = 5 # Average each point over 5 runs


# In[3]:


# 1. Parameters for Metric vs. Window Length
# Fix c0 = 10 (e.g p = 1/10, pF = 1)
p, pF = 1/10, 1
hashFracs = [1/n for i in range(n)]
windowLengths = [1, 7, 14, 21, 30] #days


# In[ ]:


# 1. Metric vs. Window Length, cont.
for length in windowLengths:
    fileName = "sim_results/fairnessTests/lengthTests/" 
    r = ceil(1/p)*144*length # on avg. 144 blocks per day
    sim = Simulator(n, r, p, pF, hashFracs, k, avgOver)
    sim.run(fileName + "length" + str(length) + "_")


# In[4]:


#2. Parameters Metric vs. c_0
# Fix window length to 30 days.
windowLength = 30
hashFracs = [1/n for i in range(n)]
c0Vals = [1, 20, 40, 60, 80, 100] # pF/p


# In[ ]:


#2. Metric vs. c_0, cont.
for c0 in c0Vals:
    fileName = "sim_results/fairnessTests/c0Tests/" 
    p = 1/max(c0Vals) 
    pF = c0 * p
    r = ceil(1/p)*144*windowLength # on avg. 144 blocks per day
    sim = Simulator(n, r, p, pF, hashFracs, k, avgOver)
    sim.run(fileName + "c0" + str(c0) + "_")


# In[5]:


#3. Metric vs. hash rate fraction settings
# Fix window length to 30 days, c0 to 10. 
# Vary hash fractions settings:All same, real data, some random setting with big nodes
setting1 = [1/n for i in range(n)] # All same
setting2 = [0.267, 0.174, 0.118, 0.106, 0.075, 0.068, 0.062, 0.043, 0.025, 0.019, 0.019, 0.012, 0.006, 0.006] # Real distribution
hashSettings = [setting1, setting2]
windowLength = 30


# In[ ]:


# #3. Metric vs. hash rate fraction settings, cont.
for i in range(len(hashSettings)):
    fileName = "sim_results/fairnessTests/hashFracTests/" 
    p, pF = 1/10, 1
    r = ceil(1/p)*144*windowLength # on avg. 144 blocks per day
    sim = Simulator(n, r, p, pF, hashSettings[i], k, avgOver)
    sim.run(fileName + "hashSetting" + str(i) + "_")


# In[6]:


cp.plotFairnessMetric(windowLengths, c0Vals, hashSettings)

