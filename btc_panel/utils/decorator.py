import inspect
from functools import wraps

import pandas as pd


class listify(object):
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
            assert (kw)

            if type(kw) is not list:
                print("see")
                kwargs[self.kw] = [kw]
                return fnc(*args, **kwargs)
            return fnc(*args, **kwargs)

        return wrapper_0


def time_enforce(fnc):
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
        assert (start)

        ts0 = start
        ts1 = end

        copy_args = list(args)
        if start and end:
            assert (type(start) == type(end))
            assert ((type(start) is str) or type(start) is pd.Timestamp)
            if type(start) is str:
                ts0 = pd.Timestamp(start)
                ts1 = pd.Timestamp(end)
            assert (ts0 < ts1)
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
