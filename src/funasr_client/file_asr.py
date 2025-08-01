import asyncio
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
import sys
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    Literal,
    Optional,
    Tuple,
    Union,
    overload,
)

from funasr_client import (
    funasr_client,
    async_funasr_client,
    InitMessageMode,
    FunASRMessage,
    FunASRMessageDecoded,
    merge_messages,
    async_merge_messages,
)


if sys.version_info >= (3, 9):
    PathType = Union[str, PathLike[str]]
else:
    PathType = Union[str, PathLike]


@contextmanager
def open_file(
    file_path: PathType,
    chunk_size: Tuple[int, int, int],
    chunk_interval: int,
    sample_rate: int,
):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Input audio file does not exist: {file_path}")

    wav_format = None
    if file_path.suffix and file_path.suffix not in [".pcm", ".wav"]:
        wav_format = file_path.suffix[1:]

    if file_path.suffix == ".wav":
        import wave

        with wave.open(str(file_path), "rb") as wav_file:
            channels = wav_file.getnchannels()
            if channels != 1:
                raise ValueError(
                    f"Only mono audio is supported, but got {channels} channels."
                )
            sample_width = wav_file.getsampwidth()
            if sample_width != 2:
                raise ValueError(
                    f"Only 16-bit PCM audio is supported, but got {sample_width * 8}-bit audio."
                )

            # change sample rate according to the file
            sample_rate = wav_file.getframerate()
            stride_frames = int(
                60 * chunk_size[1] / chunk_interval / 1000 * sample_rate
            )
            yield (
                file_path.name,
                wav_format,
                sample_rate,
                lambda: wav_file.readframes(stride_frames),
            )
    else:
        stride = int(60 * chunk_size[1] / chunk_interval / 1000 * sample_rate * 2)
        with file_path.open("rb") as f:
            yield file_path.name, wav_format, sample_rate, lambda: f.read(stride)


@overload
def file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: Literal[True] = True,
) -> Generator[FunASRMessageDecoded, Any, None]: ...


@overload
def file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: Literal[False],
) -> Generator[FunASRMessage, Any, None]: ...


def file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: bool = True,
):
    """
    Recognize audio file and yield (decoded) messages.
    """
    with open_file(
        file_path=file_path,
        chunk_size=chunk_size,
        chunk_interval=chunk_interval,
        sample_rate=sample_rate,
    ) as (file_name, wav_format, sample_rate, read_func):
        if wav_name is None:
            wav_name = file_name
        with funasr_client(
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            wav_name=wav_name,
            wav_format=wav_format,
            audio_fs=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            blocking=True,
            decode=decode,
        ) as client:
            read_done = False
            while True:
                if not read_done:
                    data = read_func()
                    if data:
                        client.send(data)
                    else:
                        read_done = True
                        client.signal_close()

                try:
                    msg = client.recv(0.001)
                    if msg is None:
                        break
                    yield msg
                except TimeoutError:
                    continue


def file_asr(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
):
    """
    Recognize audio file and return the merged decoded message.
    """
    return merge_messages(
        file_asr_stream(
            file_path=file_path,
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            chunk_interval=chunk_interval,
            wav_name=wav_name,
            sample_rate=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            decode=True,
        )
    )


@overload
async def async_file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: Literal[True] = True,
) -> AsyncGenerator[FunASRMessageDecoded, Any]:
    yield ...


@overload
async def async_file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: Literal[False],
) -> AsyncGenerator[FunASRMessage, Any]:
    yield ...


async def async_file_asr_stream(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
    *,
    decode: bool = True,
):
    """
    Recognize audio file and yield (decoded) messages.

    This is an async version of `file_asr_stream`.
    """
    with open_file(
        file_path=file_path,
        chunk_size=chunk_size,
        chunk_interval=chunk_interval,
        sample_rate=sample_rate,
    ) as (file_name, wav_format, sample_rate, read_func):
        if wav_name is None:
            wav_name = file_name
        async with async_funasr_client(
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            wav_name=wav_name,
            wav_format=wav_format,
            audio_fs=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            blocking=True,
            decode=decode,
        ) as client:
            read_done = False
            loop = asyncio.get_running_loop()
            while True:
                if not read_done:
                    data = await loop.run_in_executor(None, read_func)
                    if data:
                        await client.send(data)
                    else:
                        read_done = True
                        await client.signal_close()

                try:
                    msg = await client.recv(0.001)
                    if msg is None:
                        break
                    yield msg
                except TimeoutError:
                    continue


async def async_file_asr(
    file_path: PathType,
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: Optional[str] = None,
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
):
    """
    Recognize audio file and return the merged decoded message.

    This is an async version of `file_asr`.
    """
    return await async_merge_messages(
        async_file_asr_stream(
            file_path=file_path,
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            chunk_interval=chunk_interval,
            wav_name=wav_name,
            sample_rate=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            decode=True,
        )
    )
