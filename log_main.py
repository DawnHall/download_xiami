import logging
LOG_FILENAME = 'logging.out'
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)
log = logging.getLogger('mainThread')