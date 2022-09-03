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
import typing as t

__all__ = ["put", "aput", "get", "aget", "evict", "aevict"]

from cache import abc
from cache import errors


def put(key: str, at: str, value: t.Any, ttl: t.Optional[int] = None) -> None:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.put(key, at, value, ttl)


def aput(key: str, at: str, value: t.Any, ttl: t.Optional[int] = None) -> t.Coroutine[None, None, None]:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.aput(key, at, value, ttl)


def get(key: str, at: str) -> t.Any:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.get(key, at)


def aget(key: str, at: str) -> t.Coroutine[None, None, t.Any]:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.aget(key, at)


@t.overload
def evict(key: str, at: str) -> None:
    ...


@t.overload
def evict(key: str, *, all: t.Literal[True]) -> None:
    ...


def evict(key: str, at: t.Optional[str] = None, *, all: bool = False):
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.evict(key, at, all)


@t.overload
def aevict(key: str, at: str) -> t.Coroutine[None, None, None]:
    ...


@t.overload
def aevict(key: str, *, all: t.Literal[True]) -> t.Coroutine[None, None, None]:
    ...


def aevict(key: str, at: str, *, all: bool = False) -> t.Coroutine[None, None, None]:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.aevict(key, at, all)


def flush() -> None:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.flush()


def aflush() -> t.Coroutine[None, None, None]:
    if (cache := abc.Cache.get_instance()) is None:
        raise errors.CacheNotSetUpError("Cache has not been initialised")
    return cache.aflush()
