import logging
from pathlib import Path


def create_logger(logger_name: 'logger name (str)' = ""):
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger(logger_name + "_logger")
    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging.INFO)

    # create the logging file handler
    fp = logger_name + ".log"
    if Path.exists(Path.cwd() / "data"):
        fp = Path.cwd() / "data/log" / fp
    fh = logging.FileHandler(fp)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(f_format)
    ch.setFormatter(c_format)

    # add handler to logger object
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def exception(logger):
    """
    A decorator that wraps the passed in function and logs 
    exceptions should one occur
 
    @param logger: The logging object
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                # log the exception
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err)

            # re-raise the exception
            raise Exception("snap")

        return wrapper

    return decorator
