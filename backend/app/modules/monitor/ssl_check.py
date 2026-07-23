"""TLS certificate expiry check — raw socket handshake, no HTTP request.

``SSLSocket.getpeercert()`` returns an empty dict when ``verify_mode`` is
``CERT_NONE`` (the certificate isn't validated), even though the handshake
itself succeeded — so we read the certificate in binary form and decode it
with ``cryptography`` instead of relying on ssl's built-in dict parsing.
"""

import asyncio
import socket
import ssl
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from cryptography import x509

CONNECT_TIMEOUT = 10.0
DEFAULT_PORT = 443


def _fetch_cert_der(connect_host: str, port: int, sni_host: str) -> bytes:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with socket.create_connection((connect_host, port), timeout=CONNECT_TIMEOUT) as sock:
        with ctx.wrap_socket(sock, server_hostname=sni_host) as tls_sock:
            der = tls_sock.getpeercert(binary_form=True)

    if not der:
        raise ValueError("No certificate presented by server")
    return der


def parse_cert(der: bytes) -> dict[str, Any]:
    """Decode a DER-encoded certificate into the raw_data shape stored in snapshots."""
    cert = x509.load_der_x509_certificate(der)
    not_after = cert.not_valid_after_utc
    not_before = cert.not_valid_before_utc
    days_remaining = (not_after - datetime.now(UTC)).days

    return {
        "not_after": not_after.isoformat(),
        "not_before": not_before.isoformat(),
        "issuer": cert.issuer.rfc4514_string(),
        "subject": cert.subject.rfc4514_string(),
        "days_remaining": days_remaining,
    }


async def fetch_cert(ssl_check_url: str, connect_ip: str | None = None) -> dict[str, Any]:
    """Perform a TLS handshake and read the peer certificate.

    Blocking socket/ssl work runs in a thread. SNI/hostname is taken from
    *ssl_check_url*; when *connect_ip* is set the TCP connection targets the
    IP instead, mirroring the health/system poll's IP-override pattern.
    """
    parsed = urlparse(ssl_check_url)
    host = parsed.hostname
    if not host:
        raise ValueError(f"Invalid ssl_check_url: {ssl_check_url!r}")
    port = parsed.port or DEFAULT_PORT
    connect_host = connect_ip or host

    der = await asyncio.to_thread(_fetch_cert_der, connect_host, port, host)
    data = parse_cert(der)
    data["hostname"] = host
    data["port"] = port
    return data


def resolve_ssl_status(days_remaining: int, warning_days: int) -> str:
    if days_remaining < 0:
        return "expired"
    if days_remaining <= warning_days:
        return "expiring_soon"
    return "ok"
