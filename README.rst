isitbullshit
============

|Build Status| |Code Coverage| |Static Analysis| |PyPi Package|

``isitbullshit`` is small and funny library which is intended to be used like lightweight schema verification for JSONs
but basically it could be used as a schema validator for every generic Python structure: dict, list, tuple etc. It is
written to be pretty much Pythonic in a good sense: easy to use and very clean syntax but powerful enough to clean
your needs. But mostly for verification of incoming JSONs. Actually it is really stable and I am using it in several
production projects, this is an excerpt because I really got tired of reinventing the wheel.

Yes, this is a wheel reinvention also but probably you will like it. Let me show the code.



An example
----------

Okay, let's say you are doing some backend for the library and you have to process JSONs like this:

.. code-block:: javascript

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

You've got an idea, right? Pretty common and rather simple. Let's compose a schema and verify it.

.. code-block:: python

    from json import loads
    from isitbullshit import isitbullshit, OrSkipped

    def rate_validator(value):
        if not (1 <= int(value) <= 5):
            raise ValueError(
                "Value {} has to be from 1 till 5".format(value)
            )

    data = loads(request)
    schema = {
        "model": str,
        "pk": int,
        "fields": {
            "books": [
                {
                    "model": str,
                    "pk": int,
                    "fields": {
                        "title": str,
                        "author": str,
                        "isbn": {
                            "10": str,
                            "13": str
                        },
                        "language": str,
                        "type": ("paperback", "kindle"),
                        "finished": OrSkipped(True),
                        "rate": (rate_validator, None),
                        "tags": [str],
                        "published": {
                            "publisher": str,
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

    if isitbullshit(data, schema):
        raise Error400("Incoming request is not valid")
    process(data)

Pretty straightforward. Let me explain what is going on here.



Basic concepts
--------------

isitbullshit was created to be used with JSONs and actively uses the fact that JSON perfectly matches to Python
internal data structures. Basic rule here: if elements are equal then they should be validated without any problems.

So if you have a code like

.. code-block:: python

    >>> suspicious = {
    ...     "foo": 1,
    ...     "bar": 2
    ... }

then

.. code-block:: python

    >>> print isitbullshit(suspicious, suspicious)
    False

Keep this in mind.

If elements are equal then no additional validation steps have to be used. Otherwise it tries to match types and do
some explicit assertions.

So there are some rules.



Value validation
----------------

Value validation is pretty straighforward: if values are the same or they are equal to each other (operation ``=``)
then validation has to be passed. So the rule is: if ``is`` or ``=`` works, then matching is successful.

.. code-block:: python

    >>> print isitbullshit(1, 1)
    False
    >>> print isitbullshit(1.0, 1.0)
    False
    >>> print isitbullshit(1.0, decimal.Decimal("1.0"))
    False
    >>> print isitbullshit(None, None)
    False
    >>> obj = object()
    >>> print isitbullshit(obj, obj)
    False


Type validation
---------------

If value validation is not passed then type validation is performed. The idea is: ``1`` is ``1``, right? But you will
be satisfied if you know that ``1`` is ``int`` as well, right?

So

.. code-block:: python

    >>> print isitbullshit(1, int)
    False
    >>> print isitbullshit(1.0, float)
    False
    >>> print isitbullshit(decimal.Decimal("1.0"), decimal.Decimal)
    False
    >>> obj = object()
    >>> print isitbullshit(obj, object)
    False



Custom validation
-----------------

Let's get back to an example. Have you mentioned that we have ``rate_validator`` function there? It is custom validator.

It works pretty simple: you define custom callable (function, lambda, class, etc) and ``isitbullshit`` gives it your
value. If no exception is raised than we consider the value as successfully validated. So in our example if a ``rate``
field is not in (1, 5) interval or not integer then exception will be raised.

Custom validators are used mostly in cases if you have to check a content or do not so shallow verifications.

Another example is MongoDB. Do you use ``ObjectId``?

.. code-block:: python

    >>> print isitbullshit(1, bson.ObjectId)
    True
    >>> print isitbullshit("507c7f79bcf86cd7994f6c0e", bson.ObjectId)
    False

I hope you've got an idea.



OrSkipped validator
-------------------

Sometimes we live in a real world which sucks. Sometimes we have schemaless data (and it sucks of course) so some
fields from your requests are missed. Or you do not care. ``isitbullshit`` has 2 different fixes for
that: ``OrSkipped`` and ``WHATEVER``.

If you wrap a part of your validator in ``OrSkipped`` than you mark that it is ok if this field would be absent.
Argument is a validator of course. And if field is in place, it will be validated as expected.

.. code-block:: python

    >>> schema = {
    ...     "foo": 1,
    ...     "bar": OrSkipped(int),
    ...     "baz": OrSkipped(str)
    >>> }
    >>> print isitbullshit({"foo": 1, "bar": 1}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": "str"}, schema)
    True
    >>> print isitbullshit({"foo": 1, "bar": 1, "baz": 1}, schema)
    True
    >>> print isitbullshit({"foo": 1, "bar": 1, "baz": "str"}, schema)
    False

So if we miss any field, it is ok. Unless it is presented and validator-argument point us to a bullshit.

``OrSkipped`` has to be used only with dictionary field validation. You can put it anywhere but then it has no special
meaning, just an object.

By the way, type validation rule is still here: ``itisbullshit(something, something) == False`` anyway so the following
code is valid (and it is reasonable, right?)

.. code-block:: python

    >>> schema = {
    ...     "foo": 1,
    ...     "bar": OrSkipped(int),
    ...     "baz": OrSkipped(str)
    >>> }
    >>> isitbullshit(schema, schema)
    False
    >>> stripped_schema = dict((k, v) for k, v in schema.iteritems() if k != "baz")
    >>> isitbullshit(stripped_schema, schema)
    False
    >>> isitbullshit(schema, stripped_schema)
    False

Guess why.



WHATEVER validator
------------------

``WHATEVER`` is a mark that you do not care what value is. It could be anything, nobody cares.

.. code-block:: python

    >>> schema = {
    ...     "foo": 1,
    ...     "bar": WHATEVER
    >>> }
    >>> print isitbullshit({"foo": 1, "bar": 1}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": "str"}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": object()}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": os.path}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": [1, 2, 3]}, schema)
    False

See? We do not care about a value of a ``bar``.

``WHATEVER`` could be used with any type.


Dict validation
---------------

You've already seen a ``dict`` validation so let me repeat your assumptions: yes, we match values with the same keys.
But there is only one pitfall: if suspicious element has more fields than schema, then validation is ok also.

It has it's own meaning: we can put only those keys and fields we actually care about. Our software later will work
only with this subset so why should we care about the rest of rubbish?

So, an example again:

.. code-block:: python

    >>> schema = {
    ...     "foo": 1,
    ...     "bar": str
    >>> }
    >>> print isitbullshit({"foo": 1, "bar": "st"}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": "str", "baz": 1}, schema)
    False
    >>> print isitbullshit({"foo": 1, "bar": "str", "baz": object()}, schema)
    False

As you can see, we did not mention any ``baz`` in an element but validation still passed.



List validation
---------------

List validation is pretty simple: we define one validator and it will be matched to any list element.

.. code-block:: python

    >>> print isitbullshit([1, 2, 3], [int])
    False
    >>> print isitbullshit([1, 2, 3], [str])
    True
    >>> print isitbullshit([1, 2, "3"], [int])
    True

In the last example, ``"3"`` is not an integer so validation fails.

How could we manage situations when we have heterogeneous elements? We have to use tuples.

And please remember that ``isitbullshit(something, something) == False``.


Tuple validation
----------------

Tuple validation is pretty easy to understand if you consider it as an OR condition. We define several validators
and and the value has to match at least one of them. So

.. code-block:: python

    >>> print isitbullshit(1, (str, dict))
    True
    >>> print isitbullshit(1, (str, int))
    False

``1`` is not ``str`` but it is ``int``.

Now let's try to fix an example in the previous chapter.

.. code-block:: python

    >>> print isitbullshit([1, 2, "3"], [int])
    True
    >>> print isitbullshit([1, 2, "3"], [(int, str)])
    False

And again, do not forget about a rule of thumb: ``isitbullshit(something, something) == False``.



raise_for_problem function
--------------------------

This package also provides you with another method to validate, ``raise_for_problem`` actually this is a core method
which raises an exception on a problem. ``isitbullshit`` allows you to get an idea what is happening in both Python2 and
Python3, let's check an example.

.. code-block:: python

    >>> try:
    ...     raise_for_problem({"foo": "1", "bar": {"baz": 2}}, {"foo": "1", "bar": {"baz": str}})
    ... except ItIsBullshitError as err:
    ...     print err
    {'foo': '1', 'bar': {'baz': 2}}:
        {'baz': 2}:
            2: Scheme mismatch <type 'str'>

Quite clear and nice.



IsItBullshitMixin mixin
-----------------------

``isitbullshit`` also supplied with ``IsItBullshitMixin`` which is intended to be mixed with ``unittest.TestCase``. It
allows you to use 2 additional methods:

* ``assertBullshit``
* ``assertNotBullshit``

Guess what they do.

.. code-block:: python

    from unittest import TestCase
    from isitbullshit import IsItBullshitMixin

    class BullshitTestCase(IsIsBullshitMixin, TestCase):

        def test_bullshit(self):
            self.assertBullshit(1, None)

        def test_not_bullshit(self):
            self.assertNotBullshit(1, int)


.. |Build Status| image:: https://travis-ci.org/9seconds/isitbullshit.svg?branch=master
    :target: https://travis-ci.org/9seconds/isitbullshit

.. |Code Coverage| image:: https://coveralls.io/repos/9seconds/isitbullshit/badge.png?branch=master
    :target: https://coveralls.io/r/9seconds/isitbullshit?branch=master

.. |Static Analysis| image:: https://landscape.io/github/9seconds/isitbullshit/master/landscape.png
    :target: https://landscape.io/github/9seconds/isitbullshit/master

.. |PyPi Package| image:: https://badge.fury.io/py/isitbullshit.svg
    :target: http://badge.fury.io/py/isitbullshit