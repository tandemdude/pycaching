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
from __future__ import annotations

import abc
import typing as t

from typing_extensions import TypeAlias

__all__ = ["Cache", "Serializable"]

_EMPTY = type("_EMPTY")

SerializableT = t.TypeVar("SerializableT", bound="Serializable")
JsonT: TypeAlias = t.Union[t.Dict[str, "JsonT"], t.List["JsonT"], str, int, float, bool, None]


class Cache(abc.ABC):
    _instance: t.Optional[Cache] = None

    @abc.abstractmethod
    def put(self, key: str, at: str, value: t.Any, ttl: t.Optional[int]) -> None:
        ...

    async def aput(self, key: str, at: str, value: t.Any, ttl: t.Optional[int]) -> None:
        self.put(key, at, value, ttl)

    @abc.abstractmethod
    def get(self, key: str, at: str) -> t.Any:
        ...

    async def aget(self, key: str, at: str) -> t.Any:
        return self.get(key, at)

    @abc.abstractmethod
    def evict(self, key: str, at: str, all: bool = False) -> None:
        ...

    async def aevict(self, key: str, at: str, all: bool = False) -> None:
        return self.evict(key, at, all)

    @abc.abstractmethod
    def flush(self) -> None:
        ...

    async def aflush(self) -> None:
        return self.flush()

    @classmethod
    def get_instance(cls) -> t.Optional[Cache]:
        return Cache._instance

    @classmethod
    def set_instance(cls, instance: Cache) -> Cache:
        Cache._instance = instance
        return instance


class Serializable(abc.ABC):
    @abc.abstractmethod
    def to_json(self) -> JsonT:
        ...

    @classmethod
    @abc.abstractmethod
    def from_json(cls: t.Type[SerializableT], payload: JsonT) -> SerializableT:
        ...
