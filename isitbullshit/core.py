# -*- coding: utf-8 -*-


import sys
import re

from six import u, iteritems, string_types, callable as compat_callable

from .exceptions import ItIsBullshitError


WHATEVER = object()


def isitbullshit(element, scheme):
    try:
        raise_for_problem(element, scheme)
    except ItIsBullshitError:
        return True
    return False


def raise_for_problem(element, scheme):  # pylint: disable=R0912
    if element == scheme or element is scheme or scheme is WHATEVER:
        return

    if isinstance(scheme, dict):
        if not scheme:
            raise ValueError(
                u("Dict scheme should contain at least 1 element")
            )
        if not isinstance(element, dict):
            raise ItIsBullshitError(element,
                                    u("Type mismatch, should be a dict"))
        for key, validator in iteritems(scheme):
            if key not in element:
                raise ItIsBullshitError(element,
                                        u("Missed key {0}").format(key))
            raise_for_problem(element[key], validator)

    elif isinstance(scheme, list):
        if not scheme:
            raise ValueError(
                u("List scheme should contain at least 1 element")
            )
        if len(scheme) != 1:
            raise ValueError(u("List scheme should contain only 1 element"))
        if not isinstance(element, (tuple, list)):
            raise ItIsBullshitError(element,
                                    u("Type mismatch, should be a "
                                      "list or a tuple"))
        for item in element:
            raise_for_problem(item, scheme[0])

    elif isinstance(scheme, tuple):
        if not scheme:
            raise ValueError(
                u("Tuple scheme should contain at least 1 element")
            )
        error = None
        for type_validator in scheme:
            try:
                raise_for_problem(element, type_validator)
                break
            except ItIsBullshitError as err:
                error = err
        else:
            if error is not None:
                raise ItIsBullshitError(element, error)

    elif isinstance(scheme, string_types):
        if not isinstance(element, string_types):
            raise ItIsBullshitError(element, u("Should be a string"))
        # noinspection PyTypeChecker
        if re.match(scheme, element, re.UNICODE) is None:
            raise ItIsBullshitError(element,
                                    u("Regex mismatch: {0}").format(scheme))

    elif isinstance(scheme, float):
        if not isinstance(element, float):
            raise ItIsBullshitError(element, u("Should be a float"))
        if abs(element - scheme) >= sys.float_info.epsilon:
            raise ItIsBullshitError(element,
                                    u("Should be {0}").format(scheme))

    elif compat_callable(scheme):
        try:
            scheme(element)
        except Exception as err:
            raise ItIsBullshitError(element, err)

    else:
        raise ItIsBullshitError(element,
                                u("Scheme mismatch {0}").format(scheme))
