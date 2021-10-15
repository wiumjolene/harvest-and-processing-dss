import logging
from src.utils.controller import MainController


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s: %(message)s - %(name)s'
    #logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format=log_fmt)
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    mc = MainController()
    mc.pipeline_control()



"""
Updates
- Add non dominated sorting

TODO:
- dont save indiv - carry on in population.
- compare NSGA to DEAP


Thoughts

crossover and mutation not strong enough
use DEAP nsgaii in nsgaii to see why not getting over issues
"""