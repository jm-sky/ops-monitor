# OAuth GitHub — logowanie przez GitHub

| Pole | Wartość |
|---|---|
| **ID** | `006` |
| **Data** | 2026-07-07 |
| **Status** | `done` |
| **Moduł** | `auth` (shared core) |
| **Source** | [gear-stack #014](../../gear-stack/docs/issues/2026-07-07--014--oauth-github-login.md) · [AI-workspace](../../AI-workspace) |

## Opis zadania

Backport logowania GitHub OAuth z AI-workspace / gear-stack: backend provider, przycisk na login/register, callback `/auth/github`.

## Checklist

- [x] `backend/app/core/oauth.py` — `GitHubOAuthProvider`
- [x] `backend/app/core/config.py` — `GITHUB_OAUTH_*`
- [x] Frontend: `OAuthGitHubButton`, `routes.ts`, `useOAuth.ts`
- [x] `.env.example` — `GITHUB_OAUTH_*`, `VITE_GITHUB_OAUTH_CLIENT_ID`

## Weryfikacja

Login → GitHub → `/auth/github` → dashboard (po konfiguracji OAuth App na GitHubie).
