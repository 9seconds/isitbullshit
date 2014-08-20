isitbullshit
============

isitbullshit is small and funny library which is intended to be used like lightweight schema verification for JSONs but
basically it could be used as a schema validator for every generic Python structure: dict, list, tuple etc. It is
written to be pretty much Pythonic in a good sense: easy to use and very clean syntax but powerful enough to clean
your needs. But mostly for verification of incoming JSONs. Actually it is really stable and I am using it in a several
production projects, this is an excerpt because I really got tired from wheel reinventions.

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

You've got an idea, right? Pretty common and rather simple. Let's compose schema and verify it.

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
                        "finished": OrSkipped(true),
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

isitbullshit was created to be used with JSONs and actively uses this fact that JSON perfectly matches to Python
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

Value validation is pretty straighforward: if values are the sames or they are equal to each other (operation ``=``)
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

Let's back to an example. Have you mentioned that we have ``rate_validator`` function there? It is custom validator.

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



OrSkipped and WHATEVER validator
--------------------------------

Sometimes we live in a real world which sucks. Sometimes we have schemaless data (and it sucks of course) so some
fields from your requests are missed.