# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import sys
import re

from six import iteritems, string_types

from .exceptions import ItIsBullshitError
from .structures import WHATEVER, OrSkipped, FUNC_TYPE


def isitbullshit(suspicious, scheme):
    try:
        raise_for_problem(suspicious, scheme)
    except ItIsBullshitError:
        return True
    return False


def raise_for_problem(suspicious, scheme):
    if isinstance(scheme, OrSkipped):
        raise TypeError("Scheme could not be OrSkipped here")

    if shallow_check(suspicious, scheme):
        return

    if isinstance(scheme, dict):
        raise_for_dict_problem(suspicious, scheme)
    elif isinstance(scheme, list):
        raise_for_list_problem(suspicious, scheme)
    elif isinstance(scheme, tuple):
        raise_for_tuple_problem(suspicious, scheme)
    elif isinstance(scheme, string_types):
        raise_for_string_problem(suspicious, scheme)
    elif isinstance(scheme, float):
        raise_for_float_problem(suspicious, scheme)
    elif isinstance(scheme, FUNC_TYPE):
        raise_for_callable_problem(suspicious, scheme)
    else:
        raise ItIsBullshitError(suspicious,
                                "Scheme mismatch {0}".format(scheme))


def shallow_check(suspicious, scheme):
    if suspicious == scheme or suspicious is scheme or scheme is WHATEVER:
        return True

    for func in (isinstance, issubclass):
        try:
            if func(suspicious, scheme):
                return True
        except TypeError:
            continue

    return False


def raise_for_dict_problem(suspicious, scheme):
    if not scheme:
        raise TypeError("Dict scheme should contain at least 1 element")

    if not isinstance(suspicious, dict):
        raise ItIsBullshitError(suspicious, "Type mismatch, should be a dict")

    for key, validator in iteritems(scheme):
        original_validator = validator
        if isinstance(validator, OrSkipped):
            original_validator = validator.validator
        if key not in suspicious:
            if not isinstance(validator, OrSkipped):
                raise ItIsBullshitError(suspicious,
                                        "Missed key {0}".format(key))
        else:
            if suspicious[key] is not validator:
                try:
                    raise_for_problem(suspicious[key], original_validator)
                except ItIsBullshitError as err:
                    raise ItIsBullshitError(suspicious, err)


def raise_for_list_problem(suspicious, scheme):
    if not scheme:
        raise TypeError("List scheme should contain at least 1 element")

    if len(scheme) != 1:
        raise TypeError("List scheme should contain only 1 element")

    if not isinstance(suspicious, (tuple, list)):
        raise ItIsBullshitError(suspicious,
                                "Type mismatch, should be a list or a tuple")
    for item in suspicious:
        try:
            raise_for_problem(item, scheme[0])
        except ItIsBullshitError as err:
            raise ItIsBullshitError(suspicious, err)


def raise_for_tuple_problem(suspicious, scheme):
    if not scheme:
        raise TypeError("Tuple scheme should contain at least 1 element")

    error = None
    for type_validator in scheme:
        try:
            raise_for_problem(suspicious, type_validator)
            break
        except ItIsBullshitError as err:
            error = err
    else:
        if error is not None:
            raise ItIsBullshitError(suspicious, error)


def raise_for_string_problem(suspicious, scheme):
    if not isinstance(suspicious, string_types):
        raise ItIsBullshitError(suspicious, "Should be a string")

    # noinspection PyTypeChecker
    if re.match(scheme, suspicious, re.UNICODE) is None:
        raise ItIsBullshitError(suspicious,
                                "Regex mismatch: {0}".format(scheme))


def raise_for_float_problem(suspicious, scheme):
    if not isinstance(suspicious, float):
        raise ItIsBullshitError(suspicious, "Should be a float")

    if abs(suspicious - scheme) >= sys.float_info.epsilon:
        raise ItIsBullshitError(suspicious, "Should be {0}".format(scheme))


def raise_for_callable_problem(suspicious, validator):
    try:
        validator(suspicious)
    except Exception as err:
        raise ItIsBullshitError(suspicious, err)
