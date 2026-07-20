# ops-monitor Dependency Audit

**Status:** `done`
**Created:** 2026-07-20

## Scope & method

Audited `backend/requirements.txt`, `agent/requirements.txt`, `backend/pyproject.toml` (tooling config only — no deps), and `package.json` + `pnpm-lock.yaml` at the repo root. No files were modified and no installs were run.

Two things shape how to read the numbers below:

- **Backend has no lockfile.** `backend/requirements.txt` (and `agent/requirements.txt`) only declare `>=` floors, and the Dockerfile does a plain `pip install --no-cache-dir -r requirements.txt` with no `pip-compile`/`uv.lock`/hash pinning. That means the *actually installed* version in any given image build is "whatever was newest on PyPI that day," not something recorded in git. The table below compares the **declared floor** against **current PyPI latest** — treat the floor as a worst-case lower bound, not necessarily what's running today. `backend/requirements.txt` was last touched 2026-07-03 in commit `4bea505` ("security: fix all Python backend vulnerabilities (41 → 0)"), so floors already reflect a fairly recent sweep — the gaps found now are ~2.5 weeks of upstream drift since then, not years of neglect.
- **Frontend has a lockfile** (`pnpm-lock.yaml`), so npm numbers below are the actual resolved versions, not just the `^` range in `package.json`.

CVE data comes from the OSV.dev API (queried live per-package/version), cross-checked with PyPI/npm registry metadata for latest-available versions.

---

## 1. Backend (pip) — outdated packages

All packages below use `>=` floors; "Declared floor" is what's in `requirements.txt`, "Latest" is current PyPI.

| Package | Declared floor | Latest | CVE on floor version? | Notes |
|---|---|---|---|---|
| **Pillow** | 12.0.0 | **12.3.0** | **Yes** — 6 distinct GHSAs affect 12.0.0 (heap buffer overflow with nested list coords GHSA-5xmw-vc9v-4wf2, OOB write loading PSD images GHSA-cfh3-3jmp-rvhc, OOB write via invalid PSD tile extents/integer overflow GHSA-pwv6-vv43-88gr, PDF trailer parsing infinite loop/DoS GHSA-r73j-pqj5-w3x7, FITS GZIP decompression bomb GHSA-whj4-6x5x-4v2j, integer overflow processing fonts GHSA-wjx4-4jcj-g98j) — all fixed by 12.2.0/12.3.0 | Image processing lib, directly security-sensitive. `>=12.0.0` **permits** a vulnerable resolve; 12.3.0 is clean. |
| **jinja2** | 3.1.0 | **3.1.6** | **Yes** — 5 GHSAs: sandbox breakout via `attr` filter selecting `format` method (GHSA-cpwx-vrp4-4pq7, fixed 3.1.6), sandbox breakout via malicious filenames (GHSA-gmj6-6f8f-6699, fixed 3.1.5), HTML attribute injection via `xmlattr` filter (GHSA-h5c8-rqwp-cp95 fixed 3.1.3, GHSA-h75v-3vvj-5mfj fixed 3.1.4), sandbox breakout via indirect reference to `format` method (GHSA-q2x7-8rv6-6q7h, fixed 3.1.5) | Templating engine — sandbox-breakout CVEs are serious if any user input reaches a Jinja template/sandbox. `>=3.1.0` is the weakest possible floor here. |
| **python-dotenv** | 1.0.0 | **1.2.2** | **Yes** — symlink following in `set_key` allows arbitrary file overwrite via cross-device rename fallback (GHSA-mf9w-mj56-hr94), fixed in 1.2.2 | Lower severity (needs local write access to exploit), but trivial to fix. |
| redis | 5.0.1 | 8.0.1 | No | 3 major versions behind. RESP3 becomes the default wire protocol in 8.0 (response shapes for type-checking change; runtime behavior preserved for common ops). Used here for token blacklist/challenge storage. |
| bcrypt | 4.0.0 | 5.0.0 | No | Major bump. 5.0 makes &gt;72-byte passwords a hard `ValueError` instead of silent truncation, drops the `__about__` attribute (breaks passlib version-sniffing if anything still uses passlib), bumps MSRV. |
| webauthn (py_webauthn) | 2.3.0 | 3.0.0 | No | Major bump, real API surface change: Pydantic dependency removed entirely, `generate_challenge()` signature changed (no args, always 64 bytes), exception hierarchy now rooted at `WebAuthnException`. Directly touches the WebAuthn/passkey auth code — see SEC-3 in the security-backend review, this library's stub verification needs fixing regardless of version. |
| cryptography | 48.0.1 | 49.0.0 | No | Major version, but pyca/cryptography treats majors as routine; low practical risk. |
| httpx | 0.27.0 | 0.28.1 | No | 0.28 removed the deprecated `proxies=` argument in favor of `proxy=`/`mounts=`. Grep for `proxies=` before bumping. |
| sqlalchemy | 2.0.35 | 2.0.51 | No | Same 2.0 branch, purely patch/minor catch-up. |
| alembic | 1.13.0 | 1.18.5 | No | Same major, incremental. |
| aiosqlite | 0.20.0 | 0.22.1 | No | Incremental. |
| asyncpg | 0.30.0 | 0.31.0 | No | Incremental. |
| greenlet | 3.0.0 | 3.5.3 | No | Incremental (SQLAlchemy async transitive dep). |
| typer[all] | 0.20.0 | 0.27.0 | No | Several 0.x releases behind; stable in practice. |
| rich | 14.2.0 | 15.0.0 | No | Major bump; historically low-breakage, CLI output formatting worth a smoke test. |
| python-ulid | 2.7.0 | 3.2.1 | No | Major bump — check for API changes before relying on it in new code. |
| questionary | 2.0.1 | 2.1.1 | No | Minor, safe. |
| sentry-sdk[fastapi] | 2.19.0 | 2.66.0 | No | Same 2.x major but 47 releases behind — skim the FastAPI-integration changelog before bumping. |
| slowapi | 0.1.9 | 0.1.10 | No | Patch, safe. |
| pytest / pytest-asyncio / pytest-cov / pytest-mock | 8.3.0 / 0.24.0 / 6.0.0 / 3.15.0 | 9.1.1 / 1.4.0 / 7.1.0 / 3.15.1 | No | Dev-only; pytest-asyncio 0→1 changed `asyncio_mode` defaults — check config. |
| black | 24.10.0 | 26.5.1 | No | Dev-only; expect cosmetic reformat churn on first run. |
| mypy | 1.14.0 | 2.3.0 | No | Major bump. `bytearray`/`memoryview` no longer implicitly assignable to `bytes` (PEP 688), stricter `--ignore-missing-imports` — expect new errors to surface. Dev-only, no runtime risk. |
| ruff | 0.9.0 | 0.15.22 | No | Dev-only, low risk, may flag new lint rules. |

