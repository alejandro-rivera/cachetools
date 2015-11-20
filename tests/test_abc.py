import unittest

import cachetools.abc


class DefaultDict(cachetools.abc.DefaultMapping):

    def __init__(self, *args, **kwargs):
        self.data = dict(*args, **kwargs)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return cachetools.abc.DefaultMapping.__getitem__(self, key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


class DefaultMappingTest(unittest.TestCase):

    def test_no_missing(self):
        class D(DefaultDict):
            pass

        d = D({1: 2, 3: 4})
        self.assertNotIn(42, d)
        self.assertNotIn(42, d.keys())
        self.assertIsNone(d.get(42))
        with self.assertRaises(KeyError):
            d[42]
        with self.assertRaises(KeyError):
            del d[42]
        with self.assertRaises(KeyError):
            d.pop(42)
        self.assertIsNone(d.setdefault(42))

    def test_missing_error(self):
        class D(DefaultDict):
            def __missing__(self, key):
                raise RuntimeError(key)

        d = D({1: 2, 3: 4})
        self.assertNotIn(42, d)
        self.assertNotIn(42, d.keys())
        self.assertIsNone(d.get(42))
        with self.assertRaises(RuntimeError):
            d[42]
        with self.assertRaises(KeyError):
            del d[42]
        with self.assertRaises(KeyError):
            d.pop(42)
        self.assertIsNone(d.setdefault(42))

    def test_missing_instance(self):
        # An instance variable __missing__ should have no effect
        class D(DefaultDict):
            def __init__(self, *args, **kwargs):
                self.__missing__ = lambda key: None
                DefaultDict.__init__(self, *args, **kwargs)

        d = D({1: 2, 3: 4})
        self.assertNotIn(42, d)
        self.assertNotIn(42, d.keys())
        self.assertIsNone(d.get(42))
        with self.assertRaises(KeyError):
            d[42]
        with self.assertRaises(KeyError):
            del d[42]
        with self.assertRaises(KeyError):
            d.pop(42)
        self.assertIsNone(d.setdefault(42))

    def test_missing_value(self):
        class D(DefaultDict):
            def __missing__(self, key):
                return 42

        d = D({1: 2, 3: 4})
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertIsNone(d.get(42))
        self.assertEqual(d[2], 42)
        with self.assertRaises(KeyError):
            del d[42]
        with self.assertRaises(KeyError):
            d.pop(42)
        self.assertIsNone(d.setdefault(42))
