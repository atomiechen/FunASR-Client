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
    """
    Indicates the inference mode, divided into `2pass-online` for real-time recognition results and `2pass-offline` for 2-pass corrected recognition results.
    """

    wav_name: str
    """
    The name of the audio file to be transcribed.
    """

    text: str
    """
    The text output of speech recognition.
    """

    is_final: bool
    """
    Indicating the end of recognition.
    """

    timestamp: NotRequired[str]
    """
    If AM is a timestamp model, it will return this field, indicating the timestamp, in the format of `"[[100,200], [200,500]]"`.
    """

    stamp_sents: NotRequired[List[StampSent]]
    """
    If AM is a timestamp model, it will return this field, indicating the stamp_sents, in the format of `[{"text_seg":"正 是 因 为","punc":",","start":430,"end":1130,"ts_list":[[430,670],[670,810],[810,1030],[1030,1130]]}]`.
    """


class FunASRMessageDecoded(TypedDict):
    """
    Decoded FunASR message with additional fields.
    """

    mode: RecvMessageMode
    """
    Indicates the inference mode, divided into `2pass-online` for real-time recognition results and `2pass-offline` for 2-pass corrected recognition results.
    """

    wav_name: str
    """
    The name of the audio file to be transcribed.
    """

    text: str
    """
    The text output of speech recognition.
    """

    is_final: bool
    """
    Indicating the end of recognition.
    """

    timestamp: NotRequired[List[Tuple[int, int]]]
    """
    If AM is a timestamp model, it will return this field, indicating the timestamp, in the format of `[[100,200], [200,500]]` (ms)
    """

    stamp_sents: NotRequired[List[StampSent]]
    """
    If AM is a timestamp model, it will return this field, indicating the stamp_sents, in the format of `[{"text_seg":"正 是 因 为","punc":",","start":430,"end":1130,"ts_list":[[430,670],[670,810],[810,1030],[1030,1130]]}]`.
    """

    real_timestamp: NotRequired[List[Tuple[int, int]]]
    """
    Converts the `timestamp` to the local machine's real timestamps.
    """

    real_stamp_sents: NotRequired[List[StampSent]]
    """
    Converts the `stamp_sents` to the local machine's real timestamps.
    """


FunASRMessageLike = Union[FunASRMessage, FunASRMessageDecoded]
