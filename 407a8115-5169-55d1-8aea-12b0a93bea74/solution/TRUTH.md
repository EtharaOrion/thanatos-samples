# truth.md - Twenty, localStorage JWT to persisted cookie sessions

## Provenance

This is the private golden-trajectory projection for bundle `407a8115-5169-55d1-8aea-12b0a93bea74`, the browser-authentication migration of `twentyhq/twenty` from base commit `f8e3fd110d35778bef7341ef563c2607d065bd2e` to reference commit `267ecb12db90c003abbbfb23a16114747a460203`, published as pull request 23642 under evaluation version `persisted-cookie-sessions-2026-09-24`. It is derived from frozen bundle bytes alone: `instruction.md`, `task.toml`, `tests/config.json`, `tests/test_weights.json`, `tests/score_tests.py`, `tests/test_outputs.py`, `tests/test.sh`, `tests/rubric.json`, and `solution/fix.patch`. It records the reference route through the task and the checker identifier each step discharges.

This file is private. `tests/test_outputs.py` copies the candidate workspace into a disposable scratch tree and materialises the frozen suite separately under its own `rootDir`, so nothing here reaches the agent under test. No byte of this document may appear on the agent-visible surface, and no value stated here may be restated in `instruction.md`.

## Scope boundary

`instruction.md` places the following outside the graded contract, and no step below may contradict these reductions.

- Complete application startup, graphical-browser testing, root provider mounting, metadata resync and unrelated subsystems are out of scope. The frozen frontend suite mounts the submitted effects directly rather than booting the application.
- Four behaviours are named as deliberately excluded and are asserted nowhere: Redis deletion failure while reads still succeed, sign-ins committed after the revoke-all snapshot, overflowing lifetime values, and idle-expired-row cleanup timing. A revocation that lags its 60-second read-through TTL under a Redis delete failure is therefore conformant.
- No particular cache algorithm or implementation text is required. `tests/rubric.json` prices behaviour, not structure, and the frozen `runtime.ts` accepts either the `EventLogEmitterService` context shape or the `EventEmitter2` shape for the event-emitter dependency, recording emitted events without scoring them.
- Identity, profile and token-issuance dependencies outside the migration are local fixtures. No external mail, SSO, analytics, model or ClickHouse service is contacted.

## Deliverable manifest

