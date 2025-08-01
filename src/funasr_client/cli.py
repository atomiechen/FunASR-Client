import argparse

# python 3.8 or later
import asyncio
import importlib.metadata
import json

from funasr_client import file_asr, mic_asr, async_file_asr, async_mic_asr


def get_version():
    package_name = __name__.split(".")[0]
    return importlib.metadata.version(package_name)


def word_weight_pair(s: str):
    """
    Convert a string in the format "word:weight" to a (str, int) tuple.
    """
    if ":" not in s:
        raise ValueError(f"Invalid format: {s}. Expected 'word:weight'.")
    key, value = s.split(":", 1)
    return key.strip(), int(value.strip())


def main():
    """Main entry point for the funasr-client CLI."""
    parser = argparse.ArgumentParser(
        prog="funasr-client",
        description=f"FunASR Client CLI v{get_version()}. "
        "Use microphone for real-time recognition (needs pyaudio), or specify input audio file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version(),
    )
    parser.add_argument(
        "uri",
        metavar="URI",
        type=str,
        help="WebSocket URI to connect to the FunASR server.",
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        metavar="FILE_PATH",
        type=str,
        help="Optional input audio file path (suppress microphone).",
    )
    parser.add_argument(
        "--mode", type=str, default="2pass", help="offline, online, 2pass"
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        nargs=3,
        metavar=("P", "C", "F"),
        default=[5, 10, 5],
        help="Chunk size: past, current, future.",
    )
    parser.add_argument(
        "--chunk_interval", type=int, default=10, help="Chunk interval."
    )
    parser.add_argument(
        "--audio_fs", type=int, default=16000, help="Audio sampling frequency."
    )
    parser.add_argument(
        "--hotwords",
        type=word_weight_pair,
        metavar="WORD:WEIGHT",
        nargs="+",
        default=[],
        help="Hotwords with weights, e.g., 'hello:10 world:5'.",
    )
    parser.add_argument(
        "--no-itn", dest="itn", action="store_false", help="Disable ITN"
    )
    parser.add_argument(
        "--svs_lang",
        type=str,
        default="auto",
        help="SVS language.",
    )
    parser.add_argument(
        "--no-svs_itn", dest="svs_itn", action="store_false", help="Disable SVS ITN"
    )
    parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Use asynchronous client.",
    )
    args = parser.parse_args()

    kwargs = {
        "uri": args.uri,
        "mode": args.mode,
        "chunk_size": args.chunk_size,
        "chunk_interval": args.chunk_interval,
        "sample_rate": args.audio_fs,
        "hotwords": dict(args.hotwords),
        "itn": args.itn,
        "svs_lang": args.svs_lang,
        "svs_itn": args.svs_itn,
    }

    if args.file_path:
        if args.use_async:
            print(
                json.dumps(
                    asyncio.run(
                        async_file_asr(
                            file_path=args.file_path,
                            **kwargs,
                        )
                    ),
                    ensure_ascii=False,
                )
            )
        else:
            print(
                json.dumps(
                    file_asr(
                        file_path=args.file_path,
                        **kwargs,
                    ),
                    ensure_ascii=False,
                )
            )

    else:
        if args.use_async:

            async def mic_task():
                async with async_mic_asr(
                    **kwargs,
                ) as gen:
                    async for msg in gen:
                        print(json.dumps(msg, ensure_ascii=False))

            asyncio.run(mic_task())
        else:
            with mic_asr(
                **kwargs,
            ) as gen:
                for msg in gen:
                    print(json.dumps(msg, ensure_ascii=False))


if __name__ == "__main__":
    main()
