# Migrate Twenty browser authentication to server sessions

In `/workspace`, replace browser reliance on localStorage JWT pairs with opaque, httpOnly, server-persisted sessions. Preserve supported Bearer clients and legacy JWT exchanges. Keep the integration interfaces below.

The offline environment provides Node 24.5.0, Yarn 4.13.0, pinned dependencies, PostgreSQL 15 and Redis. Run `prepare-twenty /workspace` to materialize dependencies from `/opt/twenty-cache`; no registry or Yarn archive cache is provided. Do not upgrade dependencies or fetch an implementation. In each submitted `twenty-shared`, `twenty-emails` and `twenty-client-sdk` package, run `node /workspace/node_modules/vite/bin/vite.js build`. Verification uses these JavaScript builds without declaration generation. Server/frontend source and required libraries are included; documentation websites and frontend public media are omitted.

## Required behavior

1. **Sessions.** Generate distinct, unpredictable `sess_` credentials with at least 32 URL-safe suffix characters (`A-Z`, `a-z`, `0-9`, `_`, `-`); persist only lowercase hexadecimal SHA-256 hashes. Workspace sessions require workspace and membership; workspace-agnostic sessions require neither. Impersonation requires workspace and both membership identities. Resolve to the existing `ACCESS` or `WORKSPACE_AGNOSTIC` payload, preserving scope and provider.
2. **Renewal and fixation.** `AuthResolver.renewToken` bridges legacy renewal to sessions. Session issuance is best effort alongside successful legacy exchanges. Reuse a matching live session without creating rows or setting cookies. A changed user, workspace or impersonation scope replaces and revokes it, as does fresh sign-in. A transient issuance failure during renewal must preserve the legacy exchange result and existing cookie.
3. **Expiry.** Enforce absolute and idle deadlines on database and cache paths, rejecting credentials at or past either deadline. Defaults: 180 days absolute, 30 days idle, one day impersonation lifetime. Active-session listings exclude other users, revoked sessions and expired sessions.
4. **Activity.** Coalesce persistent activity writes during request bursts. The throttle interval for request-triggered activity updates must not exceed half the idle timeout or five minutes, whichever is shorter. Continuous activity must keep short-idle sessions usable without extending absolute expiry or restoring a concurrently revoked session.
5. **Revocation.** Support owner-only revocation, revoke-all and all-except-current. Invalidate healthy Redis entries, preserve other users' sessions and make repeated revocation idempotent.
6. **Races.** After revocation completes, subsequent authentication must reject the credential, including when revocation overlapped cache fills or activity updates. Already-authorized in-flight requests may finish. Redis read-through TTL must not exceed 60 seconds.
7. **Sign-out.** Attempt valid refresh-token revocation despite session-revocation failure, then propagate the original session-storage error. Verify JWTs before using token identifiers. An invalid/forged refresh JWT alone is a successful no-op that revokes nothing. Clear the session cookie only if presented.
8. **Request Origin.** Unsafe cookie-authenticated requests require same-origin or an explicitly allowed deployment Origin, with normalized default ports. Reject missing, malformed, `null` and foreign origins with HTTP 403 and `error: "CSRF_ORIGIN_MISMATCH"`. Preserve GET/HEAD/OPTIONS, proper Bearer requests and requests without session cookies; other Authorization schemes do not bypass this check.
9. **Cookies and rollback switch.** Refuse issuance for foreign, `null` or malformed Origins even for public exchanges; allow native/scripted exchanges without an Origin. Cookies are httpOnly, host-only and `Path=/`. HTTP uses `twenty-session`; HTTPS uses Secure `__Host-twenty-session` and rejects the insecure fallback name. `SameSite=None` forces Secure. Clearing removes both names. When `AUTH_COOKIE_SESSIONS_ENABLED=false`, preserve JWT authentication without issuing or extracting session credentials or creating sessions through token exchange.
10. **Impersonation.** Retain the original live credential in `twenty-impersonator-session` (HTTPS: its `__Host-` counterpart), without revoking it. Ending impersonation revokes the presented impersonation session. Restore only the matching active, non-impersonating administrator credential with its original expiry/provider; never mint privilege from the impersonated session. Revoked, mismatched or nested parked credentials return `canRestoreImpersonatorSession:false`. Always clear the impersonator cookie.
11. **Browser migration.** After config loads and enables sessions, probe current-user authentication with `context.skipAuthToken=true`, `fetchPolicy="network-only"`. Cookie authentication enables cookie mode. On `UNAUTHENTICATED`, `FORBIDDEN` or bare `Unauthorized`, renew the existing refresh token once and probe again. Delete local JWTs only after successful cookie authentication. Reloading with a usable cookie creates no session.
12. **Retry/sign-out.** Transport and unrelated GraphQL failures preserve credentials and allow later effect retry. Complete pending server sign-out before migration. Disabling the feature clears cookie mode while preserving a valid local token pair.
13. **Apollo.** Headerless probes attach no stale Bearer token and trigger no automatic renewal/replay. Ordinary requests without local tokens include credentials and use cookies. Revoked-cookie errors must reach the client.
14. **SSE.** Cookie-only users are logged in and can establish/reconnect `graphql-sse` subscriptions with credentials included. Missing local tokens do not imply logout. Preserve disposal after retry count greater than ten and token-mode behavior for missing, valid and expired access tokens.
15. **Schema.** Provide repeatable `core.userSession` upgrade/rollback, unique token hashes, required fields and cascading deletion for user, workspace or membership removal. Entity mappings must match. Repeated upgrade preserves data; down/up allows clean installation.
16. **Request authentication.** `AccessTokenService.validateTokenByRequest` accepts opaque tokens only via cookies; `Bearer sess_...` is `UNAUTHENTICATED`. Verified JWT Bearer credentials retain precedence. Missing credentials are forbidden; revoked/expired cookies are unauthenticated.

