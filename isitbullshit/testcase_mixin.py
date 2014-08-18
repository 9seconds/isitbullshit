# -*- coding: utf-8 -*-


from .core import raise_for_problem, isitbullshit
from .exceptions import ItIsBullshitError


class IsItBullshitMixin(object):

    @staticmethod
    def assertBullshit(data, scheme, reason=None):
        if not isitbullshit(data, scheme):
            raise AssertionError(reason)

    @staticmethod
    def assertNotBullshit(data, scheme, reason=None):
        try:
            raise_for_problem(data, scheme)
        except ItIsBullshitError as err:
            if reason is None:
                reason = unicode(err)
            raise AssertionError(reason)
