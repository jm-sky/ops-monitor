"""TLS trust for monitoring probes: certifi + optional extra CAs (e.g. an internal company root).

Scoped to probe requests only — Teams/Telegram/OAuth keep plain certifi. Extra CAs are read once
from every ``*.pem`` / ``*.crt`` file in ``MONITOR_EXTRA_CA_DIR``; a missing or empty directory
simply means "certifi only", so a host without internal CAs needs no setup at all.
"""

import logging
import ssl
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import certifi
from cryptography import x509

from app.core.config import settings

logger = logging.getLogger(__name__)

_CA_SUFFIXES = {".pem", ".crt"}


def probe_verify(verify_ssl: bool) -> ssl.SSLContext | bool:
    """Value for ``httpx.AsyncClient(verify=...)`` in monitoring probes."""
    return probe_ssl_context() if verify_ssl else False


@lru_cache(maxsize=1)
def probe_ssl_context() -> ssl.SSLContext:
    return build_ssl_context(Path(settings.monitor.extra_ca_dir), settings.monitor.ssl_expiry_warning_days)


def build_ssl_context(extra_ca_dir: Path, expiry_warning_days: int) -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=certifi.where())
    if not extra_ca_dir.is_dir():
        logger.info("Probe TLS: certifi only (no extra CA dir at %s)", extra_ca_dir)
        return ctx

    loaded = 0
    for path in sorted(p for p in extra_ca_dir.iterdir() if p.is_file() and p.suffix.lower() in _CA_SUFFIXES):
        try:
            data = path.read_bytes()
            certs = x509.load_pem_x509_certificates(data)
            ctx.load_verify_locations(cadata=data.decode("ascii"))
        except Exception as e:
            logger.error("Probe TLS: skipping unreadable CA file %s: %s", path, e)
            continue
        for cert in certs:
            loaded += 1
            _log_ca(path, cert, expiry_warning_days)

    logger.info("Probe TLS: certifi + %d extra CA cert(s) from %s", loaded, extra_ca_dir)
    return ctx


def _log_ca(path: Path, cert: x509.Certificate, expiry_warning_days: int) -> None:
    subject = cert.subject.rfc4514_string()
    days_left = (cert.not_valid_after_utc - datetime.now(UTC)).days
    if days_left < 0:
        logger.error("Probe TLS: extra CA %s (%s) EXPIRED %d day(s) ago", subject, path.name, -days_left)
    elif days_left <= expiry_warning_days:
        logger.warning("Probe TLS: extra CA %s (%s) expires in %d day(s)", subject, path.name, days_left)
    else:
        logger.info("Probe TLS: extra CA %s (%s), expires %s", subject, path.name, cert.not_valid_after_utc.date())
