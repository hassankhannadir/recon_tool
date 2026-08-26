from __future__ import annotations

import json

from recon.subdomains import enumerate_subdomains


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def test_enumerate_subdomains_collects_and_deduplicates(monkeypatch):
    def fake_urlopen(req, timeout=10.0):
        url = req.full_url
        if "crt.sh" in url:
            body = json.dumps([{"name_value": "www.example.com\napi.example.com"}]).encode()
        elif "hackertarget" in url:
            body = b"www.example.com\nmail.example.com\n"
        else:
            body = json.dumps({"Results": ["admin.example.com", "www.example.com"]}).encode()
        return FakeResponse(body)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = enumerate_subdomains("example.com")

    assert result["status"] == "ok"
    assert "www.example.com" in result["subdomains"]
    assert "api.example.com" in result["subdomains"]
