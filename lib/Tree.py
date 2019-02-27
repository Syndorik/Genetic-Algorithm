import numpy as np
import networkx as nx
import pandas as pd
import random
from operator import itemgetter
import matplotlib.pyplot as plt

class Tree:

    def __init__(self,list_files,prufer = []):
        self.nodeNum = list_files[0][0][0]
        self.flow = list_files[1]
        self.varCost = list_files[2]
        self.fixCost = list_files[3]
        self.alpha = list_files[4][0][0]
        self.cap = list_files[5]
        self.origin = list_files[6]
        self.destination = list_files[7]
        self.fitness = -1
        if(prufer == []):
            self.prufer = [random.randint(0,self.nodeNum-1) for k in range(self.nodeNum -2)]
            self.calc_fit()
        else:
            self.prufer = prufer
    
    def pruferToTree(self):
        tree = []
        T = range(0, len(self.prufer)+2)

        # the degree of each node is how many times it appears
        # in the sequence
        deg = [1]*len(T)
        for i in self.prufer: deg[i] += 1

        # for each node label i in a, find the first node j with degree 1 and add
        # the edge (j, i) to the tree
        for i in self.prufer:
            for j in T:
                if deg[j] == 1:
                    tree.append((i,j))
                    # decrement the degrees of i and j
                    deg[i] -= 1
                    deg[j] -= 1
                    break

        last = [x for x in T if deg[x] == 1]
        tree.append((last[0],last[1]))

        return tree

    def individualFitness(self):    
        Tree_Edges =self.pruferToTree()
    
        Graph = nx.Graph(Tree_Edges)
        All_Pairs_Path = dict(nx.all_pairs_shortest_path(Graph))


        Hubs = np.unique(self.prufer)
        FixedCost = self.fixCost[Hubs].sum()
        
        VarCost = 0
        FlowToHub = np.zeros(self.nodeNum)

        #First part of the sum computation
        for i in range(self.nodeNum):
            for j in range(self.nodeNum):
                if j > i:
                    for x in range(len(All_Pairs_Path[i][j])-1):
                        Route = All_Pairs_Path[i][j]
                        if Route[x] in Hubs and Route[x+1] in Hubs:
                            VarCost = VarCost + self.alpha * self.varCost[Route[x],Route[x+1]] * (self.flow[i,j]+self.flow[j,i])
                        else:
                            VarCost = VarCost + self.varCost[Route[x],Route[x+1]] * (self.flow[i,j]+self.flow[j,i])
            Fitness = FixedCost + VarCost

        # Calculating the Entering flow to Each Hub #
        for i in range(len(Tree_Edges)):
            if Tree_Edges[i][0] not in Hubs:
                FlowToHub[Tree_Edges[i][1]] = FlowToHub[Tree_Edges[i][1]] + (self.origin[Tree_Edges[i][0]]+self.destination[Tree_Edges[i][0]])
            elif Tree_Edges[i][1] not in Hubs:
                FlowToHub[Tree_Edges[i][0]] = FlowToHub[Tree_Edges[i][0]] + (self.origin[Tree_Edges[i][1]]+self.destination[Tree_Edges[i][1]])
        for i in range(len(Hubs)):
            FlowToHub[Hubs[i]] = FlowToHub[Hubs[i]] + (self.origin[Hubs[i]]+self.destination[Hubs[i]])


        # Feasibility Check: Capacity Constraint #
        Exceed = np.subtract(self.cap,FlowToHub)
        ExceedCap = Exceed[Hubs,Hubs]
        if min(ExceedCap) < 0:
            Fitness = np.dot(Fitness,100000000)
        
        return Fitness

    def calc_fit(self):
        self.fitness = self.individualFitness()

