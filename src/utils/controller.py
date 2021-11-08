# -*- coding: utf-8 -*-
import logging
import datetime
import os

import pandas as pd
#import pygmo as pg

from src.data.make_dataset import CreateOptions
from src.models.genetic_algorithm import GeneticAlgorithmVega
from src.models.genetic_algorithm import GeneticAlgorithmMoga
from src.models.genetic_algorithm import GeneticAlgorithmNsga2
from src.models.run_tests import RunTests
from src.utils import config

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False

    vega = False
    nsga2 = True
    moga = False

    test_fxn = False
    tests = ['zdt1', 'zdt2', 'zdt3']
    tests = ['zdt1']

    def pipeline_control(self):
        monitor = pd.DataFrame()

        rt = RunTests()

        if self.synch_data:
            self.logger.info('SYNC DATA')

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.vega:
            self.logger.info('--- GENETIC ALGORITHM: VEGA ---')
            if self.test_fxn:
                for t in self.tests:
                    monitor = rt.run_tests('vega', t, monitor)

            else:
                ga = GeneticAlgorithmVega()

                if not os.path.exists('data/interim/vega'):
                    os.makedirs('data/interim/vega')

                start=datetime.datetime.now()
                x=ga.vega()
                finish=datetime.datetime.now()

                temp = pd.DataFrame(data=[('vega', start, finish, (finish-start), x[0], x[1])],
                        columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])

                monitor=pd.concat([monitor, temp])

        if self.nsga2:
            self.logger.info('--- GENETIC ALGORITHM: NSGA2 ---')

            if self.test_fxn:
                for t in self.tests:
                    monitor = rt.run_tests('nsga2', t, monitor)

            else:
                ga = GeneticAlgorithmNsga2()

                if not os.path.exists('data/interim/nsga2'):
                    os.makedirs('data/interim/nsga2')

                start=datetime.datetime.now()
                x=ga.nsga2()
                finish=datetime.datetime.now()

                temp = pd.DataFrame(data=[('nsga2', start, finish, (finish-start), x[0], x[1])],
                        columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])
                monitor=pd.concat([monitor, temp])

        if self.moga:
            self.logger.info('--- GENETIC ALGORITHM: MOGA ---')

            if self.test_fxn:
                for t in self.tests:
                    monitor = rt.run_tests('moga', t, monitor)

            else:
                ga = GeneticAlgorithmMoga()

                if not os.path.exists('data/interim/moga'):
                    os.makedirs('data/interim/moga')

                start=datetime.datetime.now()
                x=ga.moga()
                finish=datetime.datetime.now()

                temp = pd.DataFrame(data=[('moga', start, finish, (finish-start), x[0], x[1])],
                        columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])

                monitor=pd.concat([monitor, temp])

        monitor.to_excel('data/interim/monitor.xlsx', index=False)

