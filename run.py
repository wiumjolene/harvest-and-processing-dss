import logging
from src.utils.controller import MainController


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s: %(message)s - %(name)s'
    #logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG, format=log_fmt)
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    mc = MainController()
    mc.pipeline_control()



"""
See how indiv was created
"""