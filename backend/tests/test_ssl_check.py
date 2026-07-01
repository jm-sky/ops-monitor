"""Tests for SSL certificate expiry check helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.modules.monitor.ssl_check import parse_cert, resolve_ssl_status


def _make_cert_der(not_valid_after: datetime) -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "example.com")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(days=1))
        .not_valid_after(not_valid_after)
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


def test_parse_cert_computes_days_remaining() -> None:
    der = _make_cert_der(datetime.now(UTC) + timedelta(days=45))
    data = parse_cert(der)

    assert data["days_remaining"] in (44, 45)
    assert "example.com" in data["subject"]
    assert "example.com" in data["issuer"]
    assert data["not_after"]
    assert data["not_before"]


def test_resolve_ssl_status_ok() -> None:
    assert resolve_ssl_status(days_remaining=60, warning_days=30) == "ok"


def test_resolve_ssl_status_expiring_soon_at_boundary() -> None:
    assert resolve_ssl_status(days_remaining=30, warning_days=30) == "expiring_soon"
    assert resolve_ssl_status(days_remaining=0, warning_days=30) == "expiring_soon"


def test_resolve_ssl_status_expired() -> None:
    assert resolve_ssl_status(days_remaining=-1, warning_days=30) == "expired"
