# -*- coding: utf-8 -*-


class ItIsBullshitError(ValueError):

    __slots__ = ("line", "cause")

    def __init__(self, line, cause):
        super(ItIsBullshitError, self).__init__()

        self.line = unicode(line) + ": "
        self.cause = cause

    def to_strings(self, indent=False):
        indentation = " " * 4 if indent else ""

        if isinstance(self.cause, ItIsBullshitError):
            yield indentation + self.line
            for level in self.cause.to_strings(True):
                yield indentation + level
        else:
            yield indentation + self.line + unicode(self.cause)

    def __repr__(self):
        return repr(list(elem.lstrip() for elem in self.to_strings()))

    def __unicode__(self):
        return u"\n".join(self.to_strings())

    def __str__(self):
        return self.__unicode__().encode("utf-8")
