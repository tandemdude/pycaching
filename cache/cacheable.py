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

import inspect
import typing as t

import pysel

from cache import abc
from cache import errors

__all__ = ["Cacheable"]


def create_context_dict(
    argument_order: t.Dict[str, t.Tuple[t.Any, t.Any]], args: t.Sequence[t.Any], kwargs: t.Mapping[str, t.Any]
) -> t.Dict[str, t.Any]:
    values = {}

    mutable_args, mutable_kwargs = list(args), dict(kwargs)
    for name, (default_value, kind) in argument_order.items():
        if kind is inspect.Parameter.VAR_POSITIONAL:
            values[name] = mutable_args or default_value
        elif kind is inspect.Parameter.VAR_KEYWORD:
            values[name] = mutable_kwargs.copy() or default_value
        else:
            values[name] = mutable_args.pop(0) if args else mutable_kwargs.pop(name, default_value)

    return values


class Cacheable:
    def __init__(
        self,
        callback,
        key_exp: t.Union[str, pysel.Expression[t.Any]],
        at_exp: t.Union[str, pysel.Expression[t.Any]],
        when_exp: t.Optional[pysel.Expression[t.Any]] = None,
        unless_exp: t.Optional[pysel.Expression[t.Any]] = None,
        ttl: t.Optional[t.Union[int, pysel.Expression[int]]] = None,
    ) -> None:
        self._cache: t.Optional[abc.Cache] = None
        self._callback = callback
        self._key_exp = key_exp
        self._at_exp = at_exp
        self._when_exp = when_exp
        self._unless_exp = unless_exp
        self._ttl_exp = ttl

        self.argument_order = {}
        for name, param in inspect.signature(callback).parameters.items():
            self.argument_order[name] = param.default, param.kind

    @property
    def cache(self) -> abc.Cache:
        if self._cache is None:
            self._cache = abc.Cache.get_instance()

        if self._cache is None:
            raise errors.CacheNotSetUpError("Cache has not been initialised")

        return self._cache

    def _key(self, ctx: t.Dict[str, t.Any]) -> str:
        if isinstance(self._key_exp, str):
            return self._key_exp
        return str(self._key_exp.evaluate(ctx))

    def _at(self, ctx: t.Dict[str, t.Any]) -> str:
        if isinstance(self._at_exp, str):
            return self._at_exp
        return str(self._at_exp.evaluate(ctx))

    def _when(self, ctx: t.Dict[str, t.Any]) -> bool:
        if self._when_exp is None:
            return True
        return bool(self._when_exp.evaluate(ctx))

    def _unless(self, ctx: t.Dict[str, t.Any]) -> bool:
        if self._unless_exp is None:
            return False
        return bool(self._unless_exp.evaluate(ctx))

    def _ttl(self, ctx: t.Dict[str, t.Any]) -> t.Optional[int]:
        if self._ttl_exp is None:
            return None
        return int(self._ttl_exp.evaluate(ctx))

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if inspect.iscoroutinefunction(self._callback):
            return self.__acall__(*args, **kwargs)

        ctx = create_context_dict(self.argument_order, args, kwargs)
        key, at = self._key(ctx), self._at(ctx)

        cached = self.cache.get(key, at)
        if cached is abc._EMPTY:
            result = self._callback(*args, **kwargs)

            if self._when(ctx) and not self._unless(ctx):
                self._cache.put(key, at, result, self._ttl(ctx))

            return result
        return cached

    async def __acall__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        # Process caching async
        ctx = create_context_dict(self.argument_order, args, kwargs)
        key, at = self._key(ctx), self._at(ctx)

        cached = await self.cache.aget(key, at)
        if cached is abc._EMPTY:
            result = await self._callback(*args, **kwargs)

            if self._when(ctx) and not self._unless(ctx):
                await self._cache.aput(key, at, result, self._ttl(ctx))

            return result
        return cached
