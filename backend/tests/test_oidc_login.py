"""Unit tests for optional OIDC login (e.g. Authentik): group gate, PKCE, hybrid admin."""

import base64
import hashlib
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest

from app.core.oauth import (
    OAuthAccessDeniedError,
    OIDCOAuthProvider,
    oidc_user_info_from_claims,
)
from app.modules.auth.models import User
from app.modules.auth.service import AuthService
from app.modules.auth.types.repository import UserRepositoryInterface

CLAIMS = {
    "sub": "abc-123",
    "email": "jan@example.com",
    "name": "Jan Example",
    "groups": ["ops-monitor"],
}


class TestClaimsMapping:
    def test_member_of_required_group_is_mapped(self) -> None:
        info = oidc_user_info_from_claims(CLAIMS, required_group="ops-monitor")

        assert info.provider == "oidc"
        assert info.providerId == "abc-123"
        assert info.email == "jan@example.com"
        assert info.name == "Jan Example"
        assert info.grantsAdmin is False

    def test_non_member_is_denied(self) -> None:
        with pytest.raises(OAuthAccessDeniedError):
            oidc_user_info_from_claims({**CLAIMS, "groups": ["other"]}, required_group="ops-monitor")

    def test_missing_groups_claim_is_denied(self) -> None:
        claims = {k: v for k, v in CLAIMS.items() if k != "groups"}
        with pytest.raises(OAuthAccessDeniedError):
            oidc_user_info_from_claims(claims, required_group="ops-monitor")

    def test_groups_as_single_string(self) -> None:
        info = oidc_user_info_from_claims({**CLAIMS, "groups": "ops-monitor"}, required_group="ops-monitor")
        assert info.email == "jan@example.com"

    def test_admin_group_grants_admin(self) -> None:
        info = oidc_user_info_from_claims(
            {**CLAIMS, "groups": ["ops-monitor", "ops-monitor-admin"]},
            required_group="ops-monitor",
            admin_group="ops-monitor-admin",
        )
        assert info.grantsAdmin is True

    def test_empty_admin_group_never_grants_admin(self) -> None:
        info = oidc_user_info_from_claims({**CLAIMS, "groups": ["ops-monitor", ""]}, required_group="ops-monitor", admin_group="")
        assert info.grantsAdmin is False

    @pytest.mark.parametrize("missing", ["sub", "email"])
    def test_missing_identity_claims_fail(self, missing: str) -> None:
        claims = {k: v for k, v in CLAIMS.items() if k != missing}
        with pytest.raises(ValueError):
            oidc_user_info_from_claims(claims, required_group="ops-monitor")


class TestPkce:
    def test_verifier_is_deterministic_per_state_and_rfc7636_sized(self) -> None:
        verifier = OIDCOAuthProvider.code_verifier("state-1")

        assert verifier == OIDCOAuthProvider.code_verifier("state-1")
        assert verifier != OIDCOAuthProvider.code_verifier("state-2")
        assert 43 <= len(verifier) <= 128

    def test_challenge_is_s256_of_verifier(self) -> None:
        verifier = OIDCOAuthProvider.code_verifier("state-1")
        expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

        assert OIDCOAuthProvider.code_challenge("state-1") == expected

    @pytest.mark.asyncio
    async def test_authorization_url_carries_state_and_challenge(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.core.config import settings

        for field, value in {
            "oidc_discovery_url": "https://idp.example/.well-known/openid-configuration",
            "oidc_client_id": "client",
            "oidc_client_secret": "secret",
            "oidc_redirect_uri": "https://app.example/auth/callback/oidc",
            "oidc_required_group": "ops-monitor",
        }.items():
            monkeypatch.setattr(settings.oauth, field, value)

        provider = OIDCOAuthProvider()
        provider._metadata = {
            "authorization_endpoint": "https://idp.example/authorize/",
            "token_endpoint": "https://idp.example/token/",
            "userinfo_endpoint": "https://idp.example/userinfo/",
        }

        url = await provider.get_authorization_url("state-1")
        query = parse_qs(urlparse(url).query)

        assert url.startswith("https://idp.example/authorize/?")
        assert query["state"] == ["state-1"]
        assert query["code_challenge"] == [OIDCOAuthProvider.code_challenge("state-1")]
        assert query["code_challenge_method"] == ["S256"]
        assert query["redirect_uri"] == ["https://app.example/auth/callback/oidc"]

    @pytest.mark.asyncio
    async def test_unconfigured_provider_refuses(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.core.config import settings

        monkeypatch.setattr(settings.oauth, "oidc_discovery_url", "")
        with pytest.raises(ValueError, match="not configured"):
            await OIDCOAuthProvider().get_authorization_url("state-1")


def _user(is_admin: bool) -> User:
    return User(
        id="user-1",
        email="jan@example.com",
        name="Jan",
        hashedPassword=None,
        isActive=True,
        isEmailVerified=True,
        isAdmin=is_admin,
        createdAt=datetime.now(UTC),
    )


class TestHybridAdmin:
    @pytest.fixture
    def repo(self) -> AsyncMock:
        repo = AsyncMock(spec=UserRepositoryInterface)
        repo.update_user.side_effect = lambda user: user
        repo.create_oauth_connection.return_value = None
        return repo

    @pytest.mark.asyncio
    async def test_admin_group_promotes_existing_user(self, repo: AsyncMock) -> None:
        repo.get_user_by_oauth_provider.return_value = _user(is_admin=False)

        user = await AuthService(user_repository=repo)._resolve_oauth_user("oidc", {"email": "jan@example.com", "providerId": "abc-123", "grantsAdmin": True})

        assert user.isAdmin is True
        repo.update_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_missing_admin_group_never_demotes_local_admin(self, repo: AsyncMock) -> None:
        repo.get_user_by_oauth_provider.return_value = _user(is_admin=True)

        user = await AuthService(user_repository=repo)._resolve_oauth_user("oidc", {"email": "jan@example.com", "providerId": "abc-123", "grantsAdmin": False})

        assert user.isAdmin is True
        repo.update_user.assert_not_awaited()
