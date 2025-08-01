"""
FunASR WebSocket Client (Synchronous).

MIT License
2025 by Atomie CHEN (atomic_cwh@163.com)
"""

import json
import logging
import threading
from typing import Optional, TypeVar, cast

from websockets.sync.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedOK

from .base_client import BaseFunASRClient
from .types import FunASRMessageLike
from .utils import decode_msg, is_final_msg


module_logger = logging.getLogger(__name__)
module_logger.addHandler(logging.NullHandler())

MessageType = TypeVar("MessageType", bound=FunASRMessageLike)


class FunASRClient(BaseFunASRClient[MessageType]):
    def _additional_init(self):
        self._ws = None
        self._loop_thread = None

    def connect(self):
        """
        Connect to the FunASR WebSocket server.
        """
        if self._ws is not None:
            module_logger.warning("WebSocket connection already established.")
            return

        args, kwargs = self._get_connect_params()
        self._ws = ws_connect(*args, **kwargs)

        if not self.blocking:
            self._final_event = threading.Event()
            self._loop_thread = threading.Thread(
                target=self._loop_receive,
                # daemon=True,
            )
            self._loop_thread.start()

        self._ws.send(self._get_init_msg())

    def _close_ws(self):
        """
        Close the WebSocket connection.
        """
        if self._ws:
            self._ws.close()
            self._ws = None
            module_logger.debug("_close_ws: WebSocket connection closed.")
        else:
            module_logger.debug("_close_ws: WebSocket connection is not established.")

    def _loop_receive(self):
        """
        Loop to receive messages and trigger callback.
        This method runs in a separate thread.
        """
        assert self._ws is not None, "WebSocket connection not established."
        try:
            module_logger.debug("Looping to receive messages...")
            while True:
                response_json = self._recv()
                if response_json is None:
                    self._final_event.set()
                    break
                if self.callback:
                    self.callback(response_json)
        except ConnectionClosedOK:
            pass
        except Exception as e:
            module_logger.error(f"Error in receive loop: {e}")
        finally:
            module_logger.debug("Receive loop ended.")

    def signal_close(self):
        """
        Signal the server that the client is done sending audio data.
        """
        if self._ws is not None:
            self._ws.send(self._close_msg)

    def close(
        self,
        wait_for_final: bool = True,
        timeout: Optional[float] = None,  # None means wait indefinitely
    ):
        """
        Send a close signal to the server and close the WebSocket connection.
        If wait_for_final is True, it will wait for the final message to be received.
        If timeout is specified, it will wait for that duration before closing.
        If timeout is None, it will wait indefinitely.
        """
        try:
            self.signal_close()
            if self._loop_thread and wait_for_final:
                if not self._final_event.wait(timeout=timeout):
                    module_logger.warning(
                        "Timeout reached, closing connection without waiting for final messages."
                    )
        finally:
            # this will also raise ConnectionClosedOK to close the loop thread
            self._close_ws()
            if self._loop_thread:
                self._loop_thread.join()
                self._loop_thread = None

    def send(self, data: bytes):
        """
        Send binary audio data.
        """
        assert self._ws is not None, "WebSocket connection not established."
        self._ws.send(data)

    def _recv(self, timeout: Optional[float] = None):
        if self._received_final:
            return None

        assert self._ws is not None, "WebSocket connection not established."
        message = self._ws.recv(timeout=timeout)
        response = json.loads(message)
        if self.decode:
            response = decode_msg(response, self.start_time)
        response = cast(MessageType, response)
        if is_final_msg(response):
            self._received_final = True
        return response

    def recv(self, timeout: Optional[float] = None):
        """
        Receive a single message from the WebSocket (only in blocking mode).

        If ``timeout`` is :obj:`None`, block until a message is received. If
        ``timeout`` is set, wait up to ``timeout`` seconds for a message to be
        received and return it, else raise :exc:`TimeoutError`. If ``timeout``
        is ``0`` or negative, check if a message has been received already and
        return it, else raise :exc:`TimeoutError`.
        """
        assert not self._loop_thread, "recv() is only available in blocking mode."
        return self._recv(timeout=timeout)

    def stream(self):
        """
        Generator that yields incoming responses (only in blocking mode).
        """
        assert not self._loop_thread, "stream() is only available in blocking mode."

        if self._ws is not None:
            try:
                while True:
                    message = self._recv()
                    if message is None:
                        break
                    yield message
            except ConnectionClosedOK:
                pass
        else:
            module_logger.debug("stream: WebSocket connection is not established.")

    def __enter__(self):
        if self.auto_connect_in_with:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
