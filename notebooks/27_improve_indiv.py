import os
import random
import sys
import logging

import pandas as pd
import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.features.build_features import Individual
from src.utils import config


log_fmt = '%(asctime)s ; %(levelname)s: %(message)s ; %(name)s'
log_save = os.path.join(config.ROOTDIR,'log.log')
logging.basicConfig(filename=log_save, filemode='w', level=logging.DEBUG, format=log_fmt)
#logging.basicConfig(filename=log_save, filemode='w', level=logging.INFO, format=log_fmt)
#logging.basicConfig(level=logging.DEBUG, format=log_fmt)

ind = Individual()

individual = ind.make_individual()