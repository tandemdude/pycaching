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

import aioredis
import redis

from cache import abc
from cache import serde

__all__ = ["RedisCacheImpl"]


class RedisCacheImpl(abc.Cache):
    _VERSION = "0"

    def __init__(self, url: str) -> None:
        self._url = url
        self.__sync_connection: t.Optional[redis.Redis] = None
        self.__async_connection: t.Optional[aioredis.Redis] = None
        self._class_cache: t.Dict[str, t.Type[abc.Serializable]] = {}

    def _sync_connection(self) -> redis.Redis:
        if self.__sync_connection is None:
            self.__sync_connection = redis.from_url(self._url)
        return self.__sync_connection

    async def _async_connection(self) -> aioredis.Redis:
        if self.__async_connection is None:
            self.__async_connection = aioredis.from_url(self._url)
        return self.__async_connection

    def put(self, key: str, at: str, value: t.Any, ttl: t.Optional[int]) -> None:
        self._sync_connection().set(f"pyc_{self._VERSION}:{key}:{at}", serde.serialize(value), ex=ttl)

    async def aput(self, key: str, at: str, value: t.Any, ttl: t.Optional[int]) -> None:
        await (await self._async_connection()).set(f"pyc_{self._VERSION}:{key}:{at}", serde.serialize(value), ex=ttl)

    def get(self, key: str, at: str) -> t.Any:
        value: t.Optional[bytes] = self._sync_connection().get(f"pyc_{self._VERSION}:{key}:{at}")
        return serde.deserialize(value)

    async def aget(self, key: str, at: str) -> t.Any:
        value: t.Optional[bytes] = await (await self._async_connection()).get(f"pyc_{self._VERSION}:{key}:{at}")
        return serde.deserialize(value)

    def evict(self, key: str, at: t.Optional[str] = None, all: bool = False) -> None:
        conn = self._sync_connection()
        if not all:
            conn.delete(f"pyc_{self._VERSION}:{key}:{at}")
            return

        keys = conn.keys(f"pyc_{self._VERSION}:{key}:*")
        if not keys:
            return
        conn.delete(*keys)

    async def aevict(self, key: str, at: str, all: bool = False) -> None:
        conn = await self._async_connection()
        if not all:
            await conn.delete(f"pyc_{self._VERSION}:{key}:{at}")
            return

        keys = await conn.keys(f"pyc_{self._VERSION}:{key}:*")
        if not keys:
            return
        await conn.delete(*keys)

    def flush(self) -> None:
        conn = self._sync_connection()
        keys = conn.keys(f"pyc_{self._VERSION}:*")
        if not keys:
            return
        conn.delete(*keys)

    async def aflush(self) -> None:
        conn = await self._async_connection()
        keys = await conn.keys(f"pyc_{self._VERSION}:*")
        if not keys:
            return
        await conn.delete(*keys)