| id | deliverable | established by | graded through |
| :-- | :-- | :-- | :-- |
| D1 | `UserSessionEntity` mapping `core.userSession` with its declared columns and `user`, `workspace`, `userWorkspace` relations | patch adds `packages/twenty-server/src/engine/core-modules/user-session/user-session.entity.ts` | `C01`, `C03`, `C15` |
| D2 | `UserSessionService` with the fixed seven-dependency constructor order | patch adds `.../user-session/services/user-session.service.ts` | `C01` through `C07`, `C10`, `C16` |
| D3 | `UserSessionCookieService` and the four cookie-name constants | patch adds `.../user-session/services/user-session-cookie.service.ts` and `.../constants/user-session-{cookie,secure-cookie,impersonator-cookie,impersonator-secure-cookie}-name.constant.ts` | `C09`, `C10`, `C16` |
| D4 | Opaque credential generation, hashing, prefix recognition and request extraction | patch adds `.../utils/{generate-user-session-token,hash-user-session-token,is-user-session-token,extract-user-session-token-from-request}.util.ts` and `.../constants/user-session-token-prefix.constant.ts` | `C01`, `C16` |
| D5 | Request-origin allow-listing with default-port normalisation | patch adds `.../utils/{is-request-origin-allowed,resolve-allowed-credentialed-origins}.util.ts` | `C08`, `C09` |
| D6 | `CookieSessionCsrfMiddleware` and its mounting in the middleware chain | patch adds `src/engine/middlewares/cookie-session-csrf.middleware.ts`, modifies `middleware.module.ts` and `middleware.service.ts` | `C08` |
| D7 | Cookie-aware `AccessTokenService.validateTokenByRequest` | patch modifies `.../auth/token/services/access-token.service.ts` and `token.module.ts` | `C08`, `C16` |
| D8 | Session-issuing `AuthResolver.renewToken` and `signOut`, and the `AuthService` exchange path | patch modifies `.../auth/auth.resolver.ts` and `.../auth/services/auth.service.ts` | `C02`, `C07`, `C09` |
| D9 | Impersonation park and restore through `stopImpersonation` | patch modifies `.../impersonation/services/impersonation.service.ts` and `impersonation.resolver.ts`, adds `.../admin-panel/dtos/stop-impersonation.dto.ts` | `C10` |
| D10 | Redis read-through entry type and its cache namespace | patch adds `.../user-session/types/cached-user-session.type.ts`, modifies `.../cache-storage/types/cache-storage-namespace.enum.ts` | `C03`, `C04`, `C05`, `C06` |
| D11 | Repeatable `core.userSession` upgrade and rollback command | patch adds `.../2-27/2-27-instance-command-fast-1785518325511-create-user-session-core-table.ts`, modifies `instance-commands.constant.ts` | `C15` |
| D12 | Duration-validated session configuration and the published client flag | patch adds the duration parser, decorators and validator, modifies `twenty-config/config-variables.ts`, `client-config/services/client-config.service.ts` and `client-config.entity.ts` | `C03`, `C09`, `C11`, `C12` |
| D13 | `CookieSessionBootEffect` and its three Jotai atoms | patch adds `auth/effect-components/CookieSessionBootEffect.tsx`, `auth/states/isCookieAuthActiveState.ts`, `auth/states/isPendingServerSignOutState.ts`, `client-config/states/isCookieSessionEnabledState.ts` | `C11`, `C12` |
| D14 | Credentialed Apollo transport that honours deliberate headerless probes | patch modifies `apollo/services/apollo.factory.ts` and `apollo/hooks/useApolloFactory.ts`, adds `apollo/utils/isUnauthenticatedGraphQLError.ts` | `C13` |
| D15 | Cookie-only login state and SSE reconnection | patch adds `auth/hooks/useIsLogged.ts`, deletes `auth/hooks/useHasAccessTokenPair.ts`, modifies `sse-db-event/components/SSEClientEffect.tsx`, `sse-db-event/hooks/useHandleSseClientConnectionRetry.ts` and `apollo/utils/streamingRestLink.ts` | `C14` |
| D16 | Active-session listing and revocation GraphQL surface | patch adds `.../user-session/user-session.resolver.ts`, `.../dtos/user-session.dto.ts` and the frontend device-session documents | `C03`, `C05` |

Every graded group in the Checker identifier set closes over at least one manifest row, and every manifest row is named by at least one trajectory step.

## Checker identifier set

Reward is `passed_groups / 16` over equally weighted groups. `tests/score_tests.py` refuses to grade unless `tests/test_weights.json` equals `dict.fromkeys(config['groups'], 1)`, so the sixteen weights are structurally pinned at 1 each and no group may be re-priced. It grades a group `passed` only when `tests/test_outputs.py` returns `passed: true` for it, which requires that the group's single frozen Jest test reports status `passed`. A group is one whole share: it earns nothing for the subcases it does satisfy, and adding failures inside an already-failing group costs nothing further.

`tests/test_outputs.py` binds a group to exactly one Jest test by matching `^(C\d+)\b` against the test title. A second test claiming the same identifier, a title that does not begin with one, a status other than `passed` or `failed`, or an observed set unequal to the group set declared for that suite raises `Measurement unavailable` and takes the whole run ungraded rather than failing one group.

| group | suite | declared subcases | trajectory step |
| :-- | :-- | --: | :-- |
| `C01` | `backend.spec.ts` | 5 | S2 |
| `C02` | `backend.spec.ts` | 7 | S3 |
| `C03` | `backend.spec.ts` | 9 | S4 |
| `C04` | `backend.spec.ts` | 4 | S5 |
| `C05` | `backend.spec.ts` | 5 | S6 |
| `C06` | `backend.spec.ts` | 2 | S7 |
| `C07` | `backend.spec.ts` | 2 | S8 |
| `C08` | `backend.spec.ts` | 13 | S9 |
| `C09` | `backend.spec.ts` | 10 | S10 |
| `C10` | `backend.spec.ts` | 4 | S11 |
| `C11` | `frontend.spec.tsx` | 4 | S12 |
| `C12` | `frontend.spec.tsx` | 4 | S13 |
| `C13` | `frontend.spec.tsx` | 3 | S14 |
| `C14` | `frontend.spec.tsx` | 7 | S15 |
| `C15` | `backend.spec.ts` | 6 | S16 |
| `C16` | `backend.spec.ts` | 5 | S17 |

