# -*- coding: utf-8 -*-


from __future__ import unicode_literals


from six import text_type, PY3


class ItIsBullshitError(ValueError):

    def __init__(self, line, cause):
        super(ItIsBullshitError, self).__init__()

        self.line = text_type(line) + ": "
        self.cause = cause

    def to_strings(self, indent=False):
        indentation = " " * 4 if indent else ""

        if isinstance(self.cause, ItIsBullshitError):
            yield indentation + self.line
            for level in self.cause.to_strings(True):
                yield indentation + level
        else:
            yield indentation + self.line + text_type(self.cause)

    def __repr__(self):
        # noinspection PyUnresolvedReferences
        return repr(list(elem.lstrip() for elem in self.to_strings()))

    # noinspection PyTypeChecker
    def __unicode__(self):
        return "\n".join(self.to_strings())

    if PY3:
        def __str__(self):  # noqa
            return self.__unicode__()
    else:
        def __str__(self):  # noqa
            return self.__unicode__().encode("utf-8")
