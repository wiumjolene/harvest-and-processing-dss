# -*- coding: utf-8 -*-
import logging

from src.data.make_dataset import CreateOptions
from src.models.genetic_algorithm import GeneticAlgorithmVega
from src.models.genetic_algorithm import GeneticAlgorithmNsga2

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False
    vega = False
    nsga2 = True


    def pipeline_control(self):

        if self.synch_data:
            self.logger.info('SYNC DATA')

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.vega:
            self.logger.info('--- GENETIC ALGORITHM: VEGA ---')
            ga = GeneticAlgorithmVega()
            ga.vega()

        if self.nsga2:
            self.logger.info('--- GENETIC ALGORITHM: NSGA2 ---')
            ga = GeneticAlgorithmNsga2()
            ga.nsga2()