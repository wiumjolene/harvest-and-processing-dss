# -*- coding: utf-8 -*-
import logging

from src.data.make_dataset import CreateOptions
from src.models.genetic_algorithm import GeneticAlgorithm

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False
    vega = True
    ga = False
    tabu = False


    def pipeline_control(self):

        if self.synch_data:
            self.logger.info('SYNC DATA')

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.vega:
            self.logger.info('--- GENETIC ALGORITHM ---')
            ga = GeneticAlgorithm()
            ga.vega()
