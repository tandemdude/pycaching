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
import functools
import inspect
import typing as t

import pysel
from typing_extensions import ParamSpec
from typing_extensions import TypeAlias

from cache import abc
from cache import cacheable

__all__ = ["able", "evict"]

T = t.TypeVar("T")
P = ParamSpec("P")
CallbackT: TypeAlias = t.Callable[[P], T]


def able(
    key: t.Union[str, pysel.Expression[t.Any]],
    at: t.Union[str, pysel.Expression[t.Any]],
    *,
    when: t.Optional[pysel.Expression[t.Any]] = None,
    unless: t.Optional[pysel.Expression[t.Any]] = None,
    ttl: t.Optional[t.Union[int, pysel.Expression[int]]] = None,
) -> t.Callable[[CallbackT], CallbackT]:
    def decorate(func: CallbackT) -> CallbackT:
        return cacheable.Cacheable(func, key, at, when, unless, ttl)

    return decorate


@t.overload
def evict(
    key: t.Union[str, pysel.Expression[t.Any]], at: t.Union[str, pysel.Expression[t.Any]]
) -> t.Callable[[CallbackT], CallbackT]:
    ...


@t.overload
def evict(key: t.Union[str, pysel.Expression[t.Any]], *, all: t.Literal[True]) -> t.Callable[[CallbackT], CallbackT]:
    ...


def evict(
    key: t.Union[str, pysel.Expression[t.Any]], at: t.Union[str, pysel.Expression[t.Any], None], *, all: bool = False
) -> t.Callable[[CallbackT], CallbackT]:
    def decorate(func: CallbackT) -> CallbackT:

        argument_order = {}
        for name, param in inspect.signature(func).parameters.items():
            argument_order[name] = param.default, param.kind

        @functools.wraps(func)
        def _wrapper(
            *args: P.args, __async: bool = False, __arg_info: t.Dict[str, t.Tuple[t.Any, t.Any]], **kwargs: P.kwargs
        ) -> T:
            method = getattr(abc.Cache.get_instance(), f"{'a' if __async else ''}evict")

            ctx = cacheable.create_context_dict(argument_order, args, kwargs)
            key_ = key if isinstance(key, str) else str(key.evaluate(ctx))
            at_ = at if at is None or isinstance(at, str) else str(at.evaluate(ctx))

            async def __wrapper() -> t.Any:
                await method(key_, at, all)
                return await func(*args, **kwargs)

            if __async:
                return __wrapper()

            method(key_, at_, all)
            return func(*args, **kwargs)

        return functools.partial(_wrapper, __async=inspect.iscoroutinefunction(func), __arg_info=argument_order)

    return decorate
