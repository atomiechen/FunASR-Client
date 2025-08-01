from typing import List, Literal, Tuple, TypedDict, Union

from typing_extensions import NotRequired


InitMessageMode = Literal["offline", "online", "2pass"]
RecvMessageMode = Literal["2pass-online", "2pass-offline"]


class StampSent(TypedDict):
    """
    Represents a sentence with its start and end timestamps.
    """

    text_seg: str
    punc: str
    start: int
    end: int
    ts_list: List[Tuple[int, int]]


class FunASRMessage(TypedDict):
    """
    Received FunASR message.
    """

    mode: RecvMessageMode
    wav_name: str
    text: str
    is_final: bool
    timestamp: NotRequired[str]
    stamp_sents: NotRequired[List[StampSent]]


class FunASRMessageDecoded(TypedDict):
    """
    Decoded FunASR message with additional fields.
    """

    mode: RecvMessageMode
    wav_name: str
    text: str
    is_final: bool
    timestamp: NotRequired[List[Tuple[int, int]]]
    stamp_sents: NotRequired[List[StampSent]]
    real_timestamp: NotRequired[List[Tuple[int, int]]]
    real_stamp_sents: NotRequired[List[StampSent]]


FunASRMessageLike = Union[FunASRMessage, FunASRMessageDecoded]
