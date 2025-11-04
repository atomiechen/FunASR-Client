# Change Log

All notable changes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).



## [0.1.5] - 2025-11-04

### Changed

- All default values of `start_time` changed from `0` to `None` to better indicate its optional nature. `real_timestamp` and `real_stamp_sents` will only be included in decoded messages if `start_time` is explicitly provided.



## [0.1.4] - 2025-10-26

### Changed

- Make arguments of factory methods (`funasr_client` / `async_funasr_client` / `file_asr` / `file_asr_stream` / `async_file_asr` / `async_file_asr_stream` / `mic_asr` / `async_mic_asr`) optional, aligning with `BaseFunASRClient` defaults.

### Fixed

- `mic` as optional dependency installation instruction in `pyproject.toml`.



## [0.1.3] - 2025-10-10

### Added

- `base_client`: make more arguments optional (default by service)
- `file_asr`: add `start_time` parameter to file ASR functions

### Fixed

- README: fix example code of `file_asr_stream` (generator instead of with statement)



## [0.1.2] - 2025-08-05

### Fixed

- Fix unexpected keyword argument `ping_interval` in sync client. This occurs in older `websockets` version (`websockets<15.0`).


## [0.1.1] - 2025-08-05

### Added

- Support `python -m funasr_client` usage

### Fixed

- `mic_asr`
  - do not start the mic stream until connection is ready
  - do not throw input buffer overflow exception



## [0.1.0] - 2025-08-04

### Added

Initial features:

- Both synchronous and asynchronous (`async`) support everywhere
- Command Line Interface (CLI) and Python API
- Auto decoding of messages with real timestamps (`FunASRMessageDecoded`)
- Real-time audio recognition from a microphone (`mic_asr`)
- File-based audio recognition (`file_asr`)