Already at latest / effectively no drift: **fastapi** (floor 0.115.0, latest 0.139.2 — big numeric gap but 0.x has stayed additive/non-breaking), **uvicorn**, **pydantic**, **pydantic-settings** (2.14.2 == latest), **python-multipart**, **python-magic** (0.4.27 == latest), **aiofiles**, **aioboto3**, **PyJWT** (2.13.0 == latest), **pyotp**, **idna** (&gt;=3.15, latest 3.18 — the relevant DoS CVE was fixed at 3.7, well below this floor), **mako** (1.3.12 == latest), **urllib3** (2.7.0 == latest), **aiohttp** (3.14.1 == latest), **starlette** (1.3.1 == latest — these last four form the "security minimums for transitive deps" block at the bottom of requirements.txt, already pinned at current tip).

**`agent/requirements.txt`** (standalone agent, separate from backend): `fastapi>=0.115.0`, `uvicorn>=0.32.0` — same as above. `psutil>=6.0.0` vs latest **7.2.2** (major bump, no CVE found — check for renamed/removed platform-specific APIs before bumping). `types-psutil` and `python-dotenv` mirror backend.

---

## 2. Frontend (npm/pnpm) — outdated packages + family baseline drift

**Family baseline check** (per `.docs/backport-progress.md`): Vue 3.5.38, Vite 7.3.6, axios 1.17.0, pinia 3.0.4, vue-tsc 3.3.4.

| Baseline package | Baseline version | ops-monitor resolved | Drift? |
|---|---|---|---|
| vue | 3.5.38 | 3.5.38 | None — exact match |
| vite | 7.3.6 | 7.3.6 | None — exact match |
| axios | 1.17.0 | **1.18.1** | Ahead (caret range resolved forward) — not a violation |
| pinia | 3.0.4 | 3.0.4 | None — exact match |
| vue-tsc | 3.3.4 | 3.3.4 | None — exact match (pinned without `^`) |

**No baseline drift to fix.** ops-monitor is fully in sync with the family core on these five; axios is marginally ahead, fine.

**Other npm deps, resolved vs latest:**