The subcase counts are the declarative `subcase_count` values `tests/config.json` records for documentation. The enforced unit is the single named Jest test per group; no subcase is independently scored.

`tests/rubric.json` declares sixteen equally weighted criteria whose ids are the same `C01` through `C16` and whose `test_ids` name the same Jest titles, with `contributes_to_reward` set to `false` because each criterion is already priced once through its deterministic group. Steps below cite those ids to show the reference route does not contradict the written contract; they add nothing to the reward.

## Preconditions

Every group fails or the run goes ungraded, before any behavioural check runs, if a condition below is unmet. Treat these as gate zero rather than as one group among sixteen. The two classes are not interchangeable: an absent migration is a graded zero, while an unavailable measurement is `score: null`.

1. `node`, `redis-server` and `runuser` resolve on `PATH`, `/usr/lib/postgresql/15/bin/initdb` exists, and `/opt/twenty-cache/node_modules/jest/bin/jest.js` exists. Otherwise the run is ungraded.
2. At least one `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` or `.cjs` file exists outside `node_modules`, and the workspace digest differs from `config['base_source_digest']`. An empty submission or a byte-identical unmigrated tree returns `migration_absent` for all sixteen groups, which is a graded reward of `0.0` rather than an ungraded run.
3. Every path in `config['required_files']` is a file: `yarn.lock`, the root `package.json`, and the `package.json` of `twenty-server`, `twenty-front`, `twenty-shared`, `twenty-emails` and `twenty-client-sdk`. A missing or relocated one is ungraded.
4. `yarn.lock` hashes to `config['lock_sha256']`. Any edit to the lockfile, including a reformat, is ungraded. The reference patch touches no lockfile.
5. `vite build` succeeds in the submitted `twenty-shared`, `twenty-emails` and `twenty-client-sdk` packages. The verifier consumes those JavaScript builds without declaration generation.
6. An isolated PostgreSQL 15 cluster and Redis server start on free loopback ports and the `twenty_verifier` database is created.
7. Each suite writes its readiness file and reports no runtime error test suites, and its exit status agrees with its own per-test outcomes. A setup or module-import failure is ungraded.
8. Every failing test carries a `matcherResult` in its `failureDetails`. A group that throws before reaching a behavioural assertion is ungraded for the entire run, not scored as a failure of that group.

## Golden trajectory

### S1 - Stand up the session module without disturbing the published interface

Add the `user-session` core module with its entity, service, cookie service, constants, types, utilities, resolver, DTO and module wiring, register it in `app.module.ts` and the auth, token, impersonation and middleware modules, and add the frontend states, effect and hooks. Leave `yarn.lock` byte-identical, keep every published `package.json` in place, and keep each file at the exact path the frozen suite imports: the Jest `moduleNameMapper` resolves `^src/(.*)` to the copied `packages/twenty-server/src/$1`, so the suite loads the submitted production modules by literal path.

- Established state: a workspace that satisfies preconditions 2 through 5 and exposes every symbol `runtime.ts` imports.
- Drift survived: relocating a module, renaming a service file, or regenerating `yarn.lock` during dependency work does not fail a group. It takes the whole run to `score: null`, so a submission that is behaviourally complete can still return no measurement at all. The same holds for a barrel-file re-export that leaves the original path absent.
- Satisfies: preconditions for all sixteen groups. Consistent with the integration contract in `instruction.md`.

### S2 - Mint opaque credentials and persist only their hashes

Generate `sess_` credentials whose suffix carries at least 32 URL-safe characters drawn from `A-Z`, `a-z`, `0-9`, `_` and `-`, distinct across concurrent issuance, and persist only the lowercase hexadecimal SHA-256 hash. Require workspace and membership together for a workspace session, require neither for a workspace-agnostic session, and require workspace plus both membership identities for an impersonating session. Resolve a live credential into the existing `ACCESS` or `WORKSPACE_AGNOSTIC` payload with its scope and provider preserved.

