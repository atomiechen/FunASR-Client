from typing import Any, Callable, Dict, Literal, Optional, Tuple, overload

from .client import FunASRClient
from .async_client import AsyncFunASRClient
from .types import InitMessageMode, FunASRMessage, FunASRMessageDecoded


@overload
def funasr_client(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback: Optional[Callable[[FunASRMessageDecoded], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[True] = True,
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
) -> FunASRClient[FunASRMessageDecoded]: ...


@overload
def funasr_client(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[False],
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
) -> FunASRClient[FunASRMessage]: ...


def funasr_client(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback=None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
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
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback: Optional[Callable[[FunASRMessageDecoded], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[True] = True,
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
) -> AsyncFunASRClient[FunASRMessageDecoded]: ...


@overload
def async_funasr_client(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback: Optional[Callable[[FunASRMessage], Any]] = None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: Literal[False],
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
) -> AsyncFunASRClient[FunASRMessage]: ...


def async_funasr_client(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    wav_name: str = "python-client",
    wav_format: Optional[str] = None,
    audio_fs: Optional[int] = None,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    callback=None,
    blocking: bool = False,  # If True, use stream() / recv() to get responses
    auto_connect_in_with: bool = True,
    decode: bool = True,
    start_time: int = 0,  # If > 0, decoded messages will include real timestamps
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
