# Runbook: optional login via OpenID Connect (e.g. Authentik)

**What it does:** adds a "Log in with <label>" button next to password login. Password login,
2FA and the existing OAuth providers keep working. Without the settings below the button and
the provider simply do not exist.

**How it works:**

- Backend redirects to the IdP (confidential client, PKCE S256), the IdP returns to
  `<app>/auth/callback/oidc`, the backend exchanges the code and reads `userinfo`.
- Only members of `OIDC_REQUIRED_GROUP` get in — checked **before** any account is created.
  Bind the same group to the application in the IdP as well (first lock); the app check is the second.
- First login creates the account; an existing account with the same e-mail is linked.
- **Admin is hybrid:** local `is_admin` is the source of truth. Members of `OIDC_ADMIN_GROUP`
  (optional) are granted admin on login. Leaving the group does **not** revoke admin — do that
  manually in Admin → Users.
- If the user enabled 2FA in the app, it is still required after the IdP login.
- Logout logs out of this app only, not of the IdP. The app session is the usual JWT + refresh cookie.

## 1. IdP side (Authentik)

1. **Directory → Groups → Create:** a group for access (e.g. `ops-monitor`), optionally a second one
   for admins (e.g. `ops-monitor-admin`). Add members.
2. **Applications → Applications → Create with provider:**
   - Application slug: e.g. `ops-monitor` (it is part of the discovery URL).
   - Provider type: **OAuth2/OpenID Provider**.
   - Authorization flow: `default-provider-authorization-implicit-consent`.
   - Client type: **Confidential** — copy Client ID and Client Secret.
   - Redirect URIs (Strict): `https://<app-host>/auth/callback/oidc`
     (+ `http://localhost:<VITE_PORT>/auth/callback/oidc` for local dev).
   - Signing Key: select one (e.g. `authentik Self-signed Certificate`).
   - Advanced protocol settings → Scopes: `openid`, `email`, `profile` (`profile` carries `groups`).
   - Bindings: bind the access group.
3. Check that `https://<idp-host>/application/o/<slug>/.well-known/openid-configuration` opens.

## 2. App settings

`backend/.env`:

```env
OIDC_DISCOVERY_URL=https://<idp-host>/application/o/<slug>/.well-known/openid-configuration
OIDC_CLIENT_ID=<client id>
OIDC_CLIENT_SECRET=<client secret>
OIDC_REDIRECT_URI=https://<app-host>/auth/callback/oidc
OIDC_REQUIRED_GROUP=ops-monitor
OIDC_ADMIN_GROUP=ops-monitor-admin   # optional
```

Frontend `.env` (build-time):

```env
VITE_OIDC_ENABLED=true
VITE_OIDC_LABEL=Authentik
```

Then redeploy (`bash scripts/deploy.sh`) — the frontend must be rebuilt for `VITE_*` to apply.

Check that the backend container reaches the IdP:

```bash
docker exec ops-monitor-app python -c "import httpx, os; print(httpx.get(os.environ['OIDC_DISCOVERY_URL']).status_code)"
```

## 3. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| IdP: "Redirect URI Error" | `OIDC_REDIRECT_URI` differs from the IdP entry (trailing slash, http/https, host) |
| App: "OIDC login is not configured" | one of the required `OIDC_*` values is empty (incl. `OIDC_REQUIRED_GROUP`) |
| App: "You do not have access to this application" | user not in `OIDC_REQUIRED_GROUP`, group name mismatch, or `groups` claim missing (scope `profile`) |
| App: "OAuth authentication failed: OIDC token error: invalid_grant" | stale/reloaded callback link — log in again; if it repeats: wrong client secret |
| Expected admin, got user | user not in `OIDC_ADMIN_GROUP`, or the name differs; admin is granted at next login |
