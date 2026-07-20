# Review: ops-monitor — frontend security review (Vue 3)

**Status:** `done`
**Created:** 2026-07-20
**Scope:** `src/` — auth/session, OAuth, WebAuthn, route guards, XSS surfaces, client storage, dependencies
**Reference bar:** `zbory-chwz/docs/reviews/2026-07-10--church-platform-review.md`
**Baseline:** `.docs/backport-progress.md` (2026-07-18)

---

## Summary / verdict

The frontend is in decent shape and most `backport-progress.md` claims for ops-monitor hold up under inspection. There are **no live XSS sinks** (zero `v-html` in the codebase), OAuth CSRF-state handling is correct, WebAuthn is implemented against the current SimpleWebAuthn `optionsJSON` contract, admin routes are gated, and the dependency baseline is actually **ahead** of the family floor (axios resolves to 1.18.1, Vite 7.3.6, Vue 3.5.38, vue-tsc 3.3.4), with `pnpm.overrides` doing real remediation.

The findings are not IDOR-class holes like the zbory-chwz backend review — they are client-side hardening gaps. The most material items: **all bearer tokens (access + refresh + 2FA) live in `localStorage`** (XSS-exfiltratable, and this is the real meaning behind the matrix's "OAuth sessionStorage" ✅ — only the CSRF *state* is in sessionStorage, not the tokens), **Sentry session replay ships unmasked page text to a third party**, and the **2FA route guard is dead code that is never installed on the router** despite `authGuard` explicitly deferring to it.

| Area | Assessment |
|------|-----------|
| Backport claims vs reality | Mostly accurate; one misleading label (see SEC-F1), one broken feature not in the matrix (SEC-F3) |
| XSS surface | Clean — no `v-html`, markdown renderer is dead code |
| Token/session storage | Weak — bearer + refresh + 2FA tokens in `localStorage` |
| OAuth / WebAuthn | Correct (state validation, options contract) |
| Route guards | Auth + admin OK; 2FA guard not wired |
| Dependencies | Good — at or above family baseline, overrides applied |
| Third-party data exposure | Sentry replay misconfigured (unmasked) |

---

## Verification of `backport-progress.md` claims

| Claim (matrix ✅ for ops-monitor) | Verdict | Evidence |
|---|---|---|
| OAuth sessionStorage (not localStorage) | ⚠️ **Partially misleading** | `useOAuth.ts:31` + `OAuthCallbackPage.vue:60,70` put/read only the **`oauth_state` CSRF param** in `sessionStorage`. The **access/refresh/2FA tokens go to `localStorage`** (`useAuthStore.ts:13–15,25,38,75`). Claim is literally true for what it names, but does not mean tokens are in sessionStorage. See SEC-F1. |
| WebAuthn FE contract (passkey list/delete) | ✅ Holds | `useWebAuthn.ts` uses `startRegistration({optionsJSON})` / `startAuthentication({optionsJSON})`, register/verify/delete + query invalidation. |
| Login formError a11y / pagination a11y / layout dark tokens / FB button / PasswordInput | ✅ Present | Components exist (`LoginForm.vue`, `OAuthFacebookButton.vue`, `PasswordInput.vue`, per-provider `v-if` in `useOAuth`). Not security-relevant; not re-audited in depth. |
| Dependabot axios 1.17 + pnpm overrides | ✅ Holds / exceeded | `package.json` `axios ^1.17.0`; lockfile resolves **axios@1.18.1**. `pnpm.overrides` remediates form-data, esbuild, ws, serialize-javascript, postcss, brace-expansion, etc. |

---

## Findings — Security

### SEC-F1 · High · Access, refresh, and 2FA tokens stored in `localStorage`

`src/modules/auth/store/useAuthStore.ts:13–15,25,38,75` and read back by the request interceptor `src/shared/services/auth.interceptor.ts:5`:

```ts
const token = ref<string | null>(localStorage.getItem(JWT_STORE_KEY))           // :13
const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY)) // :14
const twoFactorToken = ref<string | null>(localStorage.getItem(TWO_FACTOR_TOKEN_KEY)) // :15
...
localStorage.setItem(JWT_STORE_KEY, newToken)          // :25
localStorage.setItem(TWO_FACTOR_TOKEN_KEY, newToken)   // :38
localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken) // :75
```

**Exploit scenario:** any script that executes in the app origin — a compromised npm dependency (the app pulls in markdown-it, unovis, floating-vue, reCAPTCHA + Google Fonts from remote origins), a future `v-html` regression, or a malicious browser extension operating in-page — can run `localStorage.getItem('ops-monitor:token')` and `localStorage.getItem('vbr_refresh_token')` and exfiltrate them with a single `fetch()`. Because the **refresh token** is also there, the attacker gets durable, renewable access, not just a short-lived session — full silent account takeover that survives the access-token TTL. `httpOnly` cookies would make the tokens unreachable to JS; `localStorage` is the worst option specifically because XSS can read it.

Note this is the **gear-stack family baseline pattern**, not an ops-monitor regression — but the matrix's "OAuth sessionStorage ✅" wording invites the reader to believe tokens are not in `localStorage`, which is false. Also minor: `REFRESH_TOKEN_KEY`/`TWO_FACTOR_TOKEN_KEY` are hardcoded `vbr_refresh_token` / `vbr_2fa_token` (`useAuthStore.ts:8–9`), not namespaced by `config.app.id` like `JWT_STORE_KEY`, so they carry a stale `vbr_` prefix from the source template.

**Recommendation:** move refresh (at minimum) to an `httpOnly; Secure; SameSite` cookie issued by the backend; keep the access token in memory (Pinia state, not persisted) and re-mint from the cookie on load. If the family must keep `localStorage` for now, document it explicitly in the matrix instead of implying sessionStorage, and at least namespace all three keys consistently.

---

### SEC-F2 · Medium · Sentry session replay records unmasked page text and media

`src/shared/services/sentry.ts:25–28`:

```ts
Sentry.replayIntegration({
  maskAllText: false,
  blockAllMedia: false,
}),
```

with `replaysOnErrorSampleRate` defaulting to `1.0` (`config.ts:88`). Replay captures a DOM recording of every page visited during a sampled/error session and uploads it to Sentry.

**Exploit scenario:** with `maskAllText:false`, every rendered string is sent to Sentry — the logged-in user's name and email in `UserNav`, and for an ops-monitoring dashboard specifically, the **infrastructure it exists to display**: monitored hostnames, IPs, `/health/details`, reboot/update status, incident text. A support engineer or anyone with Sentry project access (or a Sentry-side breach) sees a pixel-accurate replay of production infra state. `blockAllMedia:false` additionally lets media/screenshots through. Sentry masks `<input>` values by default so passwords aren't captured, but everything else visible is.

**Recommendation:** set `maskAllText: true` and `blockAllMedia: true` (Sentry's safe defaults), or gate replay off in this app entirely. At soft-launch with no external users the urgency is low, but this is a live third-party data egress that ships more than errors.

---

### SEC-F3 · Medium · 2FA route guard is dead code — never installed on the router

`src/router/index.ts:40–43` installs only two global guards:

```ts
protectRoutes(router)        // authGuard
protectAdminRoutes(router)   // adminGuard
```

`twoFactorGuard` / `protectRoutesWithTwoFactor` (`src/modules/auth/guards/twoFactorGuard.ts:85`) is **never imported or called** anywhere (grep of `src/` returns only its own definition). Yet `authGuard.ts:35–38` explicitly hands off to it:

```ts
// Skip auth checks for 2FA verify route - twoFactorGuard handles it
if (to.path === TWO_FACTOR_VERIFY_ROUTE) { next(); return }
```

**Exploit scenario / impact:** the client-side enforcement that a user holding a token with `tfaPending=true` (2FA not yet completed) is pinned to `/auth/2fa/verify` does not run. The saving grace is that `isAuthenticated = hasToken && hasUser`, and the backend returns `401 "2FA verification required"` on protected endpoints, which `authGuard.ts:77–88` catches and uses to clear the token and bounce to login — so this is a **defense-in-depth gap, not a clean bypass**. But the intended layered 2FA gating is silently absent, and `authGuard` waives its own checks on the verify route trusting a guard that isn't there. Any future backend gap in the 2FA `401` path would become directly exploitable.

**Recommendation:** install the guard (`protectRoutesWithTwoFactor(router)` after `protectRoutes`) or delete the file and the misleading `authGuard` comment. Add a test asserting a `tfaPending` token cannot navigate to a `requiresAuth` route.

---

### SEC-F4 · Low · Unvalidated `redirectTo` passed to `router.push`

`src/modules/auth/components/LoginForm.vue:83–84` (and identically `TwoFactorVerifyPage.vue:72–73`):

```ts
const redirectTo = typeof route.query.redirectTo === 'string' ? route.query.redirectTo : undefined
await router.push(redirectTo ?? AuthRoutePaths.dashboard)
```

`redirectTo` comes straight from the URL query with no check that it's a same-origin app path.

**Exploit scenario:** a crafted link `…/auth/login?redirectTo=//evil.example/phish` is passed to `router.push`. Vue Router resolves string pushes against its own matcher rather than performing a raw location assignment, which blunts classic open-redirect (it won't navigate cross-origin), but protocol-relative / unexpected values still produce confusing post-login navigation and shouldn't be trusted verbatim.

**Recommendation:** validate `redirectTo` starts with a single `/` and not `//` before use; fall back to the dashboard otherwise.

---

### SEC-F5 · Low / Informational · No CSP, and CSP-hostile inline scripts in `index.html`

`index.html` ships two inline `<script>` blocks (manifest loader, Google-Fonts `display=swap` MutationObserver) and an inline `<style>`, and pulls remote origins: reCAPTCHA (`recaptcha.ts:24` → `https://www.google.com/recaptcha/api.js`), Google Fonts, and Sentry ingest. There is no `<meta http-equiv="Content-Security-Policy">`.

**Impact:** CSP is presumably intended to live in Caddy (per `CLAUDE.local.md`), but whenever it's added, the inline scripts force `script-src 'unsafe-inline'` (or nonces/hashes), which materially weakens the very CSP that would mitigate SEC-F1. This is the coupling to flag: the token-storage risk and the CSP-hostile inline scripts compound each other.

**Recommendation:** move the two inline scripts to an external module (they're the only inline JS) so a strict, nonce-free `script-src` becomes possible in Caddy, then add the CSP header.

---

### INFO · Markdown sanitizer is dead code and would not stop tag-based XSS if revived

`markdown-it` is a dependency and `src/shared/utils/markdownPostProcess.ts` (`secureMarkdownHtml`) + `linkSecurity.ts` + `config/markdownSecurity.ts` exist, but `secureMarkdownHtml` is **never called** and `markdown-it` is **never imported** anywhere in `src/` (grep confirms). So there is no live XSS today. Two forward-looking notes: (1) the "sanitizer" only rewrites `<a href>` protocols — it does **not** strip `<script>`, `<img onerror=…>`, or event-handler attributes, and there is **no DOMPurify** in the dependency tree; (2) if someone later renders markdown via `v-html` using these helpers, they'll get a false sense of safety. Either remove the dead code + dependency, or, before any real use, route output through DOMPurify.

---

## Things checked and found OK

- **No `v-html` / `innerHTML` / `eval` anywhere** in `src/` — no active XSS sink.
- **OAuth CSRF state**: generated server-side, stored in `sessionStorage` (`useOAuth.ts:31`), strictly compared and cleared on callback (`OAuthCallbackPage.vue:60–70`). `window.location.href = response.authUrl` uses a backend-provided URL, not user input — no open redirect there.
- **Token-refresh race**: `error.interceptor.ts` correctly serializes concurrent 401s through a Pinia queue (`useTokenRefreshStore`), single in-flight refresh, `_retry` guard — no obvious stampede.
- **Token leakage in logs**: interceptors and `logger.ts` don't log token values; `logger` is `DEV`-gated. reCAPTCHA/JWT `console.*` calls log messages only, not secrets.
- **Admin gating**: `adminGuard.ts` checks `canAccessAdminPanel` and is installed (`router/index.ts:43`); admin routes carry `requiresAdmin` (`admin/routes.ts`). Client-side only, as expected — backend must remain the real authority.
- **Dependencies**: at/above family baseline; axios 1.18.1, Vite 7.3.6, Vue 3.5.38, vue-tsc 3.3.4; extensive `pnpm.overrides` remediation present. No hardcoded secrets in `src/` (only public `VITE_*` client IDs / DSN / reCAPTCHA site key, which are public by design).

---

## Overall risk verdict

Low-to-moderate residual risk for a pre-launch internal ops dashboard. There is no critical, directly-exploitable server-trust hole in the frontend — no `v-html`, correct OAuth state handling, working auth/admin guards, and a dependency set that is genuinely current. The real exposure is concentrated in three hardening gaps that would matter more the moment this faces real users or a supply-chain incident: bearer **and refresh** tokens sitting in `localStorage` (SEC-F1) turn any single script-execution bug into durable account takeover; Sentry replay (SEC-F2) continuously ships unmasked infrastructure state and user PII to a third party; and the 2FA guard being dead code (SEC-F3) means the second auth factor is enforced only by the backend, with the frontend's layered defense quietly missing. None require emergency action pre-launch, but SEC-F1 and SEC-F3 should be resolved (or, for SEC-F1, explicitly accepted and corrected in the backport matrix's misleading "sessionStorage" label) before onboarding real external users, and SEC-F2 is a one-line config fix worth taking now.