## Integration contract

Keep existing APIs at their current paths. Add under `packages/twenty-server/src/engine/core-modules/user-session/`:

- `user-session.entity.ts`: TypeORM `UserSessionEntity` for `core.userSession`, with `id`, `tokenHash`, `userId`, `workspaceId`, `userWorkspaceId`, `authProvider`, `isImpersonating`, `impersonatorUserWorkspaceId`, `impersonatedUserWorkspaceId`, `userAgent`, `ipAddress`, `expiresAt`, `lastActiveAt`, `revokedAt`, `revokedReason`, `createdAt`, `updatedAt`, and `user`, `workspace`, `userWorkspace` relations. Dates are `Date`; nullable fields may be null.
- `services/user-session.service.ts`: `UserSessionService`, constructor dependencies in order: session repository, app-token repository, `CacheStorageService`, `TwentyConfigService`, `JwtWrapperService`, event emitter, `UserSessionCookieService`.
- `services/user-session-cookie.service.ts`: `UserSessionCookieService`, constructed with `TwentyConfigService`.

Session-service methods:

```ts
createSession(input: {
  userId: string; workspaceId?: string | null; userWorkspaceId?: string | null;
  authProvider: AuthProviderEnum; origin: 'sign_in' | 'renewal_bridge';
  isImpersonating?: boolean; impersonatorUserWorkspaceId?: string | null;
  impersonatedUserWorkspaceId?: string | null; userAgent?: string | null;
  ipAddress?: string | null;
}): Promise<{ sessionToken: string; session: UserSessionEntity }>;
issueSessionForTokenPair(input: {
  tokenPair: AuthTokenPair; request: Express.Request;
  origin: 'sign_in' | 'renewal_bridge';
}): Promise<void>;
resolveSession(token: string): Promise<{
  payload: AccessTokenJwtPayload | WorkspaceAgnosticTokenJwtPayload;
  authenticatedAt: Date; expiresAt: Date;
}>;
findSessionByToken(token: string): Promise<UserSessionEntity | null>;
findActiveSessionsForUser(userId: string): Promise<UserSessionEntity[]>;
revokeSessionByToken(token: string, reason: UserSessionRevokedReason): Promise<boolean>;
revokeSessionByIdForUser(input: {
  sessionId: string; userId: string; reason: UserSessionRevokedReason;
}): Promise<boolean>;
revokeAllSessionsForUser(input: {
  userId: string; reason: UserSessionRevokedReason; exceptSessionId?: string;
}): Promise<number>;
signOut(input: { sessionToken?: string; refreshToken?: string }): Promise<void>;
```

