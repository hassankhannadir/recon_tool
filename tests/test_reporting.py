from __future__ import annotations

from pathlib import Path

from recon.reporting import generate_html_report, generate_report, generate_report_file


def test_generate_report_includes_all_sections():
    results = {
        "target": "google.com",
        "timestamp": "2026-08-26 12:00:00 UTC",
        "ip_resolution": {"ipv4": ["172.217.3.110"], "ipv6": []},
        "whois": {"status": "ok", "data": {"domain": "google.com"}},
        "dns": {"records": {"A": ["172.217.3.110"], "MX": ["aspmx.l.google.com"], "TXT": ["google-site-verification"], "NS": ["ns1.google.com"]}},
        "subdomains": ["mail.google.com", "www.google.com"],
        "ports": [80, 443],
        "banners": {"80": "HTTP/1.1 200 OK"},
        "technologies": ["nginx", "cloudflare"],
    }

    report = generate_report(results)

    assert "Target: google.com" in report
    assert "IP Resolution:" in report
    assert "WHOIS:" in report
    assert "DNS:" in report
    assert "Subdomains:" in report
    assert "Open Ports:" in report
    assert "Detected Technologies:" in report
    assert "nginx" in report


def test_generate_html_report_contains_html_structure():
    results = {"target": "example.com", "technologies": ["apache"]}

    html = generate_html_report(results)

    assert "<html>" in html
    assert "Reconnaissance Report" in html
    assert "example.com" in html
    assert "apache" in html


def test_generate_report_file_writes_txt_output(tmp_path):
    output = tmp_path / "report.txt"
    results = {"target": "example.com", "technologies": ["django"]}

    content = generate_report_file(results, output)

    assert output.exists()
    assert "Target: example.com" in content
    assert "django" in output.read_text(encoding="utf-8")


def test_main_generates_report_for_target(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.argv", ["reporting.py", "--target", "google.com", "--report", str(tmp_path / "google_report.txt")])

    from recon.reporting import main

    exit_code = main()

    assert exit_code == 0
    assert (tmp_path / "google_report.txt").exists()
