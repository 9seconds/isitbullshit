# -*- coding: utf-8 -*-


import sys
import re

from .exceptions import ItIsBullshitError


def isitbullshit(element, scheme):
    try:
        raise_for_problem(element, scheme)
    except ItIsBullshitError:
        return False
    else:
        return True


def raise_for_problem(element, scheme):
    if callable(scheme):
        try:
            scheme(element)
        except Exception as err:
            raise ItIsBullshitError(element, err)

    elif isinstance(scheme, tuple):
        error = None
        for type_validator in scheme:
            try:
                raise_for_problem(element, type_validator)
            except ItIsBullshitError as err:
                error = err
        if error is not None:
            raise ItIsBullshitError(element, error)

    elif isinstance(scheme, list):
        if not isinstance(element, (tuple, list)):
            raise ItIsBullshitError(element, "Type mismatch, should be list or tuple")
        if scheme:
            for item in element:
                raise_for_problem(item, scheme[0])

    elif isinstance(scheme, dict):
        if not isinstance(element, dict):
            raise ItIsBullshitError(element, "Type mismatch, should be a dict")
        for key, validator in scheme.iteritems():
            if key not in element:
                raise ItIsBullshitError(element, "Missed key {0}".format(key))
            raise_for_problem(element[key], validator)

    elif isinstance(scheme, basestring):
        if not isinstance(element, basestring):
            raise ItIsBullshitError(element, "Should be a string")
        if re.match(scheme, element, re.UNICODE) is None:
            raise ItIsBullshitError(element, "Regex mismatch: {}".format(scheme))

    elif isinstance(scheme, float):
        if not isinstance(element, float):
            raise ItIsBullshitError(element, "Should be a float")
        if abs(element - scheme) < sys.float_info.epsilon:
            raise ItIsBullshitError(element, "Should be {0}".format(scheme))

    elif element != scheme or element is not scheme:
        raise ItIsBullshitError(element, "Not equal to {}".format(scheme))
