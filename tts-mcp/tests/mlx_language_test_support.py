from __future__ import annotations

from pathlib import Path
import sys
import types

import pytest

from tts_mcp.platform import HostInfo
import tts_mcp.runner as runner


_MIN_VALID_WAV_BYTES = b"RIFF" + (b"\x00" * 60)


@pytest.fixture(autouse=True)
def _mock_runtime_version_check(monkeypatch) -> None:
    monkeypatch.setattr(
        runner,
        "check_backend_runtime_version",
        lambda **_: {
            "status": "latest",
            "local_version": "1.0.0",
            "latest_version": "1.0.0",
            "message": "runtime is up to date",
        },
    )


def _mlx_host() -> HostInfo:
    return HostInfo(
        system="Darwin",
        machine="arm64",
        is_macos_arm64=True,
        is_linux=False,
        has_nvidia=False,
    )


class _FakeNumpyArray:
    def __init__(self, values: list[float]) -> None:
        self._values = values

    def __mul__(self, factor: float) -> "_FakeNumpyArray":
        return _FakeNumpyArray([value * factor for value in self._values])

    __rmul__ = __mul__

    def astype(self, _dtype) -> "_FakeNumpyArray":
        return self

    def tobytes(self) -> bytes:
        return b"\x00\x00" * len(self._values)


def _install_fake_numpy(monkeypatch) -> None:
    fake_numpy = types.SimpleNamespace(
        float32="float32",
        int16="int16",
        asarray=lambda values, dtype=None: _FakeNumpyArray(list(values)),
        clip=lambda values, _lo, _hi: values,
    )
    monkeypatch.setitem(sys.modules, "numpy", fake_numpy)
