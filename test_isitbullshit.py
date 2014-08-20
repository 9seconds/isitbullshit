#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import decimal
import json
import sys
import os.path

import pytest

from six import moves, text_type, string_types, iteritems

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
        text_type(first_error)

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


class TestREADME(object):

    def test_main_example(self):
        data = """
            {
                "model": "book_collection",
                "pk": 318,
                "fields": {
                    "books": [
                        {
                            "model": "book",
                            "pk": 18,
                            "fields": {
                                "title": "Jane Eyre",
                                "author": "Charlotte Brontë",
                                "isbn": {
                                    "10": "0142437204",
                                    "13": "978-0142437209"
                                },
                                "rate": null,
                                "language": "English",
                                "type": "paperback",
                                "tags": [
                                    "Penguin Classics",
                                    "Classics",
                                    "Favorites"
                                ],
                                "published": {
                                    "publisher": "Penguin Books",
                                    "date": {
                                        "day": 24,
                                        "month": 4,
                                        "year": 2003
                                    }
                                }
                            }
                        },
                        {
                            "model": "book",
                            "pk": 18,
                            "fields": {
                                "title": "The Great Gatsby",
                                "author": "F.Scott Fitzgerald",
                                "isbn": {
                                    "10": "185326041X",
                                    "13": "978-1853260414"
                                },
                                "language": "English",
                                "type": "paperback",
                                "finished": true,
                                "rate": 4,
                                "tags": [
                                    "Wordsworth Classics",
                                    "Classics",
                                    "Favorites"
                                ],
                                "published": {
                                    "publisher": "Wordsworth Editions Ltd",
                                    "date": {
                                        "day": 1,
                                        "month": 5,
                                        "year": 1992
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        """
        def rate_validator(value):
            if not (1 <= int(value) <= 5):
                raise ValueError(
                    "Value {} has to be from 1 till 5".format(value)
                )

        schema = {
            "model": string_types,
            "pk": int,
            "fields": {
                "books": [
                    {
                        "model": string_types,
                        "pk": int,
                        "fields": {
                            "title": string_types,
                            "author": string_types,
                            "isbn": {
                                "10": string_types,
                                "13": string_types
                            },
                            "language": string_types,
                            "type": ("paperback", "kindle"),
                            "finished": OrSkipped(True),
                            "rate": (rate_validator, None),
                            "tags": [string_types],
                            "published": {
                                "publisher": string_types,
                                "date": OrSkipped(
                                    {
                                        "day": int,
                                        "month": int,
                                        "year": int
                                    }
                                )
                            }
                        }
                    }
                ]
            }
        }

        parsed_data = json.loads(data)

        positive(parsed_data, schema)

    def test_basic_concepts(self):
        suspicious = {
            "foo": 1,
            "bar": 2
        }
        positive(suspicious, suspicious)

    @pytest.mark.parametrize("input_, validator_", (
        (1, 1),
        (1.0, 1.0),
        (None, None)
    ))
    def test_value_validation(self, input_, validator_):
        positive(input_, validator_)

    def test_value_validation_object(self):
        obj = object()
        positive(obj, obj)

    @pytest.mark.parametrize("input_, validator_", (
        (1, int),
        (1.0, float),
        (decimal.Decimal("1.0"), decimal.Decimal),
        (object(), object)
    ))
    def test_type_validation(self, input_, validator_):
        positive(input_, validator_)

    @pytest.mark.parametrize("input_, result_", (
        ({"foo": 1, "bar": 1}, True),
        ({"foo": 1, "bar": "str"}, False),
        ({"foo": 1, "bar": 1, "baz": 1}, False),
        ({"foo": 1, "bar": 1, "baz": "str"}, True)
    ))
    def test_orskipped1(self, input_, result_):
        schema = {
            "foo": 1,
            "bar": OrSkipped(int),
            "baz": OrSkipped(string_types)
        }

        func = positive if result_ else negative
        func(input_, schema)

    def test_orskipped2(self):
        schema = {
            "foo": 1,
            "bar": OrSkipped(int),
            "baz": OrSkipped(str)
        }

        positive(schema, schema)

        stripped_schema = dict((k, v) for k, v in iteritems(schema) if k != "baz")
        positive(schema, stripped_schema)
        raise_for_problem(stripped_schema, schema)

    @pytest.mark.parametrize("input_", (
        {"foo": 1, "bar": 1},
        {"foo": 1, "bar": "str"},
        {"foo": 1, "bar": object()},
        {"foo": 1, "bar": os.path},
        {"foo": 1, "bar": [1, 2, 3]}
    ))
    def test_whatever(self, input_):
        positive(input_, {"foo": 1, "bar": WHATEVER})

    @pytest.mark.parametrize("input_", (
        {"foo": 1, "bar": "st"},
        {"foo": 1, "bar": "str", "baz": 1},
        {"foo": 1, "bar": "str", "baz": object()}
    ))
    def test_dict_validation(self, input_):
        schema = {
            "foo": 1,
            "bar": string_types
        }

        positive(input_, schema)

    @pytest.mark.parametrize("input_, validator_, result_", (
        ([1, 2, 3], [int], True),
        ([1, 2, 3], [str], False),
        ([1, 2, "3"], [int], False)
    ))
    def test_list_validation(self, input_, validator_, result_):
        func = positive if result_ else negative
        func(input_, validator_)

    @pytest.mark.parametrize("input_, validator_, result_", (
        (1, (str, dict), False),
        (1, (str, int), True),
        ([1, 2, "3"], [int], False),
        ([1, 2, "3"], [(int,) + string_types], True)
    ))
    def test_tuple_validation(self, input_, validator_, result_):
        func = positive if result_ else negative
        func(input_, validator_)
