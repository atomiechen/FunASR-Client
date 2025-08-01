import asyncio
from contextlib import asynccontextmanager, contextmanager
import threading
import time
from typing import Callable, Dict, Tuple

from funasr_client import (
    funasr_client,
    async_funasr_client,
    InitMessageMode,
    FunASRMessageDecoded,
    AsyncFunASRClient,
    FunASRClient,
)


@contextmanager
def open_mic(
    sample_rate: int,
    frames_per_buffer: int,
):
    # This is a runtime check to avoid import errors at the top level
    # since this module is optional and may not be installed.
    # If pyaudio is not installed, raise an ImportError with a helpful message.
    try:
        import pyaudio
    except ImportError:
        raise ImportError(
            "pyaudio is required for microphone input. "
            'Please install it using `pip install "funasr-client[mic]"`.'
        ) from None

    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=frames_per_buffer,
        )
        yield stream
    finally:
        # NOTE: Must terminate AFTER any reading of the stream,
        # otherwise stream.read() will block FOREVER
        p.terminate()


def send_mic(
    client: FunASRClient[FunASRMessageDecoded],
    event: threading.Event,
    read_func: Callable[[], bytes],
):
    while not event.is_set():
        data = read_func()
        client.send(data)


@contextmanager
def mic_asr(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: str = "microphone",
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
):
    """
    Real-time microphone ASR.
    Returns a generator that yields decoded messages.
    """
    frames_per_buffer = int(sample_rate * 60 * chunk_size[1] / chunk_interval / 1000)
    with open_mic(
        sample_rate=sample_rate,
        frames_per_buffer=frames_per_buffer,
    ) as stream:
        start_time = int(time.time() * 1000)
        with funasr_client(
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            wav_name=wav_name,
            audio_fs=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            blocking=True,
            decode=True,
            start_time=start_time,  # Set start time for decoding
        ) as client:
            stop_event = threading.Event()
            mic_thread = threading.Thread(
                target=lambda: send_mic(
                    client, stop_event, lambda: stream.read(frames_per_buffer)
                ),
                # daemon=True,
            )
            mic_thread.start()
            try:
                yield client.stream()
            finally:
                stop_event.set()
                mic_thread.join()


async def async_send_mic(
    client: AsyncFunASRClient[FunASRMessageDecoded],
    read_func: Callable[[], bytes],
):
    loop = asyncio.get_running_loop()
    while True:
        data = await loop.run_in_executor(None, read_func)
        await client.send(data)


@asynccontextmanager
async def async_mic_asr(
    uri: str,
    mode: InitMessageMode = "2pass",
    chunk_size: Tuple[int, int, int] = (5, 10, 5),
    chunk_interval: int = 10,
    wav_name: str = "microphone",
    sample_rate: int = 16000,
    hotwords: Dict[str, int] = {},
    itn: bool = True,
    svs_lang: str = "auto",
    svs_itn: bool = True,
):
    """
    Real-time microphone ASR.
    Returns an async generator that yields decoded messages.
    """
    frames_per_buffer = int(sample_rate * 60 * chunk_size[1] / chunk_interval / 1000)
    with open_mic(
        sample_rate=sample_rate,
        frames_per_buffer=frames_per_buffer,
    ) as stream:
        start_time = int(time.time() * 1000)
        async with async_funasr_client(
            uri=uri,
            mode=mode,
            chunk_size=chunk_size,
            wav_name=wav_name,
            audio_fs=sample_rate,
            hotwords=hotwords,
            itn=itn,
            svs_lang=svs_lang,
            svs_itn=svs_itn,
            blocking=True,
            decode=True,
            start_time=start_time,  # Set start time for decoding
        ) as client:
            lock = threading.Lock()

            def read_func():
                # Use lock to signal the reading is done
                with lock:
                    # Block until data is available. No other way to interrupt.
                    # NOTE: MUST not close the stream at this point,
                    # otherwise read() will block the thread forever.
                    return stream.read(frames_per_buffer)

            task = asyncio.create_task(async_send_mic(client, read_func))
            try:
                yield client.stream()
            finally:
                task.cancel()
                # Acquire the lock to ensure the stream is done reading
                # to prevent premature closing of stream (block forever)
                lock.acquire()
