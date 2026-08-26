from __future__ import annotations

import socket

import pytest

from recon.port_scanner import scan_ports, validate_target


def test_validate_target_accepts_domain_and_ip():
    assert validate_target("google.com") == "google.com"
    assert validate_target("8.8.8.8") == "8.8.8.8"


def test_validate_target_rejects_invalid_target():
    with pytest.raises(ValueError):
        validate_target("not a valid target")


def test_scan_ports_detects_open_ports(monkeypatch):
    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

    def fake_create_connection(addr, timeout=1.0):
        host, port = addr
        if port == 80:
            class FakeSocket:
                def __enter__(self):
                    return self

                def __exit__(self, *exc):
                    return False

            return FakeSocket()
        raise OSError("connection refused")

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr("socket.create_connection", fake_create_connection)

    result = scan_ports("example.com", ports=[80, 22], timeout=0.5)

    assert result["status"] == "ok"
    assert result["open_ports"] == [80]
    assert 22 in result["closed_ports"]


def test_scan_ports_handles_no_open_ports(monkeypatch):
    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

    def fake_create_connection(addr, timeout=1.0):
        raise OSError("connection refused")

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr("socket.create_connection", fake_create_connection)

    result = scan_ports("example.com", ports=[443], timeout=0.3)

    assert result["status"] == "no_open_ports"
    assert result["open_ports"] == []
    assert result["closed_ports"] == [443]
