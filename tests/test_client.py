from funasr_client import funasr_client
import pytest


def test_callback_in_blocking():
    with pytest.raises(ValueError):
        with funasr_client(
            "<fake_uri>", blocking=True, callback=lambda msg: print(msg)
        ) as _client:
            pass
