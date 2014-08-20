#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import pytest

from six import moves, text_type

from isitbullshit import isitbullshit, raise_for_problem, IsItBullshitMixin, \
    ItIsBullshitError, WHATEVER, OrSkipped


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


class TestBullsit(object):

    @pytest.mark.parametrize("input_", (
        1, 1.0, {"1": 1}, [1], (1,), "",
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_is(self, input_):
        positive(input_, input_)

    @pytest.mark.parametrize("input_", (
        1, 1.0, {"1": 1}, [1], (1,), "",
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_not_is(self, input_):
        negative(input_, object())

    def test_numbers(self):
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
    def test_whatever(self, input_):
        positive(input_, WHATEVER)

    @pytest.mark.parametrize("input_", (
        list, dict, tuple
    ))
    def test_empty_schemas(self, input_):
        funcs = (
            isitbullshit,
            IsItBullshitMixin.assertBullshit,
            IsItBullshitMixin.assertNotBullshit,
            raise_for_problem
        )
        for func in funcs:
            with pytest.raises(TypeError):
                func({"data": 1, "time": 2}, input_())

    def test_multiple_validators_in_list(self):
        funcs = (
            isitbullshit,
            IsItBullshitMixin.assertBullshit,
            IsItBullshitMixin.assertNotBullshit,
            raise_for_problem
        )
        for func in funcs:
            with pytest.raises(TypeError):
                func({"data": 1, "time": 2}, [1, 2, 3, 4])

    @pytest.mark.parametrize("input_", (
        1, 1.0, [1], {"1": 1}, (1,), "",
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_dict_incorrect_types(self, input_):
        validators = (
            {1: 1},
            {"1": 2},
            {"1": 1, 2: 2}
        )
        for validator in validators:
            negative(input_, validator)

    def test_dict_small_subset(self):
        positive(
            dict((idx, idx) for idx in moves.range(10)),
            dict((idx, idx) for idx in moves.range(5))
        )

    @pytest.mark.parametrize("input_", (
        1, 1.0, [1], {"1": 1}, (1,), "",
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_list_incorrect_types(self, input_):
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
    def test_list_simple_validator(self, input_, validator_):
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
    def test_list_complex_validator(self, input_, validator_):
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
    def test_tuple_validator(self, input_, validator_, type_):
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
    def test_string(self, input_, result_):
        func = positive if result_ else negative
        func("hello", input_)

    @pytest.mark.parametrize("input_", (
        1, 1.0, [1], {"1": 1}, (1,),
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_not_string(self, input_):
        negative(input_, "hello")

    @pytest.mark.parametrize("input_, result_", (
        (1.0, True),
        (1.0 + sys.float_info.epsilon, False),
        (1.0 - sys.float_info.epsilon, False),
    ))
    def test_float(self, input_, result_):
        func = positive if result_ else negative
        func(1.0, input_)

    @pytest.mark.parametrize("input_", (
        2, 2.0, [1], {"1": 1}, (1,),
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_not_float(self, input_):
        negative(input_, 10.0)

    def test_custom_callable(self):
        # noinspection PyUnusedLocal
        def validator_ok(input_):
            return 1

        # noinspection PyUnusedLocal
        def validator_nok(input_):
            raise ItIsBullshitError("Test", "Test")

        positive("1", validator_ok)
        negative("1", validator_nok)

    def test_string_itisbullshiterror(self):
        key_error = ItIsBullshitError("3 line", "Key Error")
        second_error = ItIsBullshitError("2 line", key_error)
        first_error = ItIsBullshitError("3 line", second_error)

        output = text_type(first_error)
        output = [line.strip() for line in output.split("\n")]
        assert ["3 line:", "2 line:", "3 line: Key Error"] == output

        repr(first_error)
        str(first_error)

    @pytest.mark.parametrize("input_", (
        2, 2.0, [1], {"1": 1}, (1,),
        set([]), frozenset([]), object(), pytest,
        True, False, None, Ellipsis
    ))
    def test_orskipped_fails(self, input_):
        with pytest.raises(TypeError):
            negative(input_, OrSkipped(input_))

    @pytest.mark.parametrize("input_, result_", (
        ({"foo": "bar", "hello": "world"}, True),
        ({"foo": "bar", "hello": 1}, False),
        ({"foo": "bar", "hello": OrSkipped("world")}, True),
        ({"foo": "bar", "hello": OrSkipped(1)}, False),
    ))
    def test_skipped_scheme(self, input_, result_):
        func = positive if result_ else negative
        func({"foo": "bar", "hello": "world"}, input_)

    @pytest.mark.parametrize("input_, result_", (
        ({"foo": "bar", "hello": "world"}, True),
        ({"foo": "bar", "hello": 1}, False),
        ({"foo": "bar"}, True),
        ({"foo": "bar", "hello": 1}, False),
        ({"foo": "bar", "hello": OrSkipped("world")}, False),
    ))
    def test_skipped_element(self, input_, result_):
        func = positive if result_ else negative
        func(input_, {"foo": "bar", "hello": OrSkipped("world")})
