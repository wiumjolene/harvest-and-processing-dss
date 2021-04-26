# -*- coding: utf-8 -*-
import logging
import pickle

from src.utils import config

class Individual:
    """ Class to generate an individual solution. """
    logger = logging.getLogger(f"{__name__}.Individual")    