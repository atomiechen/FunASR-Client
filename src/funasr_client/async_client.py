"""
FunASR WebSocket Client (Asynchronous).

MIT License
2025 by Atomie CHEN (atomic_cwh@163.com)
"""

import asyncio
import json
import logging
from typing import Any, Callable, Optional, TypeVar, cast

from websockets import connect as ws_connect
from websockets.exceptions import ConnectionClosedOK

from .base_client import BaseFunASRClient
from .types import FunASRMessageLike
from .utils import sync_to_async, decode_msg, is_final_msg


module_logger = logging.getLogger(__name__)
module_logger.addHandler(logging.NullHandler())

MessageType = TypeVar("MessageType", bound=FunASRMessageLike)


class AsyncFunASRClient(BaseFunASRClient[MessageType]):
    def _additional_init(self):
        self._ws = None
        self._loop_task = None

    def _transform_callback(self, callback: Callable[[MessageType], Any]):
        return sync_to_async(callback)

    async def connect(self):
        """
        Connect to the FunASR WebSocket server.
        """
        if self._ws is not None:
            module_logger.warning("WebSocket connection already established.")
            return

        args, kwargs = self._get_connect_params()
        self._ws = await ws_connect(*args, **kwargs)

        if not self.blocking:
            self._final_event = asyncio.Event()
            self._loop_task = asyncio.create_task(self._loop_receive())

        await self._ws.send(self._get_init_msg())

    async def _close_ws(self):
        """
        Close the WebSocket connection.
        """
        if self._ws:
            await self._ws.close()
            self._ws = None
            module_logger.debug("_close_ws: WebSocket connection closed.")
        else:
            module_logger.debug("_close_ws: WebSocket connection is not established.")

    async def _loop_receive(self):
        """
        Loop to receive messages and trigger callback.
        This method runs in a separate task.
        """
        assert self._ws is not None, "loop: WebSocket connection is not established."
        try:
            module_logger.debug("Looping to receive messages...")
            while True:
                response_json = await self._recv()
                if response_json is None:
                    self._final_event.set()
                    break
                if self.callback:
                    await self.callback(response_json)
        except ConnectionClosedOK:
            pass
        except Exception as e:
            module_logger.error(f"Error in receive loop: {e}")
        finally:
            module_logger.debug("Receive loop ended.")

    async def signal_close(self):
        """
        Signal the server that the client is done sending audio data.
        """
        if self._ws is not None:
            await self._ws.send(self._close_msg)

    async def close(
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
            # Signal the server that the client is done sending audio data
            await self.signal_close()
            # If the loop task is running, wait for it to finish
            if self._loop_task:
                if not wait_for_final:
                    timeout = 0  # mean no wait
                # Wait for a short period to receive any final messages before closing
                try:
                    await asyncio.wait_for(self._final_event.wait(), timeout=timeout)
                    module_logger.debug(
                        "close: Loop task finished, closing connection."
                    )
                except (asyncio.TimeoutError, TimeoutError):
                    module_logger.debug(
                        "close: Timeout reached, closing connection without waiting for final messages."
                    )
        finally:
            # Always close the WebSocket connection
            await self._close_ws()
            if self._loop_task:
                try:
                    await self._loop_task
                except asyncio.CancelledError:
                    pass
                finally:
                    self._loop_task.cancel()
                    self._loop_task = None

    async def send(self, data: bytes):
        """
        Send binary audio data.
        """
        assert self._ws is not None, "send: WebSocket connection is not established."
        await self._ws.send(data)

    async def _recv(self, timeout: Optional[float] = None):
        if self._received_final:
            return None

        assert self._ws is not None, "recv: WebSocket connection is not established."
        try:
            message = await asyncio.wait_for(self._ws.recv(), timeout=timeout)
        except asyncio.TimeoutError as e:
            # convert asyncio.TimeoutError to TimeoutError for consistency
            raise TimeoutError() from e.__cause__
        response = json.loads(message)
        if self.decode:
            response = decode_msg(response, self.start_time)
        response = cast(MessageType, response)
        if is_final_msg(response):
            self._received_final = True
        return response

    async def recv(self, timeout: Optional[float] = None):
        """
        Receive a single message from the WebSocket (only in blocking mode).

        If ``timeout`` is :obj:`None`, block until a message is received. If
        ``timeout`` is set, wait up to ``timeout`` seconds for a message to be
        received and return it, else raise :exc:`TimeoutError`. If ``timeout``
        is ``0`` or negative, check if a message has been received already and
        return it, else raise :exc:`TimeoutError`.
        """
        assert not self._loop_task, "recv() is only available in blocking mode."
        return await self._recv(timeout=timeout)

    async def stream(self):
        """
        Generator that yields incoming responses (only in blocking mode).
        """
        assert not self._loop_task, "stream() is only available in blocking mode."

        if self._ws is not None:
            try:
                while True:
                    message = await self._recv()
                    if message is None:
                        break
                    yield message
            except ConnectionClosedOK:
                pass
        else:
            module_logger.debug("stream: WebSocket connection is not established.")

    async def __aenter__(self):
        if self.auto_connect_in_with:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
