# -*- coding: utf-8 -*-


__version__ = 0, 1, 1


from .core import isitbullshit, raise_for_problem, WHATEVER  # NOQA
from .exceptions import ItIsBullshitError  # NOQA
from .testcase_mixin import IsItBullshitMixin  # NOQA


# silence for pyflakes
assert isitbullshit
assert raise_for_problem
assert WHATEVER
assert ItIsBullshitError
assert IsItBullshitMixin
