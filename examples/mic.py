import asyncio
import os

from dotenv import load_dotenv
from funasr_client import async_mic_asr, mic_asr


load_dotenv()
FUNASR_URI = os.getenv("FUNASR_URI", "wss://www.funasr.com:10096/")


def mic():
    with mic_asr(FUNASR_URI) as msg_gen:
        print("Connected to FunASR WebSocket server; recording started.")
        for msg in msg_gen:
            print(f"Received decoded message: {msg}")
    print("Recording stopped.")


async def async_mic():
    async with async_mic_asr(FUNASR_URI) as msg_gen:
        print("Connected to FunASR WebSocket server; recording started.")
        async for msg in msg_gen:
            print(f"Received decoded message: {msg}")
    print("Recording stopped.")


if __name__ == "__main__":
    use_async = True
    if use_async:
        asyncio.run(async_mic())
    else:
        mic()
