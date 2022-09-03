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
import pysel

from cache import abc
from cache import cacheable
from cache import decorators
from cache import errors
from cache import manual
from cache import serde
from cache._setup import *
from cache.abc import *
from cache.cacheable import *
from cache.decorators import *
from cache.errors import *
from cache.serde import *

__all__ = [
    "Cache",
    "CacheNotSetUpError",
    "Cacheable",
    "Ex",
    "Serde",
    "Serializable",
    "abc",
    "able",
    "cacheable",
    "decorators",
    "errors",
    "evict",
    "manual",
    "serde",
    "setup",
]


__version__ = "0.0.1"

Ex = pysel.Expression