- Established state: opaque credentials that carry no authority of their own and a stored row from which the plaintext cannot be recovered.
- Drift survived: storing the credential itself, or a hash of a truncated prefix, keeps every functional test green while turning a database read into a full credential compromise. Twelve concurrent issuances are compared for distinctness, so a generator seeded per process rather than per call collides only under the concurrency the group creates.
- Satisfies: `C01`. Consistent with rubric criterion `C01`.

### S3 - Bridge legacy renewal to sessions without fixation

Issue a session alongside a successful legacy renewal in `AuthResolver.renewToken`, and reuse a presented matching live session without creating another row or setting another cookie. Replace and revoke the presented session when the user, workspace or impersonation scope changes, and on a fresh sign-in. Keep issuance best effort: a transient session-storage failure during renewal must return the legacy exchange result unchanged and leave the existing cookie in place.

- Established state: a bridge that converges repeated renewals onto one session row and rotates it exactly when the scope it encodes changes.
- Drift survived: three consecutive matching renewals are asserted, so an implementation that issues a new session per renewal passes a single-renewal test and accumulates rows under real traffic. The opposite error is louder and worse: propagating a Redis read outage out of `renewToken` converts a degraded cache into a sign-out for every renewing user.
- Satisfies: `C02`. Consistent with rubric criterion `C02`.

### S4 - Enforce both deadlines on the cold and warm paths

Apply the absolute lifetime and the idle timeout on the database path and on the cached path alike, rejecting a credential at or past either deadline rather than only past it. Publish the defaults the contract names: 180 days absolute, 30 days idle, one day for an impersonation session. Exclude other users' sessions, revoked sessions and expired sessions from the active listing.

- Established state: one expiry decision that does not depend on which path served the lookup.
- Drift survived: the group checks each deadline cold and warm, so enforcing expiry only where the row is read leaves a cached entry usable past its deadline for the life of the cache. Expiry is exclusive at the boundary, so a `>` comparison where the contract means `>=` admits a credential for exactly the instant the test pins.
- Satisfies: `C03`. Consistent with rubric criterion `C03`.

### S5 - Throttle activity writes without reviving a revoked session

Coalesce persistent activity writes during a burst so that thirty hot resolutions produce at most one persistent write, and keep the throttle interval at or below half the configured idle timeout and at or below five minutes, whichever is shorter. Keep a continuously active short-idle session usable without extending its absolute expiry, and leave an untouched short-idle credential to expire.

- Established state: an activity path cheap enough for real traffic and unable to resurrect a revoked row.
- Drift survived: a fixed throttle constant satisfies the five-minute bound and silently breaks the short-idle case, because a throttle longer than half the idle timeout lets a continuously active session idle out between writes. The revocation case is the sharper one: an activity update written as a blind upsert recreates or un-revokes the row it touches, so a session revoked concurrently becomes usable again through nothing but traffic.
- Satisfies: `C04`. Consistent with rubric criterion `C04`.

### S6 - Scope revocation to its owner and invalidate the healthy cache

Reject revocation by a non-owner, support revoke-all and all-except-current, and invalidate a healthy Redis entry as part of revoking. Leave the excepted session and other users' sessions usable, let the owner subsequently revoke the kept session, and make a repeated revoke idempotent rather than an error or a second state change.

- Established state: a revocation surface whose blast radius is exactly the caller's own sessions minus the exception.
- Drift survived: revoking by session id without checking the owner reads as a clean repository call and lets any authenticated user end anyone's session. Deleting the row without invalidating its cache entry leaves the credential working until the read-through TTL lapses.
- Satisfies: `C05`. Consistent with rubric criterion `C05`.

### S7 - Order revocation against cache fills and activity writes

Ensure that once revocation has completed, no cached usable credential survives it, including when the revocation overlapped a cold cache fill or an activity-triggered cache write. Subsequent authentication must reject the credential. An already authorised in-flight request may finish, and the group pins no cancellation order. Keep the read-through entry's TTL at or below 60 seconds.

- Established state: a revocation that wins every race against the writers that would otherwise re-cache the row it just retired.
- Drift survived: invalidating before, rather than after, the delete leaves a window in which a concurrent fill re-populates the cache from a row it read before revocation landed. The result is a credential that authenticates after revocation returned success, which no sequential test reaches and which the two overlap cases here construct deliberately.
- Satisfies: `C06`. Consistent with rubric criterion `C06`.

