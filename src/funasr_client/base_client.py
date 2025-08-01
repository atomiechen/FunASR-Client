from abc import ABC
import json
import ssl
from typing import Any, Callable, Dict, Generic, Optional, Tuple, TypeVar
from urllib.parse import urlparse

from websockets.sync.client import connect as ws_connect

from .types import FunASRMessageLike, InitMessageMode
from .utils import typed_params


MessageType = TypeVar("MessageType", bound=FunASRMessageLike)


class BaseFunASRClient(ABC, Generic[MessageType]):
    _close_msg = json.dumps({"is_speaking": False})

    def __init__(
        self,
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
        callback: Optional[Callable[[MessageType], Any]] = None,
        blocking: bool = False,  # If True, use stream() / recv() to get responses
        auto_connect_in_with: bool = True,
        decode: bool = True,
        start_time: int = 0,  # If > 0, decoded messages will include real timestamps
    ):
        self.uri = uri
        self.mode = mode
        self.chunk_size = chunk_size
        self.hotwords = hotwords
        self.wav_name = wav_name
        self.wav_format = wav_format
        self.audio_fs = audio_fs
        self.itn = itn
        self.svs_lang = svs_lang
        self.svs_itn = svs_itn

        self.blocking = blocking
        self.auto_connect_in_with = auto_connect_in_with
        self.decode = decode
        self.start_time = start_time
        """Audio start time in milliseconds, used for real timestamps in decoded messages."""

        # register callback
        self.callback = None
        if callback is not None:
            self.on_message(callback)

        self._received_final = False

        # Subclass can implement this method to perform additional initialization
        self._additional_init()

    @property
    def received_final(self):
        """Whether a final message has been received. Read-only."""
        return self._received_final

    def _additional_init(self):
        """
        Additional initialization for subclasses.
        """
        pass

    def _transform_callback(self, callback: Callable[[MessageType], Any]):
        """
        Transform the callback to be compatible with the client.
        This can be overridden by subclasses if needed.
        """
        return callback

    def on_message(self, callback: Callable[[MessageType], Any]):
        """
        Decorator to register a callback function that will be called when a message is received.
        The callback function should accept a single argument, which is the received message.
        """
        if self.blocking:
            raise ValueError("callback is not supported in blocking mode.")
        self.callback = self._transform_callback(callback)
        return callback

    def _get_init_msg(self) -> str:
        """
        Initialize message to send to the server.
        """
        msg_dict = {
            "mode": self.mode,
            "is_speaking": True,
            "chunk_size": self.chunk_size,
            "wav_name": self.wav_name,
            "wav_format": self.wav_format,
            "audio_fs": self.audio_fs,
            "itn": self.itn,
            "hotwords": json.dumps(self.hotwords),
            "svs_lang": self.svs_lang,
            "svs_itn": self.svs_itn,
        }
        # filter out None values
        msg_dict = {k: v for k, v in msg_dict.items() if v is not None}
        # convert to JSON string
        return json.dumps(msg_dict)

    def _get_connect_params(self):
        """
        Parameters for connecting to the WebSocket server.
        """
        ssl_context = None
        # check if the URI is secure (wss)
        parsed_uri = urlparse(self.uri)
        if parsed_uri.scheme == "wss":
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        elif parsed_uri.scheme != "ws":
            raise ValueError(f"Unsupported URI scheme: {parsed_uri.scheme}")

        return typed_params(
            ws_connect,
            self.uri,
            ssl=ssl_context,
            subprotocols=["binary"],  # type: ignore
            ping_interval=None,
        )
