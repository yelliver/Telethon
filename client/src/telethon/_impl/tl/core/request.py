import struct
from typing import Generic, TypeVar

Return = TypeVar("Return")


class Request(bytes, Generic[Return]):
    __slots__ = ()

    @property
    def constructor_id(self) -> int:
        try:
            cid = struct.unpack_from("<I", self)[0]
            assert isinstance(cid, int)
            return cid
        except struct.error:
            return 0

    def debug_name(self) -> str:
        return f"request#{self.constructor_id:x}"