| Package | Resolved | Latest | CVE on resolved? | Notes |
|---|---|---|---|---|
| axios | 1.18.1 | 1.18.1 | No | Up to date. |
| vue | 3.5.38 | 3.5.40 | No | Trivial patch behind. |
| vue-tsc | 3.3.4 | 3.3.7 | No | Trivial patch behind. |
| vite | 7.3.6 | **8.1.5** | No | Major — Vite 8 replaces esbuild+Rollup with Rolldown (Rust bundler) + Oxc + Lightning CSS. `build.rollupOptions` → `build.rolldownOptions`, CJS default-import interop changed, CSS minifier defaults to Lightning CSS. Vite team recommends trialing `rolldown-vite` as a drop-in on the current v7 API first. |
| pinia | 3.0.4 | **4.0.2** | No | Major, but Pinia calls it "only technically breaking": ESM-only (CJS dropped), `@vue/devtools-api` now separate, warnings refactored. Fairly mechanical. |
| @sentry/vue | 10.64.0 | 10.66.0 | No | Minor, safe. |
| @sentry/vite-plugin | 5.3.0 | 5.4.0 | No | Minor, safe. |
| tailwindcss / @tailwindcss/vite | 4.2.2 (exact-pinned) | 4.3.3 | No | Minor. Exact-pinned in package.json (no `^`), suggests a deliberate earlier freeze — skim changelog before bumping. |
| zod | 3.25.76 | **4.4.3** | No | Major, substantial breaking surface: string format validators move from methods to top-level functions (`z.string().email()` → `z.email()`), `.strict()`/`.passthrough()` replaced by `z.strictObject()`/`z.looseObject()`, defaults apply differently inside `.optional()`. A codemod exists (`@zod/codemod --transform v3-to-v4`) but needs review — `@vee-validate/zod` needs to support v4 first. |
| vue-router | 4.6.4 | **5.2.0** | No | Nominally major, but per the Vue Router team this is a **non-breaking transition release** merging `unplugin-vue-router`'s file-based routing into core; standard usage (no `unplugin-vue-router`) upgrades with zero code changes. Effectively safe despite the version number. |
| typescript | 5.9.3 | **7.0.2** | No | Major — the Microsoft native/Go-compiler rewrite. `--strict` becomes default-on, `moduleResolution: node10` removed, implicit-`any` in JS becomes an error. Explicitly recommended to stage through 6.0 first rather than jump 5→7. Also currently lacks a stable Compiler API (promised for 7.1), which can affect ESLint/ts-morph tooling. |
| eslint | 9.39.4 | 10.7.0 | No | Major, dev-only. Low blast radius, budget time last. |
| markdown-it | 14.3.0 | 14.3.0 | No | Up to date. |
| @simplewebauthn/browser, jwt-decode, qrcode, md5, reka-ui | at/near latest | — | No | Checked individually via OSV, no vulns. |

No npm CVEs were found on any currently-resolved direct dependency. The `pnpm.overrides` block in `package.json` already pins a long list of known-vulnerable transitive packages (esbuild ≥0.28.1, form-data ≥4.0.6, ws ≥8.21.0, js-yaml ≥4.2.0, etc.) — matches the "Dependabot remediation" line in the backport matrix. Nothing further to add there.

---

## 3. Risk classification

**Safe patch/minor — bump anytime, no real behavior risk:**
- Backend: fastapi, uvicorn, pydantic, python-multipart, slowapi, sqlalchemy, alembic, aiosqlite, asyncpg, greenlet, questionary, python-magic, PyJWT, pyotp, idna, mako, urllib3, aiohttp, starlette, aiofiles, aioboto3, ruff, black (expect one cosmetic reformat commit)
- Frontend: vue (→3.5.40), vue-tsc (→3.3.7), @sentry/vue, @sentry/vite-plugin, markdown-it, tailwindcss/@tailwindcss/vite (→4.3.3)
- **Security-relevant, still "safe" bumps**: **Pillow → 12.3.0**, **jinja2 → 3.1.6**, **python-dotenv → 1.2.2** — pure floor-tightening (no new major version, no API change expected), just closing off the window where an old cached wheel could satisfy the current loose `>=`.

**Minor bump needing a quick check:**
- httpx 0.27→0.28 — grep for `proxies=` kwarg first.
- typer, rich, sentry-sdk[fastapi] — skim changelogs.
- python-ulid 2→3 — check for renamed methods.
- pytest-asyncio 0.24→1.x — verify `asyncio_mode` config.
- mypy 1.14→2.0 (dev-only) — expect new type errors from the PEP 688 change; zero runtime impact.
- vue-router 4→5 — despite the major version, treat as effectively safe but verify no `unplugin-vue-router` usage exists first.
- redis-py 5→8 — check token-blacklist/challenge-storage call sites against RESP3 defaults; low usage surface (simple key/value ops) suggests a quick check, not a rewrite.

