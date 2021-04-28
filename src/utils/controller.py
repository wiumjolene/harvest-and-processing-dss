# -*- coding: utf-8 -*-
import logging

from src.data.make_dataset import CreateOptions
from src.features.build_features import Population

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False
    build_feature = True
    tabu = False


    def pipeline_control(self):

        if self.synch_data:
            self.logger.info('SYNC DATA')

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.build_feature:
            self.logger.info('MAKE POPULATION')
            p = Population()
            x = p.population(10) #FIXME:
            x.to_excel('data/interim/fitness.xlsx') #FIXME: