# Python FunASR-Client

[![GitHub](https://img.shields.io/badge/github-FunASR--Client-blue?logo=github)](https://github.com/atomiechen/FunASR-Client)
[![PyPI](https://img.shields.io/pypi/v/funasr-client?logo=pypi&logoColor=white)](https://pypi.org/project/funasr-client/)


Really easy-to-use Python client for [FunASR][1] runtime server.

To deploy your own FunASR server, follow the [FunASR runtime guide][2], or use the improved startup scripts [here][3].

## Features

- ☯️ Both synchronous and asynchronous (`async`) support everywhere
- 💻 Both Command Line Interface (CLI) and Python API
- 🔤 Auto decoding of messages with real timestamps (`FunASRMessageDecoded`)
- 🎙️ Real-time audio recognition from a microphone (`mic_asr`)
- 🎵 File-based audio recognition (`file_asr`)


## Installation

Install directly from PyPI:

```bash
pip install funasr-client
```

If you want to use the microphone (`pyaudio`) for real-time recognition, install with:

```bash
pip install "funasr-client[mic]"
```

Install from github for the latest updates:

```bash
pip install "git+https://github.com/atomiechen/FunASR-Client.git"
```

## CLI

The CLI supports either real-time microphone input or file input for ASR, and outputs the recognized results in JSON (file) or JSON Lines (mic) format.


<details>
<summary>View all CLI options by running <code>funasr-client -h</code>.</summary>

```
usage: funasr-client [-h] [-v] [--mode MODE] [--chunk_size P C F] [--chunk_interval CHUNK_INTERVAL] [--audio_fs AUDIO_FS]
                     [--hotwords WORD:WEIGHT [WORD:WEIGHT ...]] [--no-itn] [--svs_lang SVS_LANG] [--no-svs_itn] [--async]
                     URI [FILE_PATH]

FunASR Client CLI v0.1.0. Use microphone for real-time recognition (needs pyaudio), or specify input audio file.

positional arguments:
  URI                   WebSocket URI to connect to the FunASR server.
  FILE_PATH             Optional input audio file path (suppress microphone). (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --mode MODE           offline, online, 2pass (default: 2pass)
  --chunk_size P C F    Chunk size: past, current, future. (default: [5, 10, 5])
  --chunk_interval CHUNK_INTERVAL
                        Chunk interval. (default: 10)
  --audio_fs AUDIO_FS   Audio sampling frequency. (default: 16000)
  --hotwords WORD:WEIGHT [WORD:WEIGHT ...]
                        Hotwords with weights, e.g., 'hello:10 world:5'. (default: [])
  --no-itn              Disable ITN (default: True)
  --svs_lang SVS_LANG   SVS language. (default: auto)
  --no-svs_itn          Disable SVS ITN (default: True)
  --async               Use asynchronous client. (default: False)
```

</details>

### Microphone Real-time ASR

Requires `pyaudio` for microphone support (install it using `pip install "funasr-client[mic]"`).

```sh
funasr-client ws://localhost:10096
```

### File ASR

```sh
funasr-client ws://localhost:10096 path/to/audio.wav
```


## Python API

Sync API (`funasr_client`):
```python
from funasr_client import funasr_client

with funasr_client("ws://localhost:10096") as client:
    @client.on_message
    def callback(msg):
        print("Received:", msg)
```

Async API (`async_funasr_client`):
```python
from funasr_client import async_funasr_client

async def main():
    async with async_funasr_client("ws://localhost:10096") as client:
        # NOTE: sync callback is also supported
        @client.on_message
        async def callback(msg):
            print("Received:", msg)
```

See scripts in the [examples directory](examples/) for real-world usage.

### Registering Callbacks in non-blocking mode

By default, the client runs in non-blocking mode, which allows you to continue using your program while waiting for ASR results. 
It starts a background loop in a thread (sync) or an async task (async) to handle incoming messages.

Two ways to register message callbacks (**both** sync and async are supported):
1. Using `@client.on_message` decorator (like shown above).
2. Passing `callback` handler to the constructor.
    ```python
    funasr_client(
        ...
        callback=lambda msg: print(msg)
    )
    ```

> [!NOTE]  
> Sync callback in async client will be run in a thread pool executor.


### Blocking Mode

To run in blocking mode (disable background loop), pass `blocking=True` to the client constructor.
It is your responsibility to call `client.stream()` or `client.recv()` to receive messages.

Use `client.stream()` (async) generator to receive messages in a loop:

```python
from funasr_client import funasr_client
with funasr_client("ws://localhost:10096", blocking=True) as client:
    for msg in client.stream():
        print("Received:", msg)
```

Or, use the low-level `client.recv()` method to receive messages one by one:

```python
from funasr_client import funasr_client
with funasr_client("ws://localhost:10096", blocking=True) as client:
    while True:
        msg = client.recv()
        if msg is None:
            break
        print("Received:", msg)
```


### Decoding Messages

By default, the client decodes response messages into `FunASRMessageDecoded` dicts, which parses `timestamps` JSON string into a list.
If `start_time` (int in ms) is provided to the client, `real_timestamp` and `real_stamp_sents` will be calculated and added to the decoded message.

To disable decoding, pass `decode=False` to the constructor to get original dict object.


### Microphone Real-time ASR

Open a microphone stream and get the stream of **decoded** messages (`mic_asr` / `async_mic_asr`):

```python
from funasr_client import mic_asr
with mic_asr("ws://localhost:10096") as msg_gen:
  for msg in msg_gen:
      print("Received:", msg)
```

### File ASR

Get the final result as a **merged decoded** message (`file_asr` / `async_file_asr`):

```python
from funasr_client import file_asr

result = file_asr("path/to/audio.wav", "ws://localhost:10096")
print(result)
```

Or, get the stream of **decoded or original** (depends on `decode` option) messages (`file_asr_stream` / `async_file_asr_stream`):

```python
from funasr_client import file_asr_stream

with file_asr_stream("path/to/audio.wav", "ws://localhost:10096") as msg_gen:
    for msg in msg_gen:
        print("Received:", msg)
```


[1]: https://github.com/modelscope/FunASR
[2]: https://github.com/modelscope/FunASR/blob/main/runtime/readme.md
[3]: https://gist.github.com/atomiechen/2deaf80dba21b4434ab21d6bf656fbca
