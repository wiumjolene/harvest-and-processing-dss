# -*- coding: utf-8 -*-
import logging
import datetime
import os

import pandas as pd
from src.data.make_dataset import CreateOptions
from src.models.genetic_algorithm import GeneticAlgorithmMoga, GeneticAlgorithmVega
from src.models.genetic_algorithm import GeneticAlgorithmNsga2
from src.models.run_tests import RunTests

class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = False
    make_data = False

    vega = False
    nsga2 = False
    moga = False

    nsga2_zdt1 = True
    moga_zdt1 = False
    vega_zdt1 = False

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
            ga = GeneticAlgorithmMoga()

            if not os.path.exists('data/interim/moga'):
                os.makedirs('data/interim/moga')

            start=datetime.datetime.now()
            x=ga.moga()
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('moga', start, finish, (finish-start), x[0], x[1])],
                    columns=['model', 'start', 'finish', 'diff', 'best_obj1', 'best_obj2' ])

            monitor=pd.concat([monitor, temp])

        if self.nsga2_zdt1:
            self.logger.info('--- TEST: NSGA2 - ZDT1 ---')
            ga = RunTests()

            if not os.path.exists('data/interim/zdt1/nsga2'):
                os.makedirs('data/interim/zdt1/nsga2')

            start=datetime.datetime.now()
            x=ga.make_ga_test('nsga2', 'zdt1')
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('nsga1_zdt1', start, finish, (finish-start))],
                    columns=['model', 'start', 'finish', 'diff'])

            monitor=pd.concat([monitor, temp])

        if self.moga_zdt1:
            self.logger.info('--- TEST: MOGA - ZDT1 ---')
            ga = RunTests()

            if not os.path.exists('data/interim/zdt1/moga'):
                os.makedirs('data/interim/zdt1/moga')

            start=datetime.datetime.now()
            x=ga.make_ga_test('moga', 'zdt1')
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('moga_zdt1', start, finish, (finish-start))],
                    columns=['model', 'start', 'finish', 'diff'])

            monitor=pd.concat([monitor, temp])

        if self.vega_zdt1:
            self.logger.info('--- TEST: VEGA - ZDT1 ---')
            ga = RunTests()

            if not os.path.exists('data/interim/zdt1/vega'):
                os.makedirs('data/interim/zdt1/vega')

            start=datetime.datetime.now()
            x=ga.make_ga_test('vega', 'zdt1')
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[('vega_zdt1', start, finish, (finish-start))],
                    columns=['model', 'start', 'finish', 'diff'])

            monitor=pd.concat([monitor, temp])

        monitor.to_excel('data/interim/monitor.xlsx', index=False)