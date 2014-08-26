# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import sys
import re

import pep3134

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
        cause = ValueError("Scheme mismatch {0}".format(scheme))
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)


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
        cause = ValueError("Type mismatch, should be a dict")
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)

    for key, validator in iteritems(scheme):
        original_validator = validator
        if isinstance(validator, OrSkipped):
            original_validator = validator.validator

        if key not in suspicious:
            if not isinstance(validator, OrSkipped):
                cause = ValueError("Missed key {0}".format(key))
                error = ItIsBullshitError(suspicious)
                pep3134.raise_from(error, cause)
        else:
            if suspicious[key] is not validator:
                try:
                    raise_for_problem(suspicious[key], original_validator)
                except ItIsBullshitError as err:
                    error = ItIsBullshitError(suspicious)
                    pep3134.raise_from(error, err)


def raise_for_list_problem(suspicious, scheme):
    if not scheme:
        raise TypeError("List scheme should contain at least 1 element")

    if len(scheme) != 1:
        raise TypeError("List scheme should contain only 1 element")

    if not isinstance(suspicious, (tuple, list)):
        cause = ValueError("Type mismatch, should be a list or a tuple")
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)

    for item in suspicious:
        try:
            raise_for_problem(item, scheme[0])
        except ItIsBullshitError as err:
            error = ItIsBullshitError(suspicious)
            pep3134.raise_from(error, err)


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
            final_error = ItIsBullshitError(suspicious)
            pep3134.raise_from(final_error, error)


def raise_for_string_problem(suspicious, scheme):
    if not isinstance(suspicious, string_types):
        cause = ValueError("Should be a string")
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)

    # noinspection PyTypeChecker
    if re.match(scheme, suspicious, re.UNICODE) is None:
        cause = ValueError("Regex mismatch: {0}".format(scheme))
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)


def raise_for_float_problem(suspicious, scheme):
    if not isinstance(suspicious, float):
        cause = ValueError("Should be a float")
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)

    if abs(suspicious - scheme) >= sys.float_info.epsilon:
        cause = ValueError("Should be {0}".format(scheme))
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, cause)


def raise_for_callable_problem(suspicious, validator):
    try:
        validator(suspicious)
    except Exception as err:
        error = ItIsBullshitError(suspicious)
        pep3134.raise_from(error, err)
