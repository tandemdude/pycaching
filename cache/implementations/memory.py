# Copyright (c) 2022-present tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import collections
import time
import typing as t

from cache import abc

__all__ = ["InMemoryCacheImpl"]


class CachedObject:
    __slots__ = ("value", "expires")

    def __init__(self, value: t.Any, ttl: t.Optional[int]) -> None:
        self.value = value
        self.expires = (time.monotonic() + ttl) if ttl is not None else None

    @property
    def expired(self) -> bool:
        if self.expires is None:
            return False
        return time.monotonic() >= self.expires


class InMemoryCacheImpl(abc.Cache):
    def __init__(self):
        self._store: t.Dict[str, t.Dict[str, CachedObject]] = collections.defaultdict(collections.defaultdict)

    def put(self, key: str, at: str, value: t.Any, ttl: t.Optional[int]) -> None:
        self._store[key][at] = CachedObject(value, ttl)

    def get(self, key: str, at: str) -> t.Any:
        if key not in self._store:
            return abc._EMPTY

        obj = self._store[key].get(at, abc._EMPTY)
        if obj is not abc._EMPTY:
            if obj.expired:
                self.evict(key, at)
                return abc._EMPTY
            return obj.value
        return abc._EMPTY

    def evict(self, key: str, at: str, all: bool = False) -> t.Any:
        if key not in self._store:
            return

        if not all:
            self._store[key].pop(at, None)
        else:
            self._store[key].clear()

    def flush(self) -> None:
        self._store.clear()
