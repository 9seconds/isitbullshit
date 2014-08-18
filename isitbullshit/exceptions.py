# -*- coding: utf-8 -*-


from six import u, text_type, PY3


class ItIsBullshitError(ValueError):

    __slots__ = ("line", "cause")

    def __init__(self, line, cause):
        super(ItIsBullshitError, self).__init__()

        self.line = text_type(line) + u(": ")
        self.cause = cause

    def to_strings(self, indent=False):
        indentation = u(" ") * 4 if indent else u("")

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
        return u("\n").join(self.to_strings())

    if PY3:
        def __str__(self):  # noqa
            return self.__unicode__()
    else:
        def __str__(self):  # noqa
            return self.__unicode__().encode("utf-8")
