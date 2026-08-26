from __future__ import annotations

import socket

import pytest

from recon.whois_dns import dns_lookup, validate_target, whois_lookup


def test_validate_target_accepts_domain_and_ip():
    assert validate_target("google.com") == "google.com"
    assert validate_target("8.8.8.8") == "8.8.8.8"


def test_validate_target_rejects_invalid_target():
    with pytest.raises(ValueError):
        validate_target("not a valid target")


def test_dns_lookup_returns_ip_records(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )

    result = dns_lookup("example.com")

    assert result["status"] == "ok"
    assert "93.184.216.34" in result["records"]["A"]


def test_whois_lookup_reads_whois_response(monkeypatch):
    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def sendall(self, payload):
            return None

        def recv(self, size):
            return b"Domain Name: example.com\nRegistrar: Example Registrar\n"

    monkeypatch.setattr("socket.create_connection", lambda *args, **kwargs: FakeSocket())

    result = whois_lookup("example.com")

    assert result["status"] == "ok"
    assert "example.com" in result["whois"].lower()
