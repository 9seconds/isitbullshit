isitbullshit
============

small library for verifying parsed JSONs if they are bullshit or not

It has 2 cool features: `isitbullshit` function and `IsItBullshitMixin` for `unittest.TestCase`.

```python
>>> from isitbullshit import isitbullshit, IsItBullshitMixin
```

`isitbullshit` function is checking and verifying incoming `data` using `schema`
(which is literally your suspicions) you give.

Schema is rather arbitrary and flexible beast. Let's checkout simple
example:

```python
>>> schema = {
...     'hello': basestring,
...     'world': int
... }
>>>
```

Okay, let's figure out our suspicions. We expect dictionary parse
from JSON, this is good. Schema is dictionary so it means that `data`
has to be dictionary, no lists, arrays and whatever you want. JSON
payload we are expecting should include 2 keys, _hello_ and _world_.
_Hello_ has to be string and world is _int_. Damn, it was simple and good.
Now let's cast that schema on some example data.

```python
>>> print isitbullshit([], schema)
True
```

Yeah, this is bullshit. Payload is `[]` but you expecting something more
interesting

```python
>>> print isitbullshit({'hello': 'no', 'world': None}, schema)
True
```

See? World is None, incoming JSON was `{"hello": "no", "world": null}`
so there. So, bullshit. We are waiting for something pretty much more
interesting.

```python
>>> print isitbullshit({'hello': 'god no!', 'world': 3}, schema)
False
```

Finally, no bullshits. Let's go further.

```python
>>> schema = {
...     'hello': basestring,
...     'world': (float, bool, None, 1)
... }
>>>
```

Please step back and be write down that `isitbullshit` differs tuples
and lists since there is not library which decodes JSON arrays to Python
lists. So what does tuple (or set/frozenset) means for that function? It
defines multiple choice. So _world_ might be `float`, `bool`, `None` or
exact `1`. Pretty convenient, huh? Let's checkout some previous example.

```python
>>> print isitbullshit({'hello': 'no', 'world': None}, schema)
False
```

_world_ is `None` and `None` is listed in `(float, bool, None, 1)`
so it suits well at this time. Let's go further, arrays.

```python
>>> schema = {
...     'hello': [basestring],
...     'underworld': [
...         {'id': int, 'type': 24, 'active': bool, 'price': (float, None)}
...     ]
... }
>>>
```

I know that arrays might have arbitrary length but, well, as a rule
they have elements with the same type. if it does not work for you, scroll
down to the next example. Otherwise, checkout.

You can put a lot of elements in the list (please distinct tuples and
lists) but actually only first element would be used and it would be used
to check a type of each element in a list. Enough words, grab a code.

```python
>>> payload = {
...     'hello': ['sure', 'why not', 1],
...     'underworld': [
...         {'id': 1, 'type': 24, 'active': True, 'price': 12.35},
...         {'id': 2, 'type': 24, 'active': False, 'price': None}
...     ]
... }
>>> print isitbullshit(payload, schema)
False
```

Whoa?? Oh... Yeah, sure, of course. Checkout _hello_ in `payload`, it has
nasty `1`. Remove it and it will work as expected. Oh, another pretty
good feature, checkout how we fixed `type` to 24. It cannot have another
value, even another int. Even 25. Even not ask.

Ok, but what if I want something more flexible? You can use custom
validators. Let's implement, for example, range validator

````python
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
```

You got it. Happy coding.
