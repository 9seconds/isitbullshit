# -*- coding: utf-8 -*-


WHATEVER = Ellipsis


class OrSkipped(object):  # pylint: disable=R0903
    __slots__ = ("_func",)

    def __init__(self, func):
        self._func = func

    @property
    def validator(self):
        return self._func
