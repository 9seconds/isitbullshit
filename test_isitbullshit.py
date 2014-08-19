#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import pytest

from six import moves, text_type

from isitbullshit import isitbullshit, raise_for_problem, IsItBullshitMixin, \
    ItIsBullshitError, WHATEVER


def positive(element, scheme):
    assert not isitbullshit(element, scheme)

    IsItBullshitMixin.assertNotBullshit(element, scheme)
    with pytest.raises(AssertionError):
        IsItBullshitMixin.assertBullshit(element, scheme)
    raise_for_problem(element, scheme)


def negative(element, scheme):
    assert isitbullshit(element, scheme)

    IsItBullshitMixin.assertBullshit(element, scheme)
    with pytest.raises(AssertionError):
        IsItBullshitMixin.assertNotBullshit(element, scheme)
    with pytest.raises(ItIsBullshitError):
        raise_for_problem(element, scheme)


@pytest.mark.parametrize("input_", (
    1, 1.0, {"1": 1}, [1], (1,), "",
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_is(input_):
    positive(input_, input_)


@pytest.mark.parametrize("input_", (
    1, 1.0, {"1": 1}, [1], (1,), "",
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_not_is(input_):
    negative(input_, object())


def test_numbers():
    positive(1.0, 1)
    positive(1, 1.0)


# noinspection PySetFunctionToLiteral
@pytest.mark.parametrize("input_", (
    1,
    1.0,
    {}, {"1": 1}, {"1": 1, "2": 1},
    [], [1], [1, "1"],
    tuple(), (1,), (1, "2"),
    set([]), set([1]), set([1, 2]),
    frozenset([]), frozenset([1]), frozenset([1, 2]),
    object(), pytest, Ellipsis,
    "", "1",
))
def test_whatever(input_):
    positive(input_, WHATEVER)


@pytest.mark.parametrize("input_", (
    list, dict, tuple
))
def test_empty_schemas(input_):
    funcs = (
        isitbullshit,
        IsItBullshitMixin.assertBullshit,
        IsItBullshitMixin.assertNotBullshit,
        raise_for_problem
    )
    for func in funcs:
        with pytest.raises(ValueError):
            func({"data": 1, "time": 2}, input_())


def test_multiple_validators_in_list():
    funcs = (
        isitbullshit,
        IsItBullshitMixin.assertBullshit,
        IsItBullshitMixin.assertNotBullshit,
        raise_for_problem
    )
    for func in funcs:
        with pytest.raises(ValueError):
            func({"data": 1, "time": 2}, [1, 2, 3, 4])


@pytest.mark.parametrize("input_", (
    1, 1.0, [1], {"1": 1}, (1,), "",
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_dict_incorrect_types(input_):
    validators = (
        {1: 1},
        {"1": 2},
        {"1": 1, 2: 2}
    )
    for validator in validators:
        negative(input_, validator)


def test_dict_small_subset():
    positive(
        dict((idx, idx) for idx in moves.range(10)),
        dict((idx, idx) for idx in moves.range(5))
    )


@pytest.mark.parametrize("input_", (
    1, 1.0, [1], {"1": 1}, (1,), "",
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_list_incorrect_types(input_):
    validators = (
        [2],
        [object()],
        [{"ohai": 1}]
    )
    for validator in validators:
        negative(input_, validator)


@pytest.mark.parametrize("input_, validator_", (
    (list(moves.range(10)), [int]),
    ([1.0, 2.0], [float]),
    ([pytest, pytest, pytest], [pytest]),
    ([1, 1, 1, 1, 1], [1])
))
def test_list_simple_validator(input_, validator_):
    positive(input_, validator_)


@pytest.mark.parametrize("input_, validator_", (
    ({"foo": 1, "bar": 2}, {"foo": 1}),
    ({"foo": 1, "bar": 2}, {"foo": int}),
    ({"foo": 1, "bar": 2}, {"foo": 1, "bar": 2}),
    ({"foo": 1, "bar": 2}, {"foo": 1, "bar": int}),
    ({"foo": 1, "bar": 2}, {"foo": int, "bar": int}),
    ({"foo": [1], "bar": 2}, {"foo": [int], "bar": int}),
    ({"foo": [1, 2], "bar": 2}, {"foo": [int], "bar": int}),
    ({"foo": [1, 2], "bar": 2}, {"foo": [1, 2], "bar": 2}),
))
def test_list_complex_validator(input_, validator_):
    positive(input_, validator_)


@pytest.mark.parametrize("input_, validator_, type_", (
    (1, (None, 1), True),
    (None, (None, 1), True),
    ([1], (object(), 1), False),
    ([1], (object(), 1, [1]), True),
    ([1], (object(), 1, [int]), True),
    ([1], (object(), [int], [int]), True),
    ([1], (object(), [int], 1), True),
    ([1], ([int], object(), 1), True),
    ([1], (object(), int, [int]), True),
    ([1], (object(), int), False)
))
def test_tuple_validator(input_, validator_, type_):
    func = positive if type_ else negative
    func(input_, validator_)


@pytest.mark.parametrize("input_, result_", (
    ("hello", True),
    ("hello_", False),
    (object(), False),
    (r"^hello", True),
    (r"hello$", True),
    (r"^hello$", True),
    (r"hel{2}o$", True),
    (r"\w+o$", True),
    (r"h.*l", True)
))
def test_string(input_, result_):
    func = positive if result_ else negative
    func("hello", input_)


@pytest.mark.parametrize("input_", (
    1, 1.0, [1], {"1": 1}, (1,),
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_not_string(input_):
    negative(input_, "hello")


@pytest.mark.parametrize("input_, result_", (
    (1.0, True),
    (1.0 + sys.float_info.epsilon, False),
    (1.0 - sys.float_info.epsilon, False),
))
def test_float(input_, result_):
    func = positive if result_ else negative
    func(1.0, input_)


@pytest.mark.parametrize("input_", (
    2, 2.0, [1], {"1": 1}, (1,),
    set([]), frozenset([]), object(), pytest,
    True, False, None, Ellipsis
))
def test_not_float(input_):
    negative(input_, 10.0)


def test_custom_callable():
    # noinspection PyUnusedLocal
    def validator_ok(input_):
        return 1

    # noinspection PyUnusedLocal
    def validator_nok(input_):
        raise ItIsBullshitError("Test", "Test")

    positive("1", validator_ok)
    negative("1", validator_nok)


def test_string_itisbullshiterror():
    key_error = ItIsBullshitError("3 line", "Key Error")
    second_error = ItIsBullshitError("2 line", key_error)
    first_error = ItIsBullshitError("3 line", second_error)

    output = text_type(first_error)
    output = [line.strip() for line in output.split("\n")]
    assert ["3 line:", "2 line:", "3 line: Key Error"] == output

    repr(first_error)
    str(first_error)