**Major bump requiring real migration work:**
- **bcrypt 4→5** — password-length behavior changes from silent truncation to a hard `ValueError` on &gt;72-byte input. Check the password-hashing path before bumping — this could turn into a 500 in production instead of degrading gracefully.
- **webauthn (py_webauthn) 2→3** — touches the passkey/WebAuthn auth flow directly: Pydantic removed from the library, `generate_challenge()` signature changed, exception hierarchy changed. Real code-change work — bundle with the SEC-3 fix from the security-backend review (the stub verification needs rewriting anyway), not a standalone dep bump.
- **vite 7→8** (frontend) — Rolldown bundler swap. Should be a coordinated family-wide bump (shared baseline across core_family apps), not ops-monitor going first alone.
- **pinia 3→4** — ESM-only + separate devtools-api install. Contained, but move with the family baseline.
- **zod 3→4** — largest actual frontend API surface change; also gates `@vee-validate/zod` compatibility. Real day-or-two migration.
- **typescript 5.9→7** — biggest single item in this audit. Stage through TS 6 first per upstream guidance; also missing a stable Compiler API until 7.1, which risks breaking ESLint/tooling.
- **eslint 9→10** (dev-only) — deferred major.
- **cryptography 48→49** — nominally major, pyca majors are historically low-drama, but verify given it underpins auth.

---

## 4. Prioritized bump plan

**Do first (security-relevant + trivial):**
1. `Pillow>=12.3.0`, `jinja2>=3.1.6`, `python-dotenv>=1.2.2` in `backend/requirements.txt` — closes real, named CVEs (GHSA-5xmw-vc9v-4wf2 and siblings for Pillow; GHSA-cpwx-vrp4-4pq7 and siblings for jinja2; GHSA-mf9w-mj56-hr94 for python-dotenv) that the current floor technically still permits. Zero expected behavior change.
2. Tighten the rest of the backend floors already effectively at latest (fastapi, pydantic-settings, python-multipart, PyJWT, python-magic, idna, mako, urllib3, aiohttp, starlette) — hygiene, confirms the resolver can't silently drift backward.
3. **The single highest-leverage fix here isn't a version bump — it's adding a pinned lock (`pip-compile`/`uv pip compile` or hashes) so "outdated" becomes an answerable question from git history instead of "whatever PyPI had that day."** Recommend doing this before or alongside the version bumps above.

**Do soon (quick-check minors):**
4. httpx → 0.28.1 (after grepping `proxies=`), sentry-sdk → latest 2.x, typer/rich/questionary catch-up, pytest-asyncio major (after confirming `asyncio_mode`).
5. Frontend: vue → 3.5.40, vue-tsc → 3.3.7, @sentry/vue/@sentry/vite-plugin, tailwindcss → 4.3.3.
6. vue-router → 5.2.0 — low-risk per upstream's own "no breaking changes" statement; worth confirming in a family-wide pass.

**Defer (real migration work, plan as dedicated issues):**
7. **webauthn (py_webauthn) 2→3** and **bcrypt 4→5** — both touch live auth code. ops-monitor was the *source* project for the recent WebAuthn backport work (010/011 in the family queue) — natural next entry in that same queue, and should be bundled with the SEC-3 fix (unverified WebAuthn assertion) from the security-backend review rather than done as a quiet dependency bump.
8. **redis-py 5→8** — check token-blacklist/challenge-storage call sites against RESP3 defaults before bumping.
9. **zod 3→4**, **vite 7→8**, **pinia 3→4**, **typescript 5.9→7** — all four are family-baseline items and should move together across gear-stack/AI-workspace/family-recipes/ops-monitor/zbory-chwz once gear-stack (source of truth) adopts them, not piecemeal in ops-monitor alone. TypeScript needs the staged 5→6→7 path specifically.
10. **mypy 1→2**, **eslint 9→10**, **black/ruff majors** — dev-tooling-only, no runtime risk, lowest priority; batch into a single "tooling refresh" pass.

Sources: OSV.dev API, PyPI JSON API and npmjs registry, pyca/bcrypt CHANGELOG.rst, redis/redis-py GitHub releases, duo-labs/py_webauthn CHANGELOG.md, Vue Router migration guide (router.vuejs.org), Zod v4 migration guide (zod.dev/v4/changelog), Vite migration guide + Vite 8 announcement (vite.dev), mypy changelog (mypy.readthedocs.io), TypeScript 7 migration coverage.
