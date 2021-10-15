import logging
log = logging.getLogger()

# Set a severity threshold to one above WARN
log.setLevel(logging.ERROR)

# This WARNING will not reach the Humans.
log.warn('Citizens of Earth, be warned!')

# This CRITICAL message, however, will not be ignored.
log.critical('Citizens of Earth, your planet will be removed NOW!')

## Citizens of Earth, your planet will be removed NOW!