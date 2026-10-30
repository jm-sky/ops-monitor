"""Tests for probe TLS trust (certifi + extra CA directory)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.modules.monitor.tls import build_ssl_context, probe_verify


def _make_ca_pem(cn: str, not_valid_after: datetime) -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(days=1))
        .not_valid_after(not_valid_after)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM)


def _subjects(ctx: object) -> set[str]:
    return {dict(rdn[0] for rdn in c["subject"]).get("commonName", "") for c in ctx.get_ca_certs()}  # type: ignore[attr-defined]


def test_missing_dir_falls_back_to_certifi(tmp_path: Path) -> None:
    ctx = build_ssl_context(tmp_path / "nope", 30)
    assert len(ctx.get_ca_certs()) > 50


def test_loads_pem_and_crt_and_skips_garbage(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    far = datetime.now(UTC) + timedelta(days=365)
    (tmp_path / "a.pem").write_bytes(_make_ca_pem("Internal A", far))
    (tmp_path / "b.crt").write_bytes(_make_ca_pem("Internal B", far))
    (tmp_path / "broken.pem").write_text("not a cert")
    (tmp_path / "ignored.txt").write_bytes(_make_ca_pem("Ignored", far))

    with caplog.at_level(logging.INFO, logger="app.modules.monitor.tls"):
        ctx = build_ssl_context(tmp_path, 30)

    subjects = _subjects(ctx)
    assert {"Internal A", "Internal B"} <= subjects
    assert "Ignored" not in subjects
    assert "broken.pem" in caplog.text
    assert "2 extra CA cert(s)" in caplog.text


def test_warns_on_ca_close_to_expiry(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    (tmp_path / "soon.pem").write_bytes(_make_ca_pem("Soon", datetime.now(UTC) + timedelta(days=10)))

    with caplog.at_level(logging.WARNING, logger="app.modules.monitor.tls"):
        build_ssl_context(tmp_path, 30)

    assert "expires in" in caplog.text


def test_probe_verify_disabled_returns_false() -> None:
    assert probe_verify(False) is False
