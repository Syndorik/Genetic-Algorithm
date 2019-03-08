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

    def __init__(self,list_files, n_generations = 100 , pop_size = 100, k_mut_prob = 0.4, k_crossover = 3, tournament_size=7, elitism =True, method = "swap"):
        self.list_files = list_files
        self.n_generations = n_generations
        self.pop_size = pop_size
        self.k_mut_prob = k_mut_prob
        self.k_crossover = k_crossover
        self.tournament_size = tournament_size
        self.elitism = elitism
        self.method = method

        #Looping

        print("Calculating GA_loop")
        logging.info("Calculating GA_loop")
        self.final_fitness = self.ga_loop()
    
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

            the_population = GA(self.list_files,
                                k_mut_prob= self.k_mut_prob,
                                k_crossover= self.k_crossover,
                                tournament_size= self.tournament_size,
                                elitism= self.elitism,
                                method = self.method).evolve_population(the_population)

            #If fitness stays the same we try to local search a better solution and see how it goes. We're modifying the first
            #three bests.
            if(fitness_over_gen.count(best_tree.fitness)==3):
                the_population =GA(self.list_files,
                                    k_mut_prob= self.k_mut_prob,
                                    k_crossover= self.k_crossover,
                                    tournament_size= self.tournament_size,
                                    elitism= self.elitism,
                                    method= self.method).change_three_bests(the_population)
            
            # If we have found a new shorter route, save it to best_route
            if the_population.fittest.fitness < best_tree.fitness:
                # set the route (copy.deepcopy because the_population.fittest is persistent in this loop so will cause reference bugs)
                best_tree = copy.deepcopy(the_population.fittest)

            #Termination criteria : 8 times the same fitness

            if(fitness_over_gen.count(best_tree.fitness)>7 and x>30):
                old_tree = copy.deepcopy(best_tree)
                the_population =GA(self.list_files,
                                    k_mut_prob= self.k_mut_prob,
                                    k_crossover= self.k_crossover,
                                    tournament_size= self.tournament_size,
                                    elitism= self.elitism,
                                    method= self.method).change_three_bests(the_population)
                best_tree = copy.deepcopy(the_population.fittest)

                if(old_tree.fitness == best_tree.fitness):
                    print("Termination Criteria reached : No improvement for 8 generations")
                    logging.info("Termination Criteria reached : No improvement for 8 generations")
                    break


            self.maj(tot = tot)
            end_time1 = time.time()
            print("\nTime taken for one generation : {}s".format(end_time1-start_time1))
            print("Best Fitness : {}".format(best_tree.fitness))
            logging.info("\nTime taken for one generation : {}s".format(end_time1-start_time1))
            logging.info("Best Fitness : {}".format(best_tree.fitness))
            
            fitness_over_gen.append(best_tree.fitness)
        
        best_tree =GA(self.list_files,
                            k_mut_prob= self.k_mut_prob,
                            k_crossover= self.k_crossover,
                            tournament_size= self.tournament_size,
                            elitism= self.elitism,
                            method= self.method).fittest_swap(best_tree)


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

        return best_tree.fitness



if __name__ == '__main__':

    NGENERATION_DEF = 100
    NPOPULATION_DEF = 100
    KMUTPROB = 0.4
    KCROSSOVER = 3
    TOURNAMENTSIZE=7
    ELITISM =True
    METHOD = "swap"


    #Parser arguments

    #k_mut_prob = 0.4, k_crossover = 3, tournament_size=7, elitism =True

    parser = argparse.ArgumentParser(description='MainApp')
    parser.add_argument('-l','-log', nargs=1, metavar = "",
                        help='Name of the logfile')

    parser.add_argument('-ng','-num_of_generation',metavar = "", nargs=1,
                        help='Number of generation')
    
    parser.add_argument('-np','-num_of_pop',metavar = "", nargs=1,
                        help='Number of population')
    
    parser.add_argument('-m','-mutation_probabilitie',metavar = "", nargs=1,
                        help='Mutation probabilitie')

    parser.add_argument('-c','-crossover',metavar = "", nargs=1,
                        help='Division for crossover')
    
    parser.add_argument('-t','-tournament_size',metavar = "", nargs=1,
                        help='Tournament size')
    
    parser.add_argument('-me','-method',metavar = "", nargs=1,
                        help='method for mutation')

    parser.add_argument('--e','--elitism',action="store_true",
                        help='If this flag is raised, there will be no elitism in the GA')

    parser.add_argument('--s','--small',action="store_true",
                        help='Take the large or small instance, if option -s, then the small instance is taken')


    myparser = parser.parse_args()

    if(myparser.e):
        elitism = False
    else:
        elitism = ELITISM
    
    if(myparser.m != None):
        k_mut_prob = float(myparser.m[0])
    else:
        k_mut_prob = KMUTPROB
    
    if(myparser.c != None):
        k_crossover = int(myparser.c[0])
    else:
        k_crossover = KCROSSOVER
    
    if(myparser.t != None):
        tournament_size =  int(myparser.t[0])
    else:
        tournament_size = TOURNAMENTSIZE

    if(myparser.l != None):
        logname = "./log/{}".format(myparser.l[0])
    else:
        logname = "./log/def_log"
    
    if(myparser.ng != None):
        n_generations = int(myparser.ng[0])
    else:
        n_generations = NGENERATION_DEF
    
    if(myparser.np != None):
        n_population = int(myparser.np[0])
    else:
        n_population = NPOPULATION_DEF
    
    if(myparser.s):
        mysheet = "../data/InputDataHubSmallInstance.xlsx"
    else:
        mysheet = "../data/InputDataHubLargeInstance.xlsx"
    
    if(myparser.me != None):
        method = myparser.me[0]
    else:
        method = METHOD


    print("The following arguments were chosen :")
    print("Number of generation : {}".format(n_generations))
    print("Size of the population :  {}".format(n_population))
    print("Log file will be located at : {}".format(logname))
    print("The input data taken is : {}".format(mysheet))
    print("The mutation probability : {}".format(k_mut_prob))
    print("The number of point for crossover : {}".format(k_crossover))
    print("The size for tournament : {}".format(tournament_size))
    print("The elitism : {}".format(elitism))
    print("The mutation method chosen {}".format(method))
    print("##################")


    

    def read_excel_data(filename, sheet_name):
        data = pd.read_excel(filename, sheet_name=sheet_name, header=None)
        values = data.values
        return values
    logging.basicConfig(level=logging.DEBUG, filename=logname, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    
    
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

    app = App(list_files,
                n_generations = n_generations ,
                pop_size = n_population,
                k_mut_prob= k_mut_prob,
                k_crossover= k_crossover,
                tournament_size= tournament_size,
                elitism=elitism,
                method= method )
    logging.shutdown()
    os.rename(logname, logname[:6]+"Fitness={}_".format(round(app.final_fitness/(10**8),1)) + logname[6:]) 
    sys.exit(logname[:6]+"Fitness={}_".format(round(app.final_fitness/(10**8),1)) + logname[6:])