### S8 - Revoke the refresh token even when session revocation fails, and verify first

On sign-out, attempt refresh-token revocation despite a session-revocation failure, then propagate the original session-storage error rather than reporting success. Verify a refresh JWT before using any identifier it carries, so a forged token revokes nothing and is a successful no-op on its own. Clear the session cookie only when one was presented.

- Established state: a sign-out that fails loudly on storage errors and never lets an unverified token name the row to delete.
- Drift survived: reading the token identifier before verification is the whole vulnerability. A forged JWT then selects an unrelated token for revocation, which behaves identically to an honest sign-out on every valid input and turns sign-out into an arbitrary-revocation primitive. Swallowing the storage error is the quieter half: the caller is told sign-out succeeded while the session remains live.
- Satisfies: `C07`. Consistent with rubric criterion `C07`.

### S9 - Apply the request-origin policy over real HTTP

Require a same-origin or explicitly configured deployment `Origin` on unsafe cookie-authenticated requests, normalising default ports so that `https://host:443` and `https://host` agree. Reject missing, malformed, `null` and foreign origins with HTTP 403 and body `error: "CSRF_ORIGIN_MISMATCH"`. Preserve GET, HEAD and OPTIONS, preserve proper Bearer requests, preserve requests carrying no session cookie, and do not let another `Authorization` scheme bypass the check.

- Established state: a middleware whose deny set is exactly the unsafe cookie-authenticated requests without an allowed origin.
- Drift survived: exempting any request that carries an `Authorization` header, rather than only a verified Bearer credential, is the trap the thirteen-case matrix is built around. An attacker then sends `Authorization: Basic` beside the victim's cookie and skips the check entirely, while every ordinary Bearer and cookie test still passes. Treating a missing `Origin` as permissive is the same mistake in a quieter form.
- Satisfies: `C08`. Consistent with rubric criterion `C08`.

### S10 - Gate issuance by origin, set the cookie correctly, and honour the switch

Refuse cookie issuance to a foreign, `null` or malformed `Origin` even when the exchange itself is public, while allowing a native or scripted exchange that sends no `Origin` at all. Set cookies httpOnly, host-only and `Path=/`; use `twenty-session` over HTTP and the Secure `__Host-twenty-session` over HTTPS, refusing the insecure fallback name over HTTPS; force Secure whenever `SameSite=None`. Clear both names. With `AUTH_COOKIE_SESSIONS_ENABLED=false`, preserve JWT authentication, create no session through token exchange, and neither issue nor extract session credentials.

- Established state: a cookie whose attributes and name are a function of the scheme, and a rollback switch that leaves the row count unchanged.
- Drift survived: `__Host-` is a prefix the browser enforces and the server must also honour. Accepting the insecure name over HTTPS restores exactly the downgrade the prefix exists to prevent, and it is invisible unless the test presents the wrong name deliberately. The feature-off case is asserted by row count, so a switch that skips the cookie while still writing the session row is not off.
- Satisfies: `C09`. Consistent with rubric criterion `C09`.

### S11 - Park the original credential and restore only the matching one

On entering impersonation, park the original live credential in `twenty-impersonator-session`, or its `__Host-` counterpart over HTTPS, without revoking it. On ending impersonation, revoke the presented impersonation session and restore only a parked credential that is still active, non-impersonating and matches the administrator, keeping its original expiry and provider. Return `canRestoreImpersonatorSession: false` for a revoked, mismatched or nested parked credential, and clear the impersonator cookie in every case.

- Established state: an impersonation exit that can only return the administrator to a credential they already held.
- Drift survived: minting a fresh administrator session on exit is the tempting simplification, and it converts the impersonated session into a privilege source. The three negative subcases exist because a restore path that trusts the parked cookie without re-checking revocation, ownership and the nesting flag looks correct on the happy path and grants privilege on each of them.
- Satisfies: `C10`. Consistent with rubric criterion `C10`.

### S12 - Clear local credentials only after real cookie authentication

Once client config loads and reports cookie sessions enabled, probe current-user authentication with `context.skipAuthToken=true` and `fetchPolicy="network-only"`. Enable cookie mode on a successful cookie authentication, and only then delete the local JWT pair. On `UNAUTHENTICATED`, `FORBIDDEN` or a bare `Unauthorized`, renew the existing refresh token once and probe again. A reload holding a usable cookie must not create another session.

