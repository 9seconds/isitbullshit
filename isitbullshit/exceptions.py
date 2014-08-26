# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import contextlib

from six import text_type, moves, PY3


class ItIsBullshitError(ValueError):

    def __init__(self, line):
        super(ItIsBullshitError, self).__init__()

        self.line = text_type(line)

    def __iter__(self):
        cause = self
        while cause is not None:
            if isinstance(cause, ItIsBullshitError):
                yield cause.line
                cause = getattr(cause, "__cause__", None)
            else:
                yield text_type(cause)
                raise StopIteration

    def __unicode__(self):
        lines = list(self)
        if len(lines) == 1:
            return lines[0]

        with contextlib.closing(moves.cStringIO()) as buf:
            for indent_level, line in enumerate(lines):
                if indent_level == len(lines) - 1:
                    buf.write(" ")
                    buf.write(line)
                else:
                    buf.write("    " * indent_level)
                    buf.write(line)
                    buf.write(":")
                    if indent_level < len(lines) - 2:
                        buf.write("\n")
            return buf.getvalue()

    def __repr__(self):
        return repr(list(self))

    if PY3:
        def __str__(self):  # noqa
            return self.__unicode__()
    else:
        def __str__(self):  # noqa
            return self.__unicode__().encode("utf-8")
