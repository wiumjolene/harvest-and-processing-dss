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

    vega = False
    nsga2 = True
    moga = False

    development=False
    test_fxn = False
    tests = ['zdt1', 'zdt2', 'zdt3']
    tests = ['zdt1']

    def pipeline_control(self):
        monitor = pd.DataFrame()
        if self.test_fxn:
            rt = RunTests()
            if self.vega:
                for t in self.tests:
                    monitor = rt.run_tests('vega', t, monitor)

            if self.nsga2:
                for t in self.tests:
                    monitor = rt.run_tests('nsga2', t, monitor)

            if self.moga:
                for t in self.tests:
                    monitor = rt.run_tests('moga', t, monitor)

        elif self.development:    
            manplan = PrepManPlan()
            plan_date = '2021-12-22'
            weeks_str = "'21-51','21-52','22-01','22-02','22-03','22-04'"
            #dss=self.run_dss(plan_date, weeks_str)
            #dss=self.run_dss(plan_date, weeks_str,adjust_planning_data=False)
            dss=self.run_dss(plan_date, weeks_str,
                    synch_data=True,
                    adjust_planning_data=True,
                    make_data=True,
                    clearold=False)
            manplan.prep_results(dss[0], dss[1], dss[2], plan_date, weeks_str)

        else:    
            self.manage_season_run()

    def manage_season_run(self):
        sr = ManageSeasonRun()
        manplan = PrepManPlan()

        while len(sr.get_plan_dates())>0:
            plan_date=sr.get_plan_dates()
            plan_date=plan_date.plan_date[0]

            season_setup=sr.get_season_run()
            weeks=list(season_setup.week)
       
            weeks_str=''
            for w in weeks:
                weeks_str=weeks_str+f"'{w}',"
            weeks_str=weeks_str[:-1]

            print(f"{plan_date}: {weeks_str}")
            dss=self.run_dss(plan_date, weeks_str)
            manplan.prep_results(dss[0], dss[1], dss[2], plan_date, weeks_str)

            sr.update_plan_complete(plan_date)
            
        return 

    def run_dss(self, plan_date, weeks_str,
                    synch_data=True,
                    adjust_planning_data=True,
                    make_data=True,
                    clearold=False):
        
        if synch_data:
            self.logger.info('SYNC DATA')
            pdp = PrepModelData()
            dp=pdp.prep_demand_plan(plan_date, weeks_str)
            he=pdp.prep_harvest_estimates(plan_date, weeks_str) 
            pc=pdp.prep_pack_capacity(plan_date, weeks_str) 

            if (dp and he and pc):
                self.logger.info('Data synch complete, good to proceed')

            else:
                self.logger.info('Data synch failed, review to proceed')
                exit()
        
        if adjust_planning_data:
            self.logger.info('ADJUST DATA')
            apd = AdjustPlanningData()
            apd.adjust_pack_capacities(weeks_str, plan_date)

        if make_data:
            self.logger.info('MAKE DATA')
            v = CreateOptions()
            v.make_options(plan_date)

        if clearold:
            self.logger.info('CLEAR OLD DATA')
            pp = PrepManPlan()
            pp.clear_old_result()

        if self.vega:
            self.logger.info('--- GENETIC ALGORITHM: VEGA ---')
            if not os.path.exists('data/interim/vega'):
                os.makedirs('data/interim/vega')
            
            ga = GeneticAlgorithmVega()
            plan = ga.vega()


        if self.nsga2:
            self.logger.info('--- GENETIC ALGORITHM: NSGA2 ---')
            if not os.path.exists('data/interim/nsga2'):
                os.makedirs('data/interim/nsga2')

            ga = GeneticAlgorithmNsga2()
            plan = ga.nsga2()


        if self.moga:
            self.logger.info('--- GENETIC ALGORITHM: MOGA ---')
            if not os.path.exists('data/interim/moga'):
                os.makedirs('data/interim/moga')

            ga = GeneticAlgorithmMoga()
            plan = ga.moga()

        return plan


