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
import binascii
import pickle
import typing as t

import orjson

from cache import abc

__all__ = ["Serde"]


VERSION = "0"


class Serde:
    __slots__ = ("_class_cache",)

    def __init__(self) -> None:
        self._class_cache: t.Dict[str, t.Type[abc.Serializable]] = {}

    def get_cls_name(self, obj: abc.Serializable) -> str:
        name = obj.__class__.__module__ + "." + obj.__class__.__name__
        self._class_cache[name] = type(obj)
        return name

    def serialize_default(self, obj: t.Any) -> t.Dict[str, t.Any]:
        if not isinstance(obj, abc.Serializable):
            return {
                "raw": binascii.b2a_base64(pickle.dumps(obj), newline=False).decode("UTF-8"),
                "_cls": "_",
                "ver": VERSION,
                "type": "pickle",
            }
        return {"raw": obj.to_json(), "_cls": self.get_cls_name(obj), "type": "json"}

    def serialize(self, obj: t.Any) -> bytes:
        return orjson.dumps(obj, default=self.serialize_default)

    def deserialize_collection(self, item: t.Union[t.List[t.Any], t.Dict[str, t.Any]]) -> t.Any:
        if isinstance(item, dict):
            if "_cls" not in item:
                new_dict = {}
                for key, value in item.items():
                    new_dict[key] = self.deserialize_collection(value) if isinstance(value, (list, dict)) else value
                return new_dict

            if item["ver"] != VERSION:
                raise TypeError(f"Serde version mismatch. Expected {VERSION!r}, actual {item['ver']!r}")

            if item["type"] == "pickle":
                return pickle.loads(binascii.a2b_base64(item["raw"]))

            if (cls := item["_cls"]) not in self._class_cache:
                return abc._EMPTY

            return self._class_cache[cls].from_json(item["raw"])

        new_list = []
        for element in item:
            new_list.append(self.deserialize_collection(element) if isinstance(element, (list, dict)) else element)
        return new_list

    def deserialize(self, raw: bytes) -> t.Any:
        json = orjson.loads(raw)

        if isinstance(json, (list, dict)):
            return self.deserialize_collection(json)

        return json


default_serde = Serde()
serialize = default_serde.serialize
deserialize = default_serde.deserialize
