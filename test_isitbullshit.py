#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest

from isitbullshit import isitbullshit, raise_for_problem, IsItBullshitMixin, \
    ItIsBullshitError


@pytest.mark.parametrize("input_", (
    int, float, dict, list, tuple, str, unicode, set, frozenset,
    1, 1.0, {}, [], tuple(), "hello", u"hello", "",
    [1, 2], {3: 4}, (5, 6), {"hello": 1}, {"1": 1},
    True, False, None
))
def test_self_notbullshit(input_):
    assert not isitbullshit(input_, input_)

    IsItBullshitMixin.assertNotBullshit(input_, input_)
    with pytest.raises(AssertionError):
        IsItBullshitMixin.assertBullshit(input_, input_)
    raise_for_problem(input_, input_)


@pytest.mark.parametrize("value_, type_", (
    (1, int),
    (1.0, float),
    ({}, dict),
    (tuple(), tuple),
    ([1, 2], list),
    ("", str),
    (u"", unicode),
    (None, None)
))
def test_simple_types_notbullshit(value_, type_):
    assert not isitbullshit(value_, type_)

    IsItBullshitMixin.assertNotBullshit(value_, type_)
    with pytest.raises(AssertionError):
        IsItBullshitMixin.assertBullshit(value_, type_)
    raise_for_problem(value_, type_)

@pytest.mark.parametrize("input_", (
    int, float, str, unicode, list, dict, tuple, set, frozenset
))
def test_value_bullshit(input_):
    from pdb import set_trace; set_trace()
    types = set((int, float, str, unicode, list, dict, tuple, set, frozenset))
    types -= set([input_])

    for type_ in types:
        assert isitbullshit(input_(), type_)
        assert isitbullshit(type_(), input_)
        assert isitbullshit(type_(), input_())
