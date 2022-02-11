# -*- coding: utf-8 -*-
import datetime
import logging
import os

import pandas as pd
from src.data.make_dataset import (AdjustPlanningData, 
                                    CreateOptions,
                                    ManageSeasonRun)
from src.features.build_features import PrepManPlan, PrepModelData
from src.models.genetic_algorithm import (GeneticAlgorithmMoga,
                                          GeneticAlgorithmNsga2,
                                          GeneticAlgorithmVega)
from src.models.run_tests import RunTests


class MainController:
    """ Decide which parts of the module to update. """
    logger = logging.getLogger(f"{__name__}.MainController")
    synch_data = True
    adjust_planning_data = True
    make_data = True

    clearold=False
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
            pdp = PrepModelData()
            dp=pdp.prep_demand_plan()
            he=pdp.prep_harvest_estimates()
            pc=pdp.prep_pack_capacity()

            if (dp and he and pc):
                self.logger.info('Data synch complete, good to proceed')

            else:
                self.logger.info('Data synch failed, review to proceed')
                exit()

        if self.adjust_planning_data:
            self.logger.info('ADJUST DATA')
            apd = AdjustPlanningData()
            apd.adjust_pack_capacities()

        if self.make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options()

        if self.clearold:
            self.logger.info('CLEAR OLD DATA')
            pp = PrepManPlan()
            pp.clear_old_result()

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

    def manage_season_run(self):
        sr = ManageSeasonRun()
        season_setup=sr.get_seasonrun()
        plan_date=season_setup[season_setup['make_plan']==1].reset_index(drop=True)
        plan_date=plan_date.plan_date[0]

        weeks=list(season_setup.week)
        weeks=['20-01','20-02']
        
        week_str=''
        for w in weeks:
            week_str=week_str+f"'{w}',"
        
        week_str=week_str[:-1]

        return [plan_date, week_str]
