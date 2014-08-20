# -*- coding: utf-8 -*-


WHATEVER = Ellipsis
FUNC_TYPE = type(lambda: 1)


class OrSkipped(object):  # pylint: disable=R0903
    __slots__ = ("_scheme",)

    def __init__(self, func):
        self._scheme = func

    @property
    def validator(self):
        return self._scheme
