from functools import wraps, partial
import inspect
import logging
from pathlib import Path

import pandas as pd

class put_one_in_string(object):
    def __init__(self, kw):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.kw = kw

    def __call__(self, fnc):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        def wrapper_0(*args, **kwargs):
            fnc_args = inspect.getcallargs(fnc, *args, **kwargs)
            kw = fnc_args.get(self.kw)
            assert(kw)

            if type(kw) is str:
                print ("see")
                kwargs[self.kw] = [kw]
                return fnc(*args, **kwargs)
            return fnc(*args, **kwargs)

        return wrapper_0

def _validate_timeinput(fnc):
    """
    check functions that take time range arguments.
    If the input is open ended, convert it into pd.Timestamp object
    Otherwise, t0 must be ealier then t1, and convert both into Timestamp
    """
    @wraps(fnc)
    def wrapper(*args, **kwargs):
        fnc_args = inspect.getcallargs(fnc, *args, **kwargs)
        start = fnc_args.get('start')
        end = fnc_args.get('end')
        assert(start)

        ts0 = start
        ts1 = end

        copy_args = list(args)
        if start and end:
            assert(type(start) == type(end))
            assert((type(start) is str) or type(start) is pd.Timestamp)
            if type(start) is str:
                ts0 = pd.Timestamp(start)
                ts1 = pd.Timestamp(end)
            assert( ts0 < ts1 )
        else:
            if type(start) is str:
                ts0 = pd.Timestamp(start)
        
        idx = 0
        for each in inspect.getfullargspec(fnc)[0]:

            if each == 'start':
                copy_args[idx] = ts0
            elif each == 'end':
                copy_args[idx] = ts1
            idx += 1

        return fnc(*tuple(copy_args), **kwargs)

    return wrapper


def create_logger(logger_name:'logger name (str)'=""):
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger(logger_name+"_logger")
    if len(logger.handlers) > 0:
        return logger
    
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fp = logger_name+".log"
    if Path.exists(Path.cwd()/"data"):
        fp = Path.cwd()/"data/log"/fp
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
            raise
        return wrapper
    return decorator