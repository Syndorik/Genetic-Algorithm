import random
import copy
import os
import time
import math
import csv

from Tree import Tree
from TreePop import TreePop
import copy

from joblib import Parallel, delayed
"""
try:
    from tkinter import *
    from tkinter.ttk import *
except Exception as e:
    print("[ERROR]: {0}".format(e))
    from Tkinter import *
"""



class GA:
    
    def __init__(self,list_files,k_mut_prob = 0.4, k_crossover = 3, tournament_size=7, elitism =True, method = "swap"):
        self.k_mut_prob = k_mut_prob
        self.tournament_size = tournament_size
        self.elitism = elitism
        self.list_files = list_files
        self.k_crossover = k_crossover
        self.nodeNum = list_files[0][0][0]
        self.method = method
    
    @staticmethod
    def swap(tree, mut_pos1, mut_pos2):

        tmp_tree = copy.deepcopy(tree)
        # if they're the same, skip to the chase
        if mut_pos1 == mut_pos2:
            return tmp_tree

        # Otherwise swap them:
        hub1 = tmp_tree.prufer[mut_pos1]
        hub2 = tmp_tree.prufer[mut_pos2]

        tmp_tree.prufer[mut_pos2] = hub1
        tmp_tree.prufer[mut_pos1] = hub2

        return tmp_tree
    
    @staticmethod
    def swap_2opt(tree, mut_pos1, mut_pos2):
        tmp_tree = copy.deepcopy(tree)
        # if they're the same, skip to the chase
        if mut_pos1 == mut_pos2:
            return tmp_tree
        
        if(mut_pos1>mut_pos2):
            tmp = mut_pos1
            mut_pos1 = mut_pos2
            mut_pos2 = tmp
        
        fp = [tree.prufer[l] for l in range(mut_pos1)]
        lp = [tree.prufer[l] for l in range(mut_pos2+1, len(tree.prufer))]
        middle = [tree.prufer[l] for l in range(mut_pos2,mut_pos1-1,-1)]
        tree.prufer = fp+middle+lp
        return tree
    
    def tournament_select(self, population):
        '''
        TreePop() --> Tree(),TreePop()

        Randomly selects tournament_size amount of Tree() from the input population.
        Takes the fittest from the smaller number of Tree(). 

        Principle: gives worse Tree() a chance of succeeding, but favours good Tree()
        The first argument is the Tree with the best fitness, we call this func over and over until we have a new population
        '''

        # New smaller population (not intialised)
        tournament_pop = TreePop(self.tournament_size,self.list_files)

        # fills it with random individuals (can choose same twice)
        for i in range(self.tournament_size-1):
            tournament_pop.tree_pop.append(random.choice(population.tree_pop))
        
        # returns the fittest:
        return tournament_pop.get_fittest(),tournament_pop
    
    def crossover_kpoint(self, parent1, parent2):
        """
        Same as crossover_random. But this time there are k points and not just a start_pos and end_pos

        """
        # new child
        child_Tree = Tree(self.list_files, prufer = [None for k in range(self.nodeNum-2)])

        #k_crossover random point
        k_rd_point = []
        while((len(list(set(k_rd_point)))!= self.k_crossover) and (len(k_rd_point) !=self.k_crossover)):
            tmp = random.randint(0,len(parent1.prufer))
            if tmp not in k_rd_point:
                k_rd_point.append(tmp)
        k_rd_point.sort()

        start = 0
        cpt = 0
        parent_to_choose = [parent1, parent2]

        #Creating the child prufer sequence. If k_crossover = 3, we have [parent1,parnet2,parent1]
        for end in k_rd_point:
            for i in range(start,end):
                child_Tree.prufer[i] = parent_to_choose[cpt%2].prufer[i]
            start = end
            cpt+=1
        
        #Replce the last None with the parents who should be last
        for i in range(len(parent2.prufer)):
            # complete the prufer sequence with parent2
            if child_Tree.prufer[i] == None :
                child_Tree.prufer[i] = parent_to_choose[cpt%2].prufer[i]
        

        child_Tree.calc_fit()


        return child_Tree
    
    def crossover_random(self, parent1, parent2):
        '''
        Tree(), Tree() --> Tree()

        Returns a child tree Tree() after breeding the two parent Tree. 
        Trees must be of same length.

        Breeding is done by selecting a random range of parent1, and placing it into the empty child route (in the same place).
        Gaps are then filled in, without duplicates, in the order they appear in parent2.

        For example:
            parent1: 0123456789
            parent1: 5487961320

            start_pos = 0
            end_pos = 4

            unfilled child: 01234*****
            filled child:   0123458796

            * = None

        '''

        # new child
        child_Tree = Tree(self.list_files, prufer = [None for k in range(self.nodeNum-2)])

        # Two random integer indices of the parent1:
        start_pos = random.randint(0,len(parent1.prufer))
        end_pos = random.randint(0,len(parent1.prufer))


        #### takes the sub-route from parent one and sticks it in itself:
        # if the start position is before the end:
        if start_pos < end_pos:
            # do it in the start-->end order
            for x in range(start_pos,end_pos):
                child_Tree.prufer[x] = parent1.prufer[x] # set the values to eachother

        # if the start position is after the end:
        elif start_pos > end_pos:
            # do it in the end-->start order
            for i in range(end_pos,start_pos):
                child_Tree.prufer[i] = parent1.prufer[i] # set the values to eachother


        # For the None values, replace it with parent2
        for i in range(len(parent2.prufer)):
            # complete the prufer sequence with parent2
            if child_Tree.prufer[i] == None :
                child_Tree.prufer[i] = parent2.prufer[i]

        # returns the child route (of type Route())
        child_Tree.calc_fit()
        return child_Tree

    def mutate(self, tree_mut):
        '''
        Tree() --> Tree()

        Swaps two random indexes in the childs prufer sequence.
        Runs k_mut_prob*100 % of the time
        '''

        tmp_tree = copy.deepcopy(tree_mut)
        # k_mut_prob %
        if random.random() < self.k_mut_prob:

            # two random indices:
            mut_pos1 = random.randint(0,len(tmp_tree.prufer)-1)
            mut_pos2 = random.randint(0,len(tmp_tree.prufer)-1)

            print("ind1 : {}".format(mut_pos1))
            print("ind2 : {}".format(mut_pos2))

            tmp_tree = GA.swap(tmp_tree,mut_pos1,mut_pos2)

        # Recalculate the length of the route (updates it's .length)
        tmp_tree.calc_fit()

        return tmp_tree

    def mutate_swap(self,tree_mut):
        '''
        Tree() --> Tree()

        Swaps two random indexes in route_to_mut.route. Here it's more intelligent since the swap is effective only if the fitness function
        after swap is lower.
        This method allows us to have a good local search on solutions
        Runs k_mut_prob*100 % of the time
        '''
        tree = copy.deepcopy(tree_mut)
        tree.calc_fit()
        # k_mut_prob %
        breakk = False
        lenn = len(tree.prufer)
        
        if random.random() < self.k_mut_prob:
            for i in range(lenn):
                for j in range(lenn): # i is a, i + 1 is b, j is c, j+1 is d
                    tmp_tree = GA.swap(tree,i,j)
                    tmp_tree.calc_fit()
                    if(tree.fitness > tmp_tree.fitness):
                        tree = tmp_tree
                        breakk = True
                        break
                if breakk:
                    breakk = False
                    break
            tree.calc_fit()
        return tree
    

    def mutate_swap_nerfed(self,tree_mut):
        '''
        Tree() --> Tree()

        Swaps two random indexes in route_to_mut.route. Here it's more intelligent since the swap is effective only if the fitness function
        after swap is lower.
        This method allows us to have a good local search on solutions
        Runs k_mut_prob*100 % of the time
        '''
        tree = copy.deepcopy(tree_mut)
        tree.calc_fit()
        # k_mut_prob %
        breakk = False
        lenn = len(tree.prufer)
        
        if random.random() < self.k_mut_prob:
            list_indices = list(set(random.choices(list(range(lenn)), k = int(self.nodeNum/3))))
            allposs = []
            for i in list_indices:
                for j in range(lenn):
                    tmp_tree = GA.swap(tree,i,j)
                    tmp_tree.calc_fit()
                    allposs.append(tmp_tree)
                    if(tree.fitness > tmp_tree.fitness):
                        tree = tmp_tree
                        breakk = True
                        break
                if breakk:
                    breakk = False
                    break
            if not breakk:
                tree = sorted(allposs, key=lambda x: x.fitness, reverse=False)[0]
            tree.calc_fit()
        return tree


    def fittest_swap(self,tree_mut):
        '''
        Tree() --> Tree()

        Swaps two random indexes in route_to_mut.route. Here it's more intelligent since the swap is effective only if the fitness function
        after swap is lower.
        This method allows us to have a good local search on solutions
        This is Local Search at the end of each generation 
        Runs k_mut_prob*100 % of the time
        '''
        tree = copy.deepcopy(tree_mut)
        tree.calc_fit()
        lenn = len(tree.prufer)

        def toparall(i,j):
            tmp_tree = GA.swap(tree,i,j)
            tmp_tree.calc_fit()
            return tmp_tree
        
        if random.random() < self.k_mut_prob:
            for i in range(lenn):
                possibilities = Parallel(n_jobs=-1)(delayed(toparall)(i,j) for j in range(lenn))
                tmplist = sorted(possibilities, key=lambda x: x.fitness, reverse=False)
                tree = tmplist[0]
        return tree

    def mutate_2opt(self, tree_mut):
        '''
        Tree() --> Tree()

        Doing a 2opt swap. We're keeping the best swap among the possibles 2opt swap. The fitness can be lower than the original one
        This method allows us to have a good local search on solutions
        Runs k_mut_prob*100 % of the time
        '''
        tree = copy.deepcopy(tree_mut)
        tree.calc_fit()
        # k_mut_prob %

        lenn = len(tree.prufer)
        def parallel(i,j):
            tmp_tree = GA.swap_2opt(tree,i,j)
            tmp_tree.calc_fit()
            return tmp_tree

        if random.random() < self.k_mut_prob:
            list_indices = list(set(random.choices(list(range(lenn)), k = int(self.nodeNum/4))))
            allposs =[]

            for i in list_indices:
                possibilities = Parallel(n_jobs=-1)(delayed(parallel)(i,j) for j in range(lenn))
                tmplist = sorted(possibilities, key=lambda x: x.fitness, reverse=False)
                allposs.append(tmplist[0])
            
            tmplist = sorted(allposs, key=lambda x: x.fitness, reverse=False)
            tree = tmplist[0]
            tree.calc_fit()
        return tree

    def change_three_bests(self, population):
        """
        TreePop() --> TreePop()
        Change the first three best trees (in term of fitness). We're testing every swap possible.
        ### @TODO do it until there are 5 different trees
        """
        population.sort_treepop()

        #for k in range(3):
        #    population.tree_pop[k] = self.fittest_swap(population.tree_pop[k])
        cpt = 0
        k = 0
        lenn = len(population.tree_pop)
        done = []
        while(cpt< 5 and k< lenn):
            print(k)
            population.tree_pop[k] = self.fittest_swap(population.tree_pop[k])
            if(population.tree_pop[k] not in done):
                cpt+=1
                done.append(population.tree_pop[k])
            k+=1
        return population

    def evolve_population(self, init_pop):
        '''
        TreePop() --> TreePop()

        Takes a population and evolves it then returns the new population. 
        '''

        #makes a new population:
        descendant_pop = TreePop(list_files = self.list_files, size=init_pop.size, initialise=True)

        # Elitism offset (amount of Tree() carried over to new population)
        elitismOffset = 0

        # if we have elitism, set the first of the new population to the fittest of the old
        if self.elitism:
            descendant_pop.tree_pop[0] = init_pop.fittest
            elitismOffset = 1

        # Goes through the new population and fills it with the child of two tournament winners from the previous populatio
        for x in range(elitismOffset,descendant_pop.size):
            # two parents:
            tournament_parent1 = self.tournament_select(init_pop)[0]
            tournament_parent2 = self.tournament_select(init_pop)[0]

            while(tournament_parent2 == tournament_parent1):
                tournament_parent2 = self.tournament_select(init_pop)[0]

            # A child:
            tournament_child = self.crossover_kpoint(tournament_parent1, tournament_parent2)

            # Fill the population up with children
            descendant_pop.tree_pop[x] = tournament_child
        # Mutates all the Tree (mutation with happen with a prob p = k_mut_prob)
        # tre_ind in range(len(descendant_pop.tree_pop)):
        #    descendant_pop.tree_pop[tre_ind] = self.mutate_2opt_nerfed(descendant_pop.tree_pop[tre_ind])

        if(self.method == "swap"):
            func = self.mutate_swap_nerfed
        elif (self.method == "opt"):
            func = self.mutate_2opt

        tmp = Parallel(n_jobs=-1)(delayed(func)(descendant_pop.tree_pop[tre_ind]) for tre_ind in range(len(descendant_pop.tree_pop)))
        descendant_pop.tree_pop = tmp

        # Update the fittest Tree:
        #descendant_pop.sort_treepop()
        #descendant_pop.tree_pop[0] = self.fittest_2opt(descendant_pop.tree_pop[0])
        
        descendant_pop.get_fittest()
        

        return descendant_pop