`UserSessionRevokedReason`: `USER_SIGN_OUT`, `USER_REVOKED`, `SUPERSEDED`, `PASSWORD_CHANGED`, `IMPERSONATION_ENDED`. Invalid sessions throw existing `AuthException` with `code: "UNAUTHENTICATED"`.

Cookie methods: `extractSessionTokenFromRequest(req)`, `extractImpersonatorSessionTokenFromRequest(req)`, `hasSessionCookie(req)`, `attachSessionTokenToResponse(res, token, expiresAt)`, `attachImpersonatorSessionTokenToResponse(res, token)`, `clearSessionCookie(res)`, `clearImpersonatorSessionCookie(res)`. Extraction returns a string or undefined. Attachment and clearing use the existing Express response API.

Add `CookieSessionCsrfMiddleware` at `src/engine/middlewares/cookie-session-csrf.middleware.ts`, constructed with config, cookie service and JWT wrapper, exposing `use(req,res,next)`. Append session service and cookie service, in that order, after `AccessTokenService`'s seven dependencies and `AuthResolver`'s 25 dependencies (`RenewTokenService` remains sixth). Preserve `renewToken(args, {req})` and `signOut({req}, refreshToken?)`. Append config, session service and cookie service after `ImpersonationService`'s five dependencies; expose `stopImpersonation({impersonationContext,workspaceId,request})` returning `{canRestoreImpersonatorSession:boolean}`.

Provide `CreateUserSessionCoreTableFastInstanceCommand.up(queryRunner)` and `.down(queryRunner)` at `packages/twenty-server/src/database/commands/upgrade-version-command/2-27/2-27-instance-command-fast-1785518325511-create-user-session-core-table.ts`; `up` is idempotent. The existing `uuid-ossp` extension is available.

Frontend interfaces under `packages/twenty-front/src/modules/`:

- `auth/effect-components/CookieSessionBootEffect.tsx`: exported React effect `CookieSessionBootEffect`.
- `auth/states/isCookieAuthActiveState.ts`, `auth/states/isPendingServerSignOutState.ts`, `client-config/states/isCookieSessionEnabledState.ts`: correspondingly named Jotai exports with `.atom`.
- Preserve paths/shapes of `tokenPairState`, `clientConfigApiStatusState`, `ApolloFactory.getClient()`, `useIsLogged()`, `SSEClientEffect`, `useHandleSseClientConnectionRetry().handleSseClientConnectionRetry(count)`, `sseClientState`, `shouldDestroyEventStreamState`.
- Preserve `{accessOrWorkspaceAgnosticToken:{token,expiresAt},refreshToken:{token,expiresAt}}` and localStorage key `tokenPairState`.

Configuration: `AUTH_COOKIE_SESSIONS_ENABLED`, `SESSION_ABSOLUTE_LIFETIME`, `SESSION_IDLE_TIMEOUT`, `AUTH_COOKIE_SAME_SITE`, `AUTH_COOKIE_ALLOWED_ORIGINS`, `SERVER_URL`, `FRONTEND_URL`, existing `APP_SECRET`. Durations follow `ms`; allowed origins are comma-separated. `ConfigVariables` at `src/engine/core-modules/twenty-config/config-variables.ts` declares defaults, with cookie sessions disabled. `ClientConfigService.getClientConfig()` publishes `isCookieSessionEnabled`; preserve constructor order: config, domain server config, AI model registry, maintenance mode services. Frontend `useClientConfig().fetchClientConfig()` loads `/client-config` into `isCookieSessionEnabledState`; config and browser integration must use the switch.

The sixteen groups receive equal deterministic reward. Verification uses real PostgreSQL and Redis, submitted entity metadata and upgrade code, local HTTP, production Apollo and mounted React/Jotai effects. Identity, profile and token-issuance dependencies outside the migration are local fixtures. No external mail, SSO, analytics, model or ClickHouse services are needed. No particular cache algorithm or implementation text is required.

Complete application startup, graphical-browser testing, root provider mounting, metadata resync and unrelated subsystems are outside scope. Also excluded: Redis deletion failure while reads succeed (revocation may lag its 60-second TTL), sign-ins committed after revoke-all's snapshot, overflowing lifetime values and idle-expired-row cleanup timing.

Empty submissions or source trees byte-identical to the supplied unmigrated snapshot earn 0. Changed submissions with unavailable integration interfaces or incompatible toolchain, runtime, dependency cache or verifier setup are ungraded (`score: null`).
