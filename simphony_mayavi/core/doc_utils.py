import inspect


def mergedoc(function, other):
    """ Merge the docstring from the other function to the decorated function.

    """
    if other.__doc__ is None:
        return function
    elif function.__doc__ is None:
        function.__func__.__doc__ = other.__doc__
        return function
    else:
        merged_doc = '\n'.join((other.__doc__, function.__doc__))
        function.__func__.__doc__ = merged_doc
        return function


class mergedocs(object):
    """ Merge the docstrings of other class to the decorated.

    """
    def __init__(self, other):
        self.other = other

    def __call__(self, cls):
        for name, old in inspect.getmembers(self.other):
            if inspect.ismethod(old):
                new = getattr(cls, name, None)
                if new is not None:
                    mergedoc(new, old)
        return cls
