# -*- coding: utf-8 -*-
import logging
import datetime

import pandas as pd
from src.data.make_dataset import CreateOptions
from src.models.genetic_algorithm import GeneticAlgorithmMoga, GeneticAlgorithmVega
from src.models.genetic_algorithm import GeneticAlgorithmNsga2

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False

    vega = True
    nsga2 = True
    moga = True

    def pipeline_control(self):
        monitor = pd.DataFrame()

        if self.synch_data:
            self.logger.info('SYNC DATA')

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.vega:
            self.logger.info('--- GENETIC ALGORITHM: VEGA ---')
            ga = GeneticAlgorithmVega()

            start=datetime.datetime.now()
            x=ga.vega()
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('vega', start, finish, (finish-start), x[0], x[1])],
                    columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])

            monitor=pd.concat([monitor, temp])

        if self.nsga2:
            self.logger.info('--- GENETIC ALGORITHM: NSGA2 ---')
            ga = GeneticAlgorithmNsga2()

            start=datetime.datetime.now()
            x=ga.nsga2()
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('nsga2', start, finish, (finish-start), x[0], x[1])],
                    columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])
            monitor=pd.concat([monitor, temp])

        if self.moga:
            self.logger.info('--- GENETIC ALGORITHM: MOGA ---')
            ga = GeneticAlgorithmMoga()

            start=datetime.datetime.now()
            x=ga.moga()
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('moga', start, finish, (finish-start), x[0], x[1])],
                    columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])

            monitor=pd.concat([monitor, temp])

        monitor.to_excel('data/interim/monitor.xlsx', index=False)