- Established state: a one-way migration in which the local credentials survive until the replacement is proven to work.
- Drift survived: deleting the token pair when the exchange is issued, rather than when the cookie authenticates, strands every user whose deferred exchange has not completed: the old credential is gone and the new one is not yet valid. The group asserts the deferred case directly. The reload subcase catches the opposite error, an effect that re-runs issuance whenever it mounts.
- Satisfies: `C11`. Consistent with rubric criterion `C11`.

### S13 - Distinguish refusal from failure, and finish a pending sign-out first

Treat a transport failure and an unrelated GraphQL error as neither success nor authentication refusal: retain the local credentials and allow the effect to retry later. Complete a pending server sign-out before attempting migration. When the feature is disabled, clear the cookie-mode flag while preserving a still-valid local token pair.

- Established state: a boot effect whose only destructive action is gated on an authenticated cookie.
- Drift survived: collapsing every error into the refusal branch means one network blip deletes credentials and renews a refresh token that did not need renewing. Collapsing it the other way, into success, enables cookie mode with no working cookie. The disabled case is asserted for credential survival, so a rollback that clears the flag and the token pair together makes the switch unsafe to flip back.
- Satisfies: `C12`. Consistent with rubric criterion `C12`.

### S14 - Keep deliberate headerless probes headerless

Ensure a probe marked headerless attaches no stale Bearer credential and triggers no automatic renewal or replay. Send ordinary requests that hold no local token pair with credentials included so they authenticate through the cookie. Let an error from a revoked cookie reach the client rather than being absorbed by the transport.

- Established state: an Apollo link chain in which the probe's own context decides whether a credential is attached.
- Drift survived: the auth link that attaches whatever token it finds and the error link that renews on any authentication error are each individually reasonable and jointly defeat the probe: the probe is answered from the stale Bearer credential, reports success, and the migration concludes the cookie works when it was never exercised. Swallowing the revoked-cookie error hides the one signal the client needs to sign the user out.
- Satisfies: `C13`. Consistent with rubric criterion `C13`.

### S15 - Treat a cookie-only browser as logged in for SSE

Report a cookie-authenticated browser holding no token pair as logged in, and let it establish and reconnect a `graphql-sse` subscription with credentials included, including recovery after a real 503 through the production reconnect callback. Preserve the existing disposal policy at a retry count greater than ten, and preserve token-mode behaviour for missing, valid and expired access tokens, renewing an expired one through the submitted resolver.

- Established state: one login predicate that both the token era and the cookie era satisfy, with the retry policy untouched.
- Drift survived: the deleted `useHasAccessTokenPair` hook is the shape of this bug. Any surviving predicate that equates the presence of a local token pair with being logged in reports a cookie-only user as signed out, which disposes the stream on the first reconnect and looks like an ordinary session timeout. Retry counts 1, 4 and 11 are asserted together, so widening the disposal threshold while fixing the predicate trades one failure for another.
- Satisfies: `C14`. Consistent with rubric criterion `C14`.

### S16 - Ship a repeatable upgrade that enforces integrity

Provide `CreateUserSessionCoreTableFastInstanceCommand.up(queryRunner)` and `.down(queryRunner)` at the published path, with `up` idempotent so a repeated upgrade preserves existing rows. Enforce a unique token hash and the required storage fields, and cascade deletion when the user, workspace or membership is removed. Keep the runtime entity mapping in agreement with the schema the command creates, and make a `down` followed by an `up` a clean installation that still permits authentication.

- Established state: a migration that is safe to re-run and a schema the entity actually matches.
- Drift survived: the entity and the migration are written separately and drift silently. A column nullable in one and required in the other, or a relation without the cascade the contract names, passes every service-level test because the service never exercises the constraint. Re-running a non-idempotent `up` destroys the rows it was supposed to preserve, which only the repeat subcase reaches.
- Satisfies: `C15`. Consistent with rubric criterion `C15`.

### S17 - Accept opaque credentials from the cookie only

Make `AccessTokenService.validateTokenByRequest` accept an opaque credential only when it arrives in the session cookie, and answer `UNAUTHENTICATED` to `Bearer sess_...`. Keep a verified JWT Bearer credential taking precedence, including over an invalid cookie presented alongside it. Treat missing credentials as forbidden, and a revoked or expired cookie as unauthenticated.

