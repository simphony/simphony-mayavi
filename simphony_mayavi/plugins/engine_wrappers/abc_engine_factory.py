from abc import abstractmethod

from traits.api import ABCHasStrictTraits


class ABCEngineFactory(ABCHasStrictTraits):

    @abstractmethod
    def create(self):
        ''' Return a new engine wrapper instance '''
