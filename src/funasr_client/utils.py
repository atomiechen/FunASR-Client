import asyncio
from functools import partial, wraps
import json
from typing import AsyncIterable, Awaitable, Callable, Iterable, TypeVar, Union

from typing_extensions import ParamSpec

from .types import (
    FunASRMessage,
    FunASRMessageDecoded,
    RecvMessageMode,
    FunASRMessageLike,
)


P = ParamSpec("P")
R = TypeVar("R")


def typed_params(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs):
    """Wraps a function to preserve its signature for type checking."""
    return args, kwargs


def sync_to_async(
    func: Callable[P, R],
) -> Union[Callable[P, Awaitable[R]], Callable[P, R]]:
    if asyncio.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs):
        loop = asyncio.get_running_loop()
        p_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, p_func)

    return wrapped


def decode_msg(msg: FunASRMessage, start_time: int = 0):
    decoded_msg: FunASRMessageDecoded = {**msg}
    if "timestamp" in msg:
        decoded_msg["timestamp"] = json.loads(msg["timestamp"])
    if "timestamp" in decoded_msg and start_time > 0:
        decoded_msg["real_timestamp"] = [
            (pair[0] + start_time, pair[1] + start_time)
            for pair in decoded_msg["timestamp"]
        ]
    if "stamp_sents" in decoded_msg and start_time > 0:
        decoded_msg["real_stamp_sents"] = [
            {
                **item,
                "start": item["start"] + start_time
                if item["start"] >= 0
                else item["start"],
                "end": item["end"] + start_time if item["end"] >= 0 else item["end"],
                "ts_list": [
                    (pair[0] + start_time, pair[1] + start_time)
                    for pair in item["ts_list"]
                ],
            }
            for item in decoded_msg["stamp_sents"]
        ]
    return decoded_msg


def create_decoded_msg(
    mode: RecvMessageMode = "2pass-offline",
    wav_name: str = "",
    text: str = "",
    is_final: bool = True,
) -> FunASRMessageDecoded:
    """
    Create a decoded message with default values.
    This is used to initialize the message structure before merging.
    """
    return {
        "mode": mode,
        "wav_name": wav_name,
        "text": text,
        "is_final": is_final,
        "timestamp": [],
        "stamp_sents": [],
        "real_timestamp": [],
        "real_stamp_sents": [],
    }


def extend_msg(merged: FunASRMessageDecoded, new_msg: FunASRMessageDecoded):
    """
    Extend the merged message with new_msg.
    """
    merged["text"] += new_msg["text"]
    if "timestamp" in new_msg:
        merged["timestamp"].extend(new_msg["timestamp"])  # type: ignore
    if "stamp_sents" in new_msg:
        merged["stamp_sents"].extend(new_msg["stamp_sents"])  # type: ignore
    if "real_timestamp" in new_msg:
        merged["real_timestamp"].extend(new_msg["real_timestamp"])  # type: ignore
    if "real_stamp_sents" in new_msg:
        merged["real_stamp_sents"].extend(new_msg["real_stamp_sents"])  # type: ignore
    if "wav_name" in new_msg:
        # always update wav_name to the latest one
        merged["wav_name"] = new_msg["wav_name"]


def msg_remove_empty(msg: FunASRMessageDecoded) -> FunASRMessageDecoded:
    """
    Remove empty fields from the message.
    """
    if not msg["timestamp"]:  # type: ignore
        del msg["timestamp"]
    if not msg["stamp_sents"]:  # type: ignore
        del msg["stamp_sents"]
    if not msg["real_timestamp"]:  # type: ignore
        del msg["real_timestamp"]
    if not msg["real_stamp_sents"]:  # type: ignore
        del msg["real_stamp_sents"]
    return msg


def merge_messages(messages: Iterable[FunASRMessageDecoded]):
    """
    Merge messages from an iterable into a single decoded message.
    Only `2pass-offline` (fixed results) messages are merged."""
    merged = create_decoded_msg()
    for msg in messages:
        if msg["mode"] == "2pass-offline":
            extend_msg(merged, msg)
    return msg_remove_empty(merged)


async def async_merge_messages(messages: AsyncIterable[FunASRMessageDecoded]):
    """
    Merge messages from an async iterable into a single decoded message.
    Only `2pass-offline` (fixed results) messages are merged.
    """
    merged = create_decoded_msg()
    async for msg in messages:
        if msg["mode"] == "2pass-offline":
            extend_msg(merged, msg)
    return msg_remove_empty(merged)


def is_final_msg(response: FunASRMessageLike) -> bool:
    """
    Check if the response indicates the end of a final result.
    """
    return response.get("is_final", False)
