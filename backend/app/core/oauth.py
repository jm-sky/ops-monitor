"""OAuth authentication service for multiple providers."""

import base64
import hashlib
import hmac
import logging
import secrets
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuthAccessDeniedError(ValueError):
    """The identity provider authenticated the user, but this app must not let them in."""


class OAuthUserInfo(BaseModel):
    """Standardized OAuth user info (camelCase for API consistency)."""

    provider: str
    providerId: str
    email: str
    name: str | None = None
    avatarUrl: str | None = None
    # Provider asserts admin rights (OIDC admin group). Only ever grants is_admin, never revokes it.
    grantsAdmin: bool = False


class OAuthTokenResponse(BaseModel):
    """OAuth token exchange response."""

    accessToken: str
    tokenType: str
    scope: str | None = None
    refreshToken: str | None = None


class OAuthProvider(ABC):
    """Abstract base class for OAuth providers."""

    @abstractmethod
    async def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token."""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information using access token."""
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider implementation."""

    def __init__(self) -> None:
        self.client_id = settings.oauth.google_client_id
        self.client_secret = settings.oauth.google_client_secret
        self.redirect_uri = settings.oauth.google_redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_api_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email profile",
            "state": state,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "select_account",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        """Exchange Google authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(f"Google OAuth error: {data.get('error_description', data['error'])}")

            return OAuthTokenResponse(
                accessToken=data["access_token"],
                tokenType=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                refreshToken=data.get("refresh_token"),
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get Google user information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            user_data = response.json()

            if not user_data.get("verified_email", False):
                raise ValueError("Google account email is not verified")

            return OAuthUserInfo(
                provider="google",
                providerId=str(user_data["id"]),
                email=user_data["email"],
                name=user_data.get("name"),
                avatarUrl=user_data.get("picture"),
            )


class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth provider implementation."""

    def __init__(self) -> None:
        self.client_id = settings.oauth.facebook_client_id
        self.client_secret = settings.oauth.facebook_client_secret
        self.redirect_uri = settings.oauth.facebook_redirect_uri
        self.auth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.user_api_url = "https://graph.facebook.com/v18.0/me"

    async def get_authorization_url(self, state: str) -> str:
        """Generate Facebook OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email public_profile",
            "state": state,
            "response_type": "code",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        """Exchange Facebook authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.token_url,
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_info = data.get("error", {})
                error_message = error_info.get("message", error_info.get("error_description", "Unknown error"))
                raise ValueError(f"Facebook OAuth error: {error_message}")

            return OAuthTokenResponse(
                accessToken=data["access_token"],
                tokenType=data.get("token_type", "Bearer"),
                scope=None,  # Facebook doesn't return scope in token response
                refreshToken=None,  # Facebook doesn't provide refresh tokens
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get Facebook user information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_api_url,
                params={
                    "fields": "id,name,email,picture",
                    "access_token": access_token,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            user_data = response.json()

            if "error" in user_data:
                error_info = user_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                raise ValueError(f"Facebook API error: {error_message}")

            # Get picture URL if available
            avatar_url = None
            if "picture" in user_data and "data" in user_data["picture"]:
                avatar_url = user_data["picture"]["data"].get("url")

            return OAuthUserInfo(
                provider="facebook",
                providerId=str(user_data["id"]),
                email=user_data.get("email", ""),
                name=user_data.get("name"),
                avatarUrl=avatar_url,
            )


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth App provider for login."""

    def __init__(self) -> None:
        self.client_id = settings.oauth.github_client_id
        self.client_secret = settings.oauth.github_client_secret
        self.redirect_uri = settings.oauth.github_redirect_uri
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_api_url = "https://api.github.com/user"
        self.emails_api_url = "https://api.github.com/user/emails"

    def _api_headers(self, access_token: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{settings.app.name}-login",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    async def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": "read:user user:email",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers=self._api_headers(),
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(data.get("error_description") or data.get("error", "GitHub OAuth error"))

            return OAuthTokenResponse(
                accessToken=data["access_token"],
                tokenType=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                refreshToken=data.get("refresh_token"),
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_api_url,
                headers=self._api_headers(access_token),
                timeout=15.0,
            )
            response.raise_for_status()
            user_data = response.json()

            email = user_data.get("email")
            if not email:
                emails_response = await client.get(
                    self.emails_api_url,
                    headers=self._api_headers(access_token),
                    timeout=15.0,
                )
                emails_response.raise_for_status()
                for entry in emails_response.json():
                    if entry.get("primary") and entry.get("verified"):
                        email = entry.get("email")
                        break
                if not email:
                    for entry in emails_response.json():
                        if entry.get("verified"):
                            email = entry.get("email")
                            break

            if not email:
                raise ValueError("GitHub account email is required — enable user:email scope " "or make your email public on GitHub")

            return OAuthUserInfo(
                provider="github",
                providerId=str(user_data["id"]),
                email=email,
                name=user_data.get("name") or user_data.get("login"),
                avatarUrl=user_data.get("avatar_url"),
            )


def _claim_groups(value: object) -> list[str]:
    """The `groups` claim may be a list, a single string, or missing."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple):
        return [g for g in value if isinstance(g, str)]
    return []


def oidc_user_info_from_claims(claims: dict[str, Any], required_group: str, admin_group: str = "") -> OAuthUserInfo:
    """
    Map OIDC userinfo claims to OAuthUserInfo, enforcing group membership.

    Raises:
        OAuthAccessDeniedError: user is not a member of `required_group`
        ValueError: claims lack a subject or e-mail
    """
    subject = claims.get("sub")
    email = claims.get("email")
    if not isinstance(subject, str) or not subject:
        raise ValueError("Identity provider did not return a subject (sub)")
    if not isinstance(email, str) or not email:
        raise ValueError("Identity provider did not return an e-mail address")

    groups = _claim_groups(claims.get("groups"))
    # The IdP should already restrict the application to this group; this is the second lock.
    if required_group not in groups:
        logger.warning("OIDC login denied: %s is not in the required group", email)
        raise OAuthAccessDeniedError("You do not have access to this application. Ask an administrator to add you.")

    name = claims.get("name") or claims.get("preferred_username")
    avatar = claims.get("picture")
    return OAuthUserInfo(
        provider="oidc",
        providerId=subject,
        email=email,
        name=name if isinstance(name, str) else None,
        avatarUrl=avatar if isinstance(avatar, str) else None,
        grantsAdmin=bool(admin_group) and admin_group in groups,
    )


class OIDCOAuthProvider(OAuthProvider):
    """
    Generic OpenID Connect provider (e.g. Authentik), confidential client with PKCE (S256).

    Endpoints come from the discovery document, fetched once on first use. The PKCE
    code_verifier is derived from the single-use, server-verified `state` with an HMAC
    keyed by SECRET_KEY, so nothing extra has to be stored between redirect and callback.
    """

    def __init__(self) -> None:
        self.discovery_url = settings.oauth.oidc_discovery_url
        self.client_id = settings.oauth.oidc_client_id
        self.client_secret = settings.oauth.oidc_client_secret
        self.redirect_uri = settings.oauth.oidc_redirect_uri
        self.scopes = settings.oauth.oidc_scopes
        self.required_group = settings.oauth.oidc_required_group
        self.admin_group = settings.oauth.oidc_admin_group
        self._metadata: dict[str, Any] | None = None

    def _ensure_enabled(self) -> None:
        if not settings.oauth.oidc_enabled:
            raise ValueError("OIDC login is not configured")

    async def _get_metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.discovery_url, timeout=10.0)
                response.raise_for_status()
                metadata = response.json()
            for key in ("authorization_endpoint", "token_endpoint", "userinfo_endpoint"):
                if not metadata.get(key):
                    raise ValueError(f"OIDC discovery document has no {key}")
            self._metadata = metadata
        return self._metadata

    @staticmethod
    def code_verifier(state: str) -> str:
        """PKCE verifier bound to `state` (43 chars, RFC 7636 alphabet)."""
        digest = hmac.new(settings.security.secret_key.encode(), f"oidc-pkce:{state}".encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    @classmethod
    def code_challenge(cls, state: str) -> str:
        digest = hashlib.sha256(cls.code_verifier(state).encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    async def get_authorization_url(self, state: str) -> str:
        self._ensure_enabled()
        metadata = await self._get_metadata()
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
            "state": state,
            "code_challenge": self.code_challenge(state),
            "code_challenge_method": "S256",
        }
        return f"{metadata['authorization_endpoint']}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthTokenResponse:
        self._ensure_enabled()
        metadata = await self._get_metadata()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                metadata["token_endpoint"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "code_verifier": self.code_verifier(state),
                },
                auth=(self.client_id, self.client_secret),
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            data = response.json() if response.content else {}
            if response.is_error or "error" in data:
                raise ValueError(f"OIDC token error: {data.get('error_description') or data.get('error') or response.status_code}")

            return OAuthTokenResponse(
                accessToken=data["access_token"],
                tokenType=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                refreshToken=data.get("refresh_token"),
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        self._ensure_enabled()
        metadata = await self._get_metadata()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metadata["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            claims = response.json()

        return oidc_user_info_from_claims(claims, self.required_group, self.admin_group)


class OAuthService:
    """Central OAuth service for managing multiple providers."""

    def __init__(self) -> None:
        self.providers: dict[str, OAuthProvider] = {
            "google": GoogleOAuthProvider(),
            "facebook": FacebookOAuthProvider(),
            "github": GitHubOAuthProvider(),
            "oidc": OIDCOAuthProvider(),
        }

    def get_provider(self, provider_name: str) -> OAuthProvider:
        """Get OAuth provider by name."""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider_name}")
        return self.providers[provider_name]

    def generate_state(self) -> str:
        """Generate a secure state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)

    async def get_authorization_url(self, provider_name: str, state: str) -> str:
        """Generate authorization URL for provider."""
        provider = self.get_provider(provider_name)
        return await provider.get_authorization_url(state)

    async def exchange_code_for_token(self, provider_name: str, code: str, state: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token (`state` binds PKCE where used)."""
        provider = self.get_provider(provider_name)
        return await provider.exchange_code_for_token(code, state)

    async def get_user_info(self, provider_name: str, access_token: str) -> OAuthUserInfo:
        """Get user information from provider."""
        provider = self.get_provider(provider_name)
        return await provider.get_user_info(access_token)

    async def complete_oauth_flow(self, provider_name: str, code: str, state: str) -> tuple[OAuthUserInfo, OAuthTokenResponse]:
        """Complete OAuth flow: exchange code for token and get user info."""
        token_response = await self.exchange_code_for_token(provider_name, code, state)
        user_info = await self.get_user_info(provider_name, token_response.accessToken)
        return user_info, token_response


# Global OAuth service instance
oauth_service = OAuthService()
