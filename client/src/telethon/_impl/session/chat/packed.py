import struct
from enum import Enum
from typing import Optional, Self

from telethon._impl.tl import abcs, types


class PackedType(Enum):
    # bits: zero, has-access-hash, channel, broadcast, group, chat, user, bot
    USER = 0b0000_0010
    BOT = 0b0000_0011
    CHAT = 0b0000_0100
    MEGAGROUP = 0b0010_1000
    BROADCAST = 0b0011_0000
    GIGAGROUP = 0b0011_1000


class PackedChat:
    __slots__ = ("ty", "id", "access_hash")

    def __init__(self, ty: PackedType, id: int, access_hash: Optional[int]) -> None:
        self.ty = ty
        self.id = id
        self.access_hash = access_hash

    def __bytes__(self) -> bytes:
        return struct.pack(
            "<Bqq",
            self.ty.value | (0 if self.access_hash is None else 0b0100_0000),
            self.id,
            self.access_hash or 0,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        ty_byte, id, access_hash = struct.unpack("<Bqq", data)
        has_hash = (ty_byte & 0b0100_0000) != 0
        ty = PackedType(ty_byte & 0b0011_1111)
        return cls(ty, id, access_hash if has_hash else None)

    def is_user(self) -> bool:
        return self.ty in (PackedType.USER, PackedType.BOT)

    def is_chat(self) -> bool:
        return self.ty in (PackedType.CHAT,)

    def is_channel(self) -> bool:
        return self.ty in (
            PackedType.MEGAGROUP,
            PackedType.BROADCAST,
            PackedType.GIGAGROUP,
        )

    def to_peer(self) -> abcs.Peer:
        if self.is_user():
            return types.PeerUser(user_id=self.id)
        elif self.is_chat():
            return types.PeerChat(chat_id=self.id)
        elif self.is_channel():
            return types.PeerChannel(channel_id=self.id)
        else:
            raise RuntimeError("unexpected case")

    def to_input_peer(self) -> abcs.InputPeer:
        if self.is_user():
            return types.InputPeerUser(
                user_id=self.id, access_hash=self.access_hash or 0
            )
        elif self.is_chat():
            return types.InputPeerChat(chat_id=self.id)
        elif self.is_channel():
            return types.InputPeerChannel(
                channel_id=self.id, access_hash=self.access_hash or 0
            )
        else:
            raise RuntimeError("unexpected case")

    def try_to_input_user(self) -> Optional[abcs.InputUser]:
        if self.is_user():
            return types.InputUser(user_id=self.id, access_hash=self.access_hash or 0)
        else:
            return None

    def to_input_user_lossy(self) -> abcs.InputUser:
        return self.try_to_input_user() or types.InputUser(user_id=0, access_hash=0)

    def try_to_chat_id(self) -> Optional[int]:
        return self.id if self.is_chat() else None

    def try_to_input_channel(self) -> Optional[abcs.InputChannel]:
        return (
            types.InputChannel(channel_id=self.id, access_hash=self.access_hash or 0)
            if self.is_channel()
            else None
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.ty == other.ty
            and self.id == other.id
            and self.access_hash == other.access_hash
        )

    def __str__(self) -> str:
        return f"PackedChat.{self.ty.name}({self.id})"