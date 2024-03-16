from __future__ import annotations

from ..event import Event
from .combinators import Combinable


class Data(Combinable):
    """
    Filter by ``event.data`` using a full bytes match, used for events such as :class:`telethon.events.ButtonCallback`.

    It checks if ``event.data`` is equal to the data passed to the filter.

    :param data: Bytes to match data with.
    """

    __slots__ = ("_data",)

    def __init__(self, data: bytes) -> None:
        self._data = data

    def __call__(self, event: Event) -> bool:
        data = getattr(event, "data", None)
        return self._data == data if isinstance(data, bytes) else False
