import logging
import os
from src.utils.controller_test import MainController
from src.utils import config


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s: %(message)s - %(name)s'
    log_save = os.path.join(config.ROOTDIR,'log.log')
    logging.basicConfig(filename=log_save, filemode='w', level=logging.DEBUG, format=log_fmt)
    #logging.basicConfig(filename=log_save, filemode='w', level=logging.INFO, format=log_fmt)
    #logging.basicConfig(level=logging.INFO, format=log_fmt)

    mc = MainController()
    mc.pipeline_control()



"""
Containerisation
"""