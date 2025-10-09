# Change Log

All notable changes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).



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
