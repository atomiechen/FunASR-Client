from typing import Any, Callable, Dict, Literal, Optional, Tuple, Union, overload

from .client import FunASRClient
from .async_client import AsyncFunASRClient
from .types import InitMessageMode, FunASRMessage, FunASRMessageDecoded


@overload
def funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessageDecoded], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[True] = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> FunASRClient[FunASRMessageDecoded]: ...


@overload
def funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[False],
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> FunASRClient[FunASRMessage]: ...


@overload
def funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> Union[FunASRClient[FunASRMessage], FunASRClient[FunASRMessageDecoded]]: ...


def funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback=None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
):
    """
    The factory function to create a `FunASRClient` instance with type hints.
    If `decode` is True, the client will return decoded messages.
    If `decode` is False, the client will return raw messages.
    The `start_time` parameter is used to adjust timestamps in decoded messages.
    """
    kwargs = {
        "uri": uri,
        "mode": mode,
        "chunk_size": chunk_size,
        "wav_name": wav_name,
        "wav_format": wav_format,
        "audio_fs": audio_fs,
        "hotwords": hotwords,
        "itn": itn,
        "svs_lang": svs_lang,
        "svs_itn": svs_itn,
        "callback": callback,
        "blocking": blocking,
        "auto_connect_in_with": auto_connect_in_with,
        "decode": decode,
        "start_time": start_time,
    }
    if decode:
        return FunASRClient[FunASRMessageDecoded](**kwargs)
    else:
        return FunASRClient[FunASRMessage](**kwargs)


@overload
def async_funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessageDecoded], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[True] = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> AsyncFunASRClient[FunASRMessageDecoded]: ...


@overload
def async_funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[False],
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> AsyncFunASRClient[FunASRMessage]: ...


@overload
def async_funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
) -> Union[
    AsyncFunASRClient[FunASRMessage], AsyncFunASRClient[FunASRMessageDecoded]
]: ...


def async_funasr_client(
    uri: str,
    mode: Optional[InitMessageMode] = None,
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: Optional[str] = None,
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Optional[Dict[str, int]] = None,
    itn: Optional[bool] = None,
    svs_lang: Optional[str] = None,
    svs_itn: Optional[bool] = None,
    *,
    callback=None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: Optional[int] = None,  # If specified, decoded messages will include real timestamps
):
    """
    The factory function to create a `AsyncFunASRClient` instance with type hints.
    If `decode` is True, the client will return decoded messages.
    If `decode` is False, the client will return raw messages.
    The `start_time` parameter is used to adjust timestamps in decoded messages.
    """
    kwargs = {
        "uri": uri,
        "mode": mode,
        "chunk_size": chunk_size,
        "wav_name": wav_name,
        "wav_format": wav_format,
        "audio_fs": audio_fs,
        "hotwords": hotwords,
        "itn": itn,
        "svs_lang": svs_lang,
        "svs_itn": svs_itn,
        "callback": callback,
        "blocking": blocking,
        "auto_connect_in_with": auto_connect_in_with,
        "decode": decode,
        "start_time": start_time,
    }
    if decode:
        return AsyncFunASRClient[FunASRMessageDecoded](**kwargs)
    else:
        return AsyncFunASRClient[FunASRMessage](**kwargs)
