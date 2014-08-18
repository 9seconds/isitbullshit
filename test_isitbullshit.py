#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest

from isitbullshit import isitbullshit, raise_for_problem, IsItBullshitMixin


@pytest.mark.parametrize("input_", (
    int, float, dict, list, tuple, str, unicode,
    1, 1.0, {}, [], tuple(), "hello", u"hello",
    [1, 2], {3: 4}, (5, 6), {"hello": 1}, {"1": 1},
    True, False
))
def test_self(input_):
    assert not isitbullshit(input_, input_)

    IsItBullshitMixin.assertNotBullshit(input_, input_)
    raise_for_problem(input_, input_)
