# -*- coding: utf-8 -*-


from __future__ import unicode_literals


__author__ = "Sergey Arkhipov <serge@aerialsounds.org>"
__version__ = 0, 2, 0


from .core import isitbullshit, raise_for_problem  # NOQA
from .exceptions import ItIsBullshitError  # NOQA
from .structures import WHATEVER, OrSkipped  # NOQA
from .testcase_mixin import IsItBullshitMixin  # NOQA


# silence for pyflakes
assert isitbullshit
assert raise_for_problem

assert ItIsBullshitError

assert WHATEVER
assert OrSkipped

assert IsItBullshitMixin
