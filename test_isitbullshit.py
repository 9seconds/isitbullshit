#!/usr/bin/env python
# -*- coding: utf-8 -*-


# #############################################################################


from isitbullshit import IsItBullshitMixin

from unittest import main, TestCase


# #############################################################################


class IsItBullshitTestCase (TestCase, IsItBullshitMixin):

    def test_none(self):
        self.assertNoBullshit(None, None)
        self.assertBullshit(None, [])
        self.assertBullshit(None, '')

    # ---------------------------------

    def test_str(self):
        for nobullshit in ('', str, basestring, unicode):
            self.assertNoBullshit('', nobullshit, nobullshit)
        self.assertBullshit('1', '')
        self.assertBullshit('1', 1)

    # ---------------------------------

    def test_int(self):
        for bullshit in ('1', [1], {}, basestring, float):
            self.assertBullshit(1, bullshit, bullshit)
        for nobullshit in (1, int):
            self.assertNoBullshit(1, nobullshit, nobullshit)

    # ---------------------------------

    def test_tuple(self):
        for bullshit in ('1', [1], {}, basestring, float):
            self.assertNoBullshit(1, (bullshit, 1), bullshit)

    # ---------------------------------

    def test_dict(self):
        self.assertNoBullshit({}, {})
        self.assertBullshit({}, {'1': 1})
        self.assertNoBullshit(
            {'1': '2', '2': 1},
            {'1': basestring, '2': (int, None)}
        )
        self.assertNoBullshit(
            {'1': '2', '2': 1},
            {'1': basestring}
        )

    # ---------------------------------

    def test_list(self):
        self.assertNoBullshit(range(10), [int])
        self.assertNoBullshit([{}] * 10, [{}])

    # ---------------------------------

    def test_complex(self):
        payload = {
            'id': '12bacc267fe',
            'price': 100.0,
            'visitors': 10,
            'geometry': [
                {'lat': 35, 'lon': 96},
                {'lat': 36, 'lon': 96},
                {'lat': 37, 'lon': 99},
                {'lat': 38, 'lon': None}
            ]
        }
        self.assertNoBullshit(
            payload,
            {
                'id': basestring,
                'price': float,
                'visitors': int,
                'geometry': [
                    {
                        'lat': (int, float),
                        'lon': (int, float, None)
                    }
                ]
            }
        )

# #############################################################################


if __name__ == '__main__':
    main()
