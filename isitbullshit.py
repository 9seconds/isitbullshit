#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
isitbullshit. And this is module description. You do not need those letters,
checkout that docs that isitbullshit_ and IsItBullshitMixin_ have.

The MIT License (MIT)

Copyright (c) 2013 sergey arkhipov

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''


# #############################################################################


from sys import float_info


# #############################################################################


__all__ = 'isitbullshit', 'IsItBullshitMixin'

__title__ = 'isitbullshit'
__author__ = 'Sergey Arkhipov'
__version__ = (0, 1, 0)
__maintainer__ = 'Sergey Arkhipov'
__email__ = 'serge@aerialsounds.org'
__status__ = 'Production'
__credits__ = 'Sergey Arkhipov',
__license__ = 'MIT License'
__copyright__ = 'Copyright 2013 Sergey Arkhipov'


# #############################################################################


def isitbullshit(data, schema):
    '''
    This function is checking and verifying incoming ``data`` using ``schema``
    (which is literally your suspicions) you give.

    Schema is rather arbitrary and flexible beast. Let's checkout simple
    example:

    >>> schema = {
    ...     'hello': basestring,
    ...     'world': int
    ... }
    >>>

    Okay, let's figure out our suspicions. We expect dictionary parse
    from JSON, this is good. Schema is dictionary so it means that ``data``
    has to be dictionary, no lists, arrays and whatever you want. JSON
    payload we are expecting should include 2 keys, *hello* and *world*.
    *Hello* has to be string and world is *int*. Damn, it was simple and good.
    Now let's cast that schema on some example data.

    >>> print isitbullshit([], schema)
    True

    Yeah, this is bullshit. Payload is [] but you expecting something more
    interesting

    >>> print isitbullshit({'hello': 'no', 'world': None}, schema)
    True

    See? World is None, incoming JSON was ``{"hello": "no", "world": null}``
    so there. So, bullshit. We are waiting for something pretty much more
    interesting.

    >>> print isitbullshit({'hello': 'god no!', 'world': 3}, schema)
    False

    Finally, no bullshits. Let's go further.

    >>> schema = {
    ...     'hello': basestring,
    ...     'world': (float, bool, None, 1)
    ... }
    >>>

    Please step back and be write down that ``isitbullshit`` differs tuples
    and lists since there is not library which decodes JSON arrays to Python
    lists. So what does tuple (or set/frozenset) means for that function? It
    defines multiple choice. So *world* might be float, bool, None or
    exact 1. Pretty convenient, huh? Let's checkout some previous example.

    >>> print isitbullshit({'hello': 'no', 'world': None}, schema)
    False

    *world* is ``None`` and ``None`` is listed in ``(float, bool, None, 1)``
    so it suits well at this time. Let's go further, arrays.

    >>> schema = {
    ...     'hello': [basestring],
    ...     'underworld': [
    ...         {'id': int, 'type': 24, 'active': bool, 'price': (float, None)}
    ...     ]
    ... }
    >>>

    I know that arrays might have arbitrary length but, well, as a rule
    they have elements with the same type. if it does not work for you, scroll
    down to the next example. Otherwise, checkout.

    You can put a lot of elements in the list (please distinct tuples and
    lists) but actually only first element would be used and it would be used
    to check a type of each element in a list. Enough words, grab a code.

    >>> payload = {
    ...     'hello': ['sure', 'why not', 1],
    ...     'underworld': [
    ...         {'id': 1, 'type': 24, 'active': True, 'price': 12.35},
    ...         {'id': 2, 'type': 24, 'active': False, 'price': None}
    ...     ]
    ... }
    >>> print isitbullshit(payload, schema)
    False

    Whoa?? Oh... Yeah, sure, of course. Checkout *hello* in ``payload``, it has
    nasty ``1``. Remove it and it will work as expected. Oh, another pretty
    good feature, checkout how we fixed ``type`` to 24. It cannot have another
    value, even another int. Even 25. Even not ask.

    Ok, but what if I want something more flexible? You can use custom
    validators. Let's implement, for example, range validator

    >>> def range_validator(min_=None, max_=None):
    ...     def validator(element):
    ...         if not isinstance(element, int):
    ...             raise AssertionError
    ...         if min_ is not None:
    ...             assert min_ <= element
    ...         if max_ is not None:
    ...             assert element <= max_
    ...     return validator
    >>> schema = {'suspect': range_validator(10, 20)}
    >>> print isitbullshit({'suspect': 30}, schema)
    False
    >>> print isitbullshit({'suspect': 15}, schema)
    True

    You got it. Happy coding.
    '''
    try:
        _isitbullshit_rec(data, schema)
        return False
    except AssertionError:
        return True

# -----------------------------------------------------------------------------

def _isitbullshit_rec(data, schema):
    '''
    This is internal recursive implementation for ``isitbullshit``_ function.
    Actually you should not use that (that's why it is underscored).
    '''
    if isinstance(schema, (tuple, set, frozenset)):
        for suspicion in schema:
            try:
                _isitbullshit_rec(data, suspicion)
                break
            except AssertionError:
                pass
        else:
            raise AssertionError

    elif isinstance(schema, list):
        if not isinstance(data, list):
            raise AssertionError
        if data and not schema:
            raise AssertionError
        for element in data:
            _isitbullshit_rec(element, schema[0])

    elif isinstance(schema, dict):
        if not isinstance(data, dict):
            raise AssertionError
        if set(schema) - set(data):
            raise AssertionError
        for schema_key, schema_value in schema.iteritems():
            _isitbullshit_rec(data[schema_key], schema_value)

    elif schema in (basestring, str, unicode):
        if not isinstance(data, basestring):
            raise AssertionError

    elif schema in (int, float, bool):
        if not isinstance(data, schema):
            raise AssertionError

    elif isinstance(schema, basestring):
        success = (
            isinstance(data, basestring) and
            unicode(schema) == unicode(data)
        )
        if not success:
            raise AssertionError

    elif isinstance(schema, int):
        if not (isinstance(data, int) and data == schema):
            raise AssertionError

    elif isinstance(schema, float):
        success = (
            isinstance(data, float) and
            abs(data - schema) <= float_info.epsilon
        )
        if not success:
            raise AssertionError

    elif callable(schema):
        schema(data)

    elif schema is None and data is not None:
        raise AssertionError

    elif schema != data:
        raise AssertionError


# #############################################################################


class IsItBullshitMixin (object):
    '''
    This is simple mixin to add to your shiny testcases. It brings two
    additional methods, assertBullshit_ and assertNotBullshit_. Using them
    you can easily suspect bullshit. This is good.
    '''

    @staticmethod
    def assertBullshit(data, schema, reason=None):
        '''
        Checks that given ``data`` is came from malformed JSON you do not
        suspect by `schema`.
        '''
        if not isitbullshit(data, schema):
            message = u'Data perfectly match scheme'
            if reason is not None:
                message += u': {}'.format(reason)
            raise AssertionError(message)

    # ---------------------------------

    @staticmethod
    def assertNoBullshit(data, schema, reason=None):
        '''
        Checks that given ``data`` is came from good well formed decoded JSON.
        ``schema`` is your suspicions.
        '''
        if isitbullshit(data, schema):
            message = u'Data and schema are mismatching'
            if reason is not None:
                message += u': {}'.format(reason)
            raise AssertionError(message)
