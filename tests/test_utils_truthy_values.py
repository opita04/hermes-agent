"""Tests for shared utility helpers."""

import logging
import sys

from utils import configure_utf8_stdio, env_var_enabled, is_truthy_value


def test_is_truthy_value_accepts_common_truthy_strings():
    assert is_truthy_value("true") is True
    assert is_truthy_value(" YES ") is True
    assert is_truthy_value("on") is True
    assert is_truthy_value("1") is True


def test_is_truthy_value_respects_default_for_none():
    assert is_truthy_value(None, default=True) is True
    assert is_truthy_value(None, default=False) is False


def test_is_truthy_value_rejects_falsey_strings():
    assert is_truthy_value("false") is False
    assert is_truthy_value("0") is False
    assert is_truthy_value("off") is False


def test_env_var_enabled_uses_shared_truthy_rules(monkeypatch):
    monkeypatch.setenv("HERMES_TEST_BOOL", "YeS")
    assert env_var_enabled("HERMES_TEST_BOOL") is True

    monkeypatch.setenv("HERMES_TEST_BOOL", "no")
    assert env_var_enabled("HERMES_TEST_BOOL") is False


class _FakeTextStream:
    def __init__(self):
        self.encoding = "cp1252"
        self.errors = "strict"
        self.reconfigured = []
        self.writes = []

    def reconfigure(self, *, encoding=None, errors=None):
        self.reconfigured.append({"encoding": encoding, "errors": errors})
        if encoding is not None:
            self.encoding = encoding
        if errors is not None:
            self.errors = errors

    def write(self, data):
        if "✓" in data and self.encoding != "utf-8":
            raise UnicodeEncodeError("charmap", data, data.index("✓"), data.index("✓") + 1, "cannot encode")
        self.writes.append(data)
        return len(data)

    def flush(self):
        pass


def test_configure_utf8_stdio_reconfigures_console_streams(monkeypatch):
    stdout = _FakeTextStream()
    stderr = _FakeTextStream()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    configure_utf8_stdio()

    assert stdout.reconfigured == [{"encoding": "utf-8", "errors": "replace"}]
    assert stderr.reconfigured == [{"encoding": "utf-8", "errors": "replace"}]


def test_configure_utf8_stdio_allows_unicode_logging(monkeypatch):
    stream = _FakeTextStream()
    monkeypatch.setattr(sys, "stderr", stream)

    configure_utf8_stdio()

    logger = logging.getLogger("tests.configure_utf8_stdio")
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        logger.info("✓ connected → gateway")
    finally:
        logger.removeHandler(handler)

    assert any("✓ connected → gateway" in chunk for chunk in stream.writes)
