from typing import Optional, Tuple, Any

from enum import Enum
from dataclasses import dataclass, asdict, fields
from bson.objectid import ObjectId


@dataclass
class CallbackData:
    def dump(self):
        data = asdict(self)
        data.pop("prefix")
        parts = [self.prefix, *data.values()]
        return "|".join(str(x) for x in parts)
    
    @classmethod
    def load(cls, data):
        parts = data.split("|")
        prefix = parts[0]
        if prefix != cls.prefix:
            raise ValueError(f"Invalid prefix: {prefix}")
        _fields = fields(cls)
        if len(parts) != len(_fields):
            raise ValueError(f"Invalid number of parts {len(parts)} in data {data} for {_fields}")
        _fields = [x for x in _fields if x.name != "prefix"]
        kwargs = {f.name: cls.string_to_field_value(p, f.type) for f, p in zip(_fields, parts[1:])}
        return cls(**kwargs)
    
    @classmethod
    def pattern(cls):
        return f"^{cls.prefix}"
    
    @staticmethod
    def string_to_field_value(line: str, field_type: type) -> Any:
        if field_type is bool:
            return line == "True"
        return field_type(line)


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    BANNED = "banned"

    def __str__(self):
        return self.value


@dataclass
class ChooseRoleData(CallbackData):
    role: Role
    user_id: int
    prefix: str = "choose_role"


@dataclass
class BarrierData(CallbackData):
    barrier_id: ObjectId
    prefix: str = "barrier"


@dataclass
class BarrierAccessData(CallbackData):
    barrier_id: ObjectId
    user_id: int
    prefix: str = "barrier_access"