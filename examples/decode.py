import asyncio
import os

from dotenv import load_dotenv
from funasr_client import async_funasr_client


load_dotenv()
FUNASR_URI = os.getenv("FUNASR_URI", "wss://www.funasr.com:10096/")


async def with_decode():
    async with async_funasr_client(
        uri=FUNASR_URI,
        blocking=True,
        decode=True,
    ) as client:
        print("Connected to FunASR WebSocket server.")
        # send some audio data to the server
        with open("test.pcm", "rb") as f:
            await client.send(f.read())
        async for response in client.stream():
            # check your IDE to see the type of response: FunASRMessageDecoded
            print("Received decoded response:", response)


async def no_decode():
    async with async_funasr_client(
        uri=FUNASR_URI,
        blocking=True,
        decode=False,
    ) as client:
        print("Connected to FunASR WebSocket server.")
        # send some audio data to the server
        with open("test.pcm", "rb") as f:
            await client.send(f.read())
        async for response in client.stream():
            # check your IDE to see the type of response: FunASRMessage
            print("Received original response:", response)


if __name__ == "__main__":
    decode = True
    if decode:
        asyncio.run(with_decode())
    else:
        asyncio.run(no_decode())
