from __future__ import annotations

import socket

import pytest

from recon.banner_tech import detect_technologies, grab_banner, validate_target


class DummySocket:
    def __init__(self, banner=b"HTTP/1.1 200 OK\r\nServer: nginx\r\n"):
        self.banner = banner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def recv(self, size):
        return self.banner

    def settimeout(self, value):
        return None


class DummyResponse:
    def __init__(self):
        self.headers = {"Server": "nginx", "X-Powered-By": "Django"}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size):
        return b"<html><head><meta name=\"generator\" content=\"WordPress\"></head><body>hello</body></html>"


def test_validate_target_accepts_domain_and_ip():
    assert validate_target("google.com") == "google.com"
    assert validate_target("8.8.8.8") == "8.8.8.8"


def test_validate_target_rejects_invalid_target():
    with pytest.raises(ValueError):
        validate_target("not a valid target")


def test_grab_banner_reads_banner(monkeypatch):
    monkeypatch.setattr("socket.create_connection", lambda *args, **kwargs: DummySocket(b"220 mail.example.com ESMTP\r\n"))

    result = grab_banner("example.com", 25)

    assert result["status"] == "ok"
    assert "220 mail.example.com ESMTP" in result["banner"]


def test_grab_banner_handles_connection_errors(monkeypatch):
    def fake_create_connection(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("socket.create_connection", fake_create_connection)

    result = grab_banner("example.com", 22)

    assert result["status"] == "error"
    assert "connection refused" in result["error"].lower()


def test_detect_technologies_extracts_common_markers(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: DummyResponse())

    result = detect_technologies("https://example.com")

    assert result["status"] == "ok"
    assert "nginx" in result["technologies"]
    assert "django" in result["technologies"]
    assert "wordpress" in result["technologies"]
