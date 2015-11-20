from .abc import DefaultMapping


class _CacheDict(dict):

    def __init__(self, getsizeof):
        dict.__init__(self)
        self.getsizeof = getsizeof
        self.size = 0

    def __delitem__(self, key):
        self.size -= dict.pop(self, key)[1]

    def getvalue(self, key):
        return self[key][0]

    def getsize(self, key):
        try:
            return self[key][1]
        except KeyError:
            return 0

    def set(self, key, value, size):
        delta = size - self.getsize(key)
        self[key] = (value, size)
        self.size += delta


class _SimpleDict(dict):

    @property
    def size(self):
        return len(self)

    def getvalue(self, key):
        return self[key]

    def getsize(self, key):
        return 1 if key in self else 0

    def set(self, key, value, _):
        self[key] = value

    @staticmethod
    def getsizeof(value):
        return 1


class Cache(DefaultMapping):
    """Mutable mapping to serve as a simple cache or cache base class."""

    def __init__(self, maxsize, missing=None, getsizeof=None):
        if missing:
            self.__missing = missing
        if getsizeof:
            self.__data = _CacheDict(getsizeof)
        else:
            self.__data = _SimpleDict()
        self.__maxsize = maxsize

    def __repr__(self):
        return '%s(%r, maxsize=%d, currsize=%d)' % (
            self.__class__.__name__,
            list(self.items()),
            self.maxsize,
            self.currsize,
        )

    def __contains__(self, key):
        return key in self.__data

    def __getitem__(self, key):
        try:
            return self.__data.getvalue(key)
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key, value):
        size = self.__data.getsizeof(value)
        if self.__data.getsize(key) < size:
            maxsize = self.maxsize
            if size > maxsize:
                raise ValueError('value too large')
            while self.__data.size + size > maxsize:
                self.popitem()
        self.__data.set(key, value, size)

    def __delitem__(self, key):
        del self.__data[key]

    def __missing__(self, key):
        value = self.__missing(key)
        self.__setitem__(key, value)
        return value

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    @staticmethod
    def __missing(key):
        raise KeyError(key)

    @property
    def maxsize(self):
        """The maximum size of the cache."""
        return self.__maxsize

    @property
    def currsize(self):
        """The current size of the cache."""
        return self.__data.size

    def getsizeof(self, value):
        """Return the size of a cache element's value."""
        return self.__data.getsizeof(value)
