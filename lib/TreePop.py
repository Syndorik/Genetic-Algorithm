import random
import copy
import os
import time
import math
import csv

from Tree import Tree
import copy

class TreePop(object):
    """
    Contains a list of Tree objects and provides info on them.

    self.tree_pop: list of Tree objects
    self.size: lenth of tree_pop - specified upon __init__
    self.fittest: Tree() object with shortest length from self.tree_pop

    self.get_fittest(): Calcualtes fittest Tree, sets self.fittest to it, and returns the Tree. Use if Tree have changed manually.
    """
    def __init__(self, size, list_files, initialise = False):
        self.tree_pop = []
        self.size = size
        # If we want to initialise a population.rt_pop:
        if initialise:
            for x in range(0,size):
                new_tree = Tree(list_files)
                new_tree.calc_fit()
                self.tree_pop.append(new_tree)
            self.get_fittest()

    def get_fittest(self):
        '''
        self --> Tree()

        Returns the best Graph with the minimum fitness funciton
        '''
        # sorts the list based on graph's fintess
        sorted_list = sorted(self.tree_pop, key=lambda x: x.fitness, reverse=False)
        self.fittest = sorted_list[0]
        return self.fittest
    
    def sort_treepop(self):
        sorted_list = sorted(self.tree_pop, key=lambda x: x.fitness, reverse=False)
        self.tree_pop = sorted_list