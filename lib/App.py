import random
import copy
import os
import time
import math
import csv
import pandas as pd
import numpy as np
import argparse

from Tree import Tree
from TreePop import TreePop
from GA import GA
import copy
import logging

class App:
    """
    Runs the application
    """

    # Print iterations progress
    @staticmethod
    def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '#'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        logging.info('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        # Print New Line on Complete
        if iteration == total: 
            print()


    def maj(self,reset = False, tot = 0):
            if reset == True:
                    self.count =0
                    App.printProgressBar(self.count,tot,prefix=" Status progression")
                    self.count+=1
            else:
                    App.printProgressBar(self.count,tot,prefix=" Status progression")
                    self.count+=1

    def __init__(self,list_files, n_generations = 100 , pop_size = 100 , graph=False):
        self.list_files = list_files
        self.n_generations = n_generations
        self.pop_size = pop_size

        #Looping

        print("Calculating GA_loop")
        logging.info("Calculating GA_loop")
        self.ga_loop()
    
    def ga_loop(self):
        '''
        Main logic loop for the GA. Creates and manages populations, running variables etc.
        '''

        # takes the time to measure the elapsed time
        start_time = time.time()

        # Creates the population:
        print("Creates the population:")
        logging.info("Creates the population:")
        the_population = TreePop(self.pop_size, self.list_files, initialise= True)
        print ("Finished Creation of the population")
        logging.info("Finished Creation of the population")

        #Initial fitness
        initial_fitness = the_population.fittest.fitness

        # Creates a random Tree called best_tree. It will store our overall best tree.
        best_tree = Tree(self.list_files)

        # Main process loop (for number of generations)
        tot = self.n_generations
        self.maj(reset= True, tot = tot)

        fitness_over_gen = []

        for x in range(0,self.n_generations):
            start_time1 = time.time()
            # Evolves the population:
            the_population = GA(self.list_files).evolve_population(the_population)

            # If we have found a new shorter route, save it to best_route
            if the_population.fittest.fitness < best_tree.fitness:
                # set the route (copy.deepcopy because the_population.fittest is persistent in this loop so will cause reference bugs)
                best_tree = copy.deepcopy(the_population.fittest)
            self.maj(tot = tot)
            end_time1 = time.time()
            print("\nTime taken for one generation : {}s".format(end_time1-start_time1))
            print("Best Fitness : {}".format(best_tree.fitness))
            logging.info("\nTime taken for one generation : {}s".format(end_time1-start_time1))
            logging.info("Best Fitness : {}".format(best_tree.fitness))
            fitness_over_gen.append(best_tree.fitness)

        # takes the end time of the run:
        end_time = time.time()

        logging.info('Finished evolving {0} generations.'.format(self.n_generations))
        logging.info("Elapsed time was {0:.1f} seconds.".format(end_time - start_time))
        logging.info(' ')
        logging.info('Initial best fitness: {0:.2f}'.format(initial_fitness))
        logging.info('Final best fitness:   {0:.2f}'.format(best_tree.fitness))
        logging.info('Best fitness over generations {}'.format(fitness_over_gen))
        logging.info('The prufer sequence of the best Tree {}'.format(best_tree.prufer))

        
        print('Finished evolving {0} generations.'.format(self.n_generations))
        print("Elapsed time was {0:.1f} seconds.".format(end_time - start_time))
        print(' ')
        print('Initial best fitness: {0:.2f}'.format(initial_fitness))
        print('Final best fitness:   {0:.2f}'.format(best_tree.fitness))
        print('Best fitness over generations {}'.format(fitness_over_gen))
        print('The prufer sequence of the best Tree {}'.format(best_tree.prufer))
        return



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='MainApp')
    parser.add_argument('logname', metavar='l', nargs=1,
                        help='Name of the logfile')

    myparser = parser.parse_args()
    logname = myparser.logname[0]


    def read_excel_data(filename, sheet_name):
        data = pd.read_excel(filename, sheet_name=sheet_name, header=None)
        values = data.values
        return values
    logging.basicConfig(level=logging.DEBUG, filename=logname, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    
    mysheet = "../data/InputDataHubLargeInstance.xlsx"
    list_files = [read_excel_data(mysheet, "NodeNum"), read_excel_data(mysheet, "flow"), read_excel_data(mysheet, "varCost"),
                read_excel_data(mysheet, "fixCost"), read_excel_data(mysheet, "alpha"), read_excel_data(mysheet, "Cap")]
    flow = list_files[1]
    Origin = [0 for k in list(range(0,list_files[0][0][0]))]
    Destination = [0 for k in list(range(0,list_files[0][0][0]))]

    for i in range(0,list_files[0][0][0]):
        for j in range(0,list_files[0][0][0]):
            Origin[i] += flow[i,j]
            Destination[i] += flow[j,i]

    Origin = np.array(Origin)
    Destination = np.array(Destination)
    list_files.append(Origin)
    list_files.append(Destination)

    app = App(list_files)