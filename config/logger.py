import logging

LOGGER_NAME = 'wslbot'

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

fh = logging.FileHandler(f'{LOGGER_NAME}.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d-%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