- Established state: a single entry point whose accepted credential set is the union of verified JWT Bearer and live cookie, and nothing else.
- Drift survived: accepting `sess_` from the `Authorization` header is the natural generalisation and it undoes the migration, because an opaque credential readable by script is exactly the localStorage exposure the task removes. The precedence subcase catches the inverse: a resolver that checks the cookie first rejects a valid Bearer request whenever a stale cookie is also present.
- Satisfies: `C16`. Consistent with rubric criterion `C16`.

## Red lines

- Editing `yarn.lock`, or relocating any path in `config['required_files']`. Both take the run to `score: null` rather than to a low score.
- Moving, renaming or re-exporting a production module the frozen suite imports by literal `src/...` path. The suite resolves those paths directly against the copied subject tree.
- Upgrading a dependency or fetching an implementation. The environment is offline and the cache is pinned.
- Editing or adding tests in the expectation that they will be graded. The verifier materialises its own suite from `config['source_files']` under its own `rootDir` and never collects candidate tests.
- Accepting an opaque `sess_` credential from the `Authorization` header on any path.
- Reading a refresh-token identifier before verifying the JWT that carries it.
- Writing a session row while `AUTH_COOKIE_SESSIONS_ENABLED=false`.

## Rejected routes

Each route below is a plausible implementation that a reviewer might accept and the graded surface rejects. The named control is the check that catches it.

| rejected route | why it looks correct | control that rejects it |
| :-- | :-- | :-- |
| Store the session credential rather than its hash | every behavioural test passes unchanged | `C01` |
| Issue a new session on every renewal | correct for any single renewal | `C02` |
| Enforce expiry only where the row is read | correct on every cold lookup | `C03` |
| Use a fixed activity throttle constant | satisfies the five-minute bound | `C04` |
| Write activity as a blind upsert | keeps sessions fresh under load | `C04`, `C06` |
| Revoke by session id without an owner check | a clean repository call | `C05` |
| Delete the row and leave its cache entry | the row is authoritative | `C05`, `C06` |
| Invalidate the cache before deleting the row | ordering looks incidental | `C06` |
| Read the refresh-token identifier before verifying it | identical on every honest token | `C07` |
| Exempt any request carrying an `Authorization` header | Bearer clients keep working | `C08` |
| Treat a missing `Origin` as permissive | avoids breaking native clients | `C08` |
| Accept the insecure cookie name over HTTPS | a tolerant fallback | `C09` |
| Skip the cookie but still write the session row when disabled | the user sees JWT behaviour | `C09` |
| Mint a fresh administrator session when impersonation ends | restores access reliably | `C10` |
| Delete the local token pair when the exchange is issued | the cookie is on its way | `C11` |
| Treat any error during the probe as authentication refusal | fails safe, renews and retries | `C12` |
| Attach the stored Bearer token to every outgoing request | one uniform auth link | `C13` |
| Equate an absent local token pair with being logged out | true for the entire token era | `C14` |
| Let the entity and the migration define the schema separately | both compile and both run | `C15` |
| Accept `Bearer sess_...` alongside the cookie | one credential, two transports | `C16` |
| Check the cookie before the Bearer credential | cookies are the new default | `C16` |

## Reconciliation

The trajectory step set is `{S1..S17}`. The graded group set named by the steps is `{C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16}`, which is exactly the key set of `tests/test_weights.json` and exactly the key set of `config['groups']` in `tests/config.json`, in both directions and with no surplus on either side. S1 binds the preconditions rather than a group, which is why seventeen steps close over sixteen groups.

Every manifest row D1 through D16 is named by at least one step, and every step names at least one manifest row. The rubric criterion ids in `tests/rubric.json` are the same sixteen identifiers as the groups; they are cited for consistency only and contribute nothing to the deterministic reward, because that file sets `contributes_to_reward` to `false`.

The exclusions in the Scope boundary section appear in no step, matching `instruction.md`, which names them as outside scope.

Open gaps recorded against this bundle: `solution/grounding.yaml` and `solution/recompute.py` are absent, so this file is hand-derived and not regenerated; no feasibility bundle exists, so the rejected routes above are reasoned from committed bytes rather than measured against executed negative controls.
