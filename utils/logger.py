import logging

def setup_logging(log_level):
    """
    Sets up logging to console and database.
    """
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('Picard')
    return logger
