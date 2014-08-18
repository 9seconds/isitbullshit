# -*- coding: utf-8 -*-


from six import text_type

from .core import raise_for_problem, isitbullshit
from .exceptions import ItIsBullshitError


# noinspection PyPep8Naming
class IsItBullshitMixin(object):

    @staticmethod
    def assertBullshit(data, scheme, reason=None):  # noqa pylint: disable=C0103
        if not isitbullshit(data, scheme):
            raise AssertionError(text_type(reason))

    @staticmethod
    def assertNotBullshit(data, scheme, reason=None):  # noqa pylint: disable=C0103
        try:
            raise_for_problem(data, scheme)
        except ItIsBullshitError as err:
            if reason is None:
                reason = err
            raise AssertionError(text_type(reason))
