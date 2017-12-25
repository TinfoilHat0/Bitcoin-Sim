def getExpectedConsensusViolation(self):
      '''
      Computes the expected number of consensus violations.
      (Consider delta=1 for the analysis below)

      Observation: At the beginning of each round, all nodes have chains of equal length.

      We DON'T have a violation at round r iff:
      1) Only 1 node mines during the round, i.e., there will be only 1 chain of max_length
      2) We don't have a consensus violation at round r-1 and nobody mines during round r

      Define the events V_r, M_i(resp. their negations as V_r' and M_i') as follows:
      V_r: There's consensus violation at round r
      M_i: i nodes mined a block during the round

      Then, the probability of not having a consensus violation at round r is:
      P(V_r') = P(M_1) + P(V_(r-1)')*P(M_0)
      with base case P(V_0) = 0 as all the nodes start with same with the same genesis block

      Then expected is simply E = sum( P(V_r) ) from r=1 to nRounds
      '''
      probs = [1] # [P(V_0)', .., P(V_nRounds')]
      pM1 = self.n * self.p * ((1-self.p)**(self.n-1))
      pM0 = (1-self.p)**self.n

      for r in range(1, self.nRounds+1):
          _p = pM1 + probs[r-1]*pM0 # P(V_r')
          probs.append(_p)

      expected = 0
      for p in probs:
          expected += (1-p)
      return expected

  def testFruitFreshness(self):
      '''
      Checks whether fruit-freshness is satisfied.
      Every fruit mined at round r < (nRounds - wait) should be in a position
      of at least K deep on chain of every honest node for every round _r > r + wait.
      Wait is calculates as below.
      '''
      # Take division by zero into account?
      alpha = 1-(1-self.p)**((1-self.rho)*self.n) # Pr(At least a honest mines in a round)
      beta = self.rho*self.n*self.p # Expected number of blocks that adversary mines in a round
      gamma = alpha/(1 + self.delta*alpha) # Effective mining power of honest nodes
      wait = ceil(2*self.delta + 2*self.K/(gamma))
      #print("Wait:" + str(wait))

      for r in range(1, self.nRounds-wait):
          fList = self.environment.minedFruits[r] # All the fruits mined at round r
          _r = r + wait
          for f in fList:
              for chain in self.environment.blockChains[_r]:
                  pos = self.getFruitPosition(chain, f) # TODO:Get height from the fruits?
                  depth = chain.length - pos   # Depthness is the distance from the head of chain (-1 here?)
                  if depth < self.K:
                      print("Fruit freshness failed")
                      print("Pos:" + str(pos) + " Depth:" + str(depth))
                      return (False, f)

      print("Fruit freshness satisfied")
      return True



      """
        These are for the old model
        """

def getAvgHonestChainLength(self):
    # E[L] = 1 + p + (r-1)E[X_i]
    expected = 1 + self.p + (self.r-1)*self.eXi
    sm = 0
    for node in self.environment.honestNodes:
        sm += node.blockChain.length
        avg = sm / self.n
        print("Avg. honest chain length: " + str(avg) + " Expected:" + str(expected))

def getNConsensusViolation(self):
            '''
            Calculates the number of rounds in which there's a "consensus violation"

            Def: We have a consensus violation at round r, if at the end of round
            there exists at least 2 chains of max_length that differ in at least 1 block
            where max_length = max(len(chain_1), ..., len(chain_nNodes)).
            '''
            pXi_0 = (1-self.p)**(self.n-self.t)
            pYi_1 = self.p*(self.n-self.t)*((1-self.p)**(self.n-self.t-1))
            expected = 0
            for i in range(1, self.r+1):
                expected += pYi_1*(pXi_0**i - 1)/(pXi_0-1) + pXi_0**i
            expected = self.r - expected
            print("# of consensus violations: " + str(self.nConsensusViolation) + " Expected:" + str(expected))
            return self.nConsensusViolation


        def getAvgFruitPerBlock(self):
            # E[F] = (n-t)*pF/P(X_i)
            pXi_1 = 1-((1-self.p)**(self.n - self.t))
            expected = (self.n-self.t)*self.pF/pXi_1
            avg = 0
            for node in self.environment.honestNodes:
                sm = 0
                for b in node.blockChain:
                    sm += b.nFruits
                avg += sm / (node.blockChain.length-1) # exclude genesis block
            avg  /=  self.n
            print("Avg. fruit per block:" + str(avg) + " Expected: " + str(expected))
            return avg


    def copyChain(self, other):
        '''
        Copy the blocks from other to self.

        Find the 1st pos which they have the same block, copy from other
        to self up to that point.
        '''
        if other.length <= self.length:
            return

        for i in range(self.length-1, -1, -1):
            if self[i] == other[i]:
                break

        for j in range(i+1, other.length):
            self.append(copy.deepcopy(other[j]))
