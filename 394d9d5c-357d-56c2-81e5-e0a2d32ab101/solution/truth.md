# TRUTH.md - dan-nor98__pypostboy-45

## Defect

The backend is implemented around Flask-specific application, routing, request-context, session, response, static-file, and development-server APIs. It therefore does not satisfy the requirement to run as a Django 5.0.6 WSGI application.

Observable consequences include:

- There is no Django settings module, URL configuration, or WSGI entry point.
- Route modules expose Flask blueprints rather than Django views.
- Authentication depends on Flask globals and Werkzeug password helpers.
- Shared responses are Flask response tuples rather than Django responses.
- Proxy configuration depends on a Flask application context.
- The root launcher starts Flask’s server.
- Flask and its CORS extension remain runtime dependencies.
- Existing callers and tests that use the historical application factory and test-client surface would break if Flask were simply removed without compatibility handling.

## Root cause

Framework concerns are distributed throughout the backend rather than isolated at the entry point:

- Route registration, method dispatch, request-body parsing, and response construction use Flask conventions.
- Current-user state is stored in Flask request globals, while identity is read through Flask header, cookie, and session abstractions.
- Configuration is loaded directly into a Flask application object and read later through Flask context-local configuration.
- Static serving and SPA fallback behavior are delegated to Flask utilities.
- Password storage and verification use Werkzeug formats.
- The test suite relies on parts of Flask’s convenient client and response interface in addition to the public HTTP behavior.

A migration must therefore replace the complete HTTP integration layer while preserving the SQLite repository and service behavior beneath it.

## Solution shape

A correct destination has these properties:

- Django 5.0.6 is the declared web-framework dependency; Flask and the Flask CORS extension are no longer required.
- The project has conventional Django settings, URL routing, and WSGI modules.
- The existing application factory remains usable. It accepts the same built-in configuration names, mappings, custom configuration objects, and import paths, configures the existing database layer, and returns a callable WSGI-facing application.
- Existing test code can still obtain a client from the factory result and inspect response bytes, media type, status, headers, and decoded JSON in the legacy style.
- Every existing endpoint retains its path, accepted HTTP methods, status codes, response shape, ownership checks, validation, and repository/service calls.
- Unsupported methods produce a proper method-not-allowed response rather than accidentally executing a view.
- JSON request parsing is tolerant in the same way as before: missing, malformed, non-object, or undecodable bodies behave as empty objects where the old handlers did.
- API writes remain usable by the existing browser/client architecture, either through explicit CSRF exemption or an equivalent correctly configured API-CSRF strategy.
- Authentication resolves identity from the same headers, session key, and cookies, caches it only for the active request, and falls back to the default local user when no identity is supplied.
- Registration stores passwords in a Django-supported format. Login continues to verify password hashes produced by older releases, including the relevant Werkzeug PBKDF2 and scrypt forms. Successful verification may transparently upgrade an old or weak hash.
- Session login, registration, and logout remain functional across client requests and expose only public user fields.
- Middleware establishes request-local context safely under concurrent and asynchronous execution, performs API authentication behavior, restores context afterward, and applies the expected security and CORS headers.
- Collection, saved-request, request-instance, import, and proxy behavior remains delegated to the existing repositories and services.
- Static files retain MIME types, the root serves the application shell, extensionless unknown paths use the SPA fallback, missing asset-like paths return 404, the favicon keeps its caching behavior, and traversal outside the public directory is rejected.
- Proxy timeout comes from Django-visible runtime configuration and still falls back to the base configuration outside a customized application.
- The command-line launcher serves the Django WSGI callable while retaining environment-based port selection and occupied-port retry behavior.
- Documentation consistently describes Django rather than Flask.

## Load-bearing work

- `README.md` — Describe the backend as Django-based, document the Django project layout and configuration model, update setup examples and security notes, and remove stale Flask-oriented descriptions.
- `app.py` — Remain a thin executable entry point, construct the migrated application, run its WSGI callable with a Django-compatible development server, and preserve port retry/error behavior.
- `django/__init__.py` — If the repository supports operation without an externally importable Django package, identify the local compatibility runtime and expose version information consistent with the required framework level.
- `django/conf/__init__.py` — Provide lazy loading of the configured settings module for the compatibility-runtime route, including access to uppercase settings and predictable failure when no settings module is selected.
- `django/contrib/__init__.py` — Make the local contribution namespace importable when the compatibility route is used.
- `django/contrib/auth/hashers.py` — Provide secure generation and constant-time verification of Django-style password hashes, unusable-password handling, and verification of legacy Werkzeug PBKDF2 and scrypt hashes. Malformed or unsupported hashes must fail safely, and verified legacy hashes may be upgraded through the normal callback mechanism.
- `django/contrib/contenttypes/__init__.py` — Supply the importable content-types namespace required by the selected settings.
- `django/contrib/sessions/__init__.py` — Supply the importable sessions namespace required by the selected settings.
- `django/contrib/sessions/middleware.py` — Ensure requests have mutable session state in the compatibility runtime; a full-Django implementation may instead rely directly on Django’s signed-cookie session middleware.
- `django/core/__init__.py` — Make the local core namespace importable.
- `django/core/handlers.py` — For a compatibility runtime, translate WSGI environments into request objects, parse headers and cookies, build the middleware chain, route requests, convert not-found exceptions to 404 responses, and emit valid WSGI responses.
- `django/core/servers/basehttp.py` — For a compatibility runtime, expose a blocking development-server adapter capable of serving the WSGI application.
- `django/core/wsgi.py` — Load settings and construct the configured WSGI handler.
- `django/http/__init__.py` — Supply the HTTP response subset needed by the application: byte content, status and headers, JSON serialization, file responses, 404 signaling, and method-not-allowed responses.
- `django/middleware/__init__.py` — Make the middleware namespace importable.
- `django/middleware/security/__init__.py` — Supply the security-middleware contract needed by the configured middleware chain, or delegate to the real framework implementation.
- `django/urls/__init__.py` — Support Django-style path declarations and the integer and remainder-of-path converters used by the application, including exact matching and converted keyword arguments.
- `django/utils/module_loading.py` — Support importing configuration and middleware objects from dotted Python paths.
- `django/views/__init__.py` — Make the views namespace importable.
- `django/views/decorators/__init__.py` — Make the decorator namespace importable.
- `django/views/decorators/csrf.py` — Provide or expose the CSRF exemption contract used by JSON API write views.
- `pypostboy/app.py` — Convert the application factory from Flask construction to Django WSGI setup, preserve all accepted configuration forms, synchronize mutable runtime settings, configure the existing database singleton, and provide only the compatibility facade needed by historical entry points and tests.
- `pypostboy/auth.py` — Remove Flask globals, read headers from Django request metadata and cookies/session from Django request attributes, support explicit or request-context-based calls, cache users on the request itself, and preserve default-local-user behavior.
- `pypostboy/config.py` — Keep the environment configuration objects and values while making their documentation and use framework-neutral or Django-oriented.
- `pypostboy/db/connection.py` — Continue accepting the resolved application configuration and support both an injected connection and path-based database setup without assuming a Flask application object.
- `pypostboy/djangoapp/context.py` — Maintain current-request state with an execution-context-safe mechanism and expose balanced bind, lookup, and restore operations.
- `pypostboy/djangoapp/middleware.py` — Bind request context, perform API identity handling, always clean up the binding, and add/remove the required security and CORS headers on both normal and authentication-error responses.
- `pypostboy/djangoapp/request.py` — Centralize safe decoding of JSON object bodies and return an empty mapping for blank, malformed, undecodable, or non-object payloads.
- `pypostboy/http/responses.py` — Produce Django JSON responses while retaining the standard success/data and failure/error envelopes, status selection, extra fields, and old helper aliases.
- `pypostboy/routes/auth.py` — Replace the blueprint with request-taking Django views; preserve current-user, login, registration, and logout behavior; use Django-compatible password APIs; manipulate Django session state; and avoid exposing password hashes.
- `pypostboy/routes/collections.py` — Convert collection handlers to Django views, pass the request-derived user ID into all repository operations, preserve validation and error-to-status mapping, and protect write semantics from CSRF incompatibility.
- `pypostboy/routes/imports.py` — Convert import handling to a Django view, parse JSON through the shared helper, preserve cURL and Postman branches, and scope database imports to the current user.
- `pypostboy/routes/instances.py` — Convert request-instance handlers to Django views while preserving ownership, CRUD behavior, status codes, and JSON envelopes.
- `pypostboy/routes/proxy.py` — Convert the proxy endpoint to a Django JSON view while preserving its intentionally distinct payload shape and the distinction between validation and outbound-proxy failures.
- `pypostboy/routes/requests.py` — Convert saved-request handlers to Django views and preserve create, retrieve, update, delete, duplicate, move, reorder, and collection-listing behavior with user isolation.
- `pypostboy/routes/static.py` — Replace Flask file helpers with Django responses, retain favicon and SPA behavior, detect content types, and perform canonical path containment checks before opening files.
- `pypostboy/services/proxy_service.py` — Read the outbound timeout from Django settings without requiring a Flask application context and retain the existing default.
- `pypostboy/settings.py` — Define the project’s Django settings: hosts, URL and WSGI modules, timezone, required installed applications and middleware, signed-cookie sessions, framework database metadata, public directory, proxy timeout, and request upload limit.
- `pypostboy/urls.py` — Declare every existing public route, apply method-specific dispatch where paths share handlers, return 405 with allowed methods when appropriate, and place the catch-all SPA route last.
- `pypostboy/wsgi.py` — Select the project settings module and expose the configured Django WSGI application for deployment.
- `requirements.txt` — Pin Django to 5.0.6, retain the HTTP client and test dependencies, and remove Flask-specific packages.

## Solution space

Valid implementations are not limited to one internal structure:

1. **Use Django 5.0.6 directly.**  
   This is the conventional route: depend on the real package, use its request/response, URL, middleware, test-client, session, password, server, and WSGI facilities, and keep only a small PostBoy compatibility facade.

2. **Provide a local compatibility runtime for constrained environments.**  
   A repository-local Django-compatible subset is acceptable if it implements all framework semantics PostBoy actually relies on, reports the intended compatibility level, and does not silently omit routing, sessions, middleware, password security, WSGI, or response behavior. It must remain coherent if the external package is unavailable.

3. **Preserve tests through adapters or migrate tests to native Django interfaces.**  
   A response/client adapter around Django is valid when the existing suite expects Flask-style conveniences. An equally valid implementation can update project-owned tests and callers to native Django interfaces, provided all externally observable application behavior remains unchanged.

4. **Use function-based or class-based Django views.**  
   Either is valid. Method restrictions, arguments from URL converters, CSRF behavior, status codes, and payloads must remain equivalent.

5. **Use explicit per-route method dispatch or Django’s standard method facilities.**  
   Shared paths can be dispatched by a small wrapper, class-based handlers, or separate framework-supported declarations. Unsupported methods must still produce 405 responses and accurate allowed-method metadata.

6. **Use signed-cookie or another correctly configured Django session backend.**  
   Signed cookies avoid introducing Django-managed session tables and match the lightweight architecture. A database or cache-backed session is also valid if migrations, persistence, tests, and deployment setup are complete.

7. **Handle legacy passwords with a custom Django hasher or an authentication-layer verifier.**  
   Either placement is acceptable. New passwords must be securely encoded, old hashes must continue to authenticate, malformed hashes must fail safely, and migration-on-login should be supported where practical.

8. **Use middleware context or pass the request explicitly everywhere.**  
   Explicit request passing is preferable where possible. A context variable is valid for compatibility with deeper code that resolves the current user implicitly, provided it is always reset and is safe under concurrency.

9. **Serve frontend files through Django or deployment middleware.**  
   Production static middleware is acceptable, but local execution and tests must still preserve root, favicon, MIME, 404, SPA fallback, and traversal-protection behavior.

The SQLite repository layer need not be rewritten as Django models. Retaining it is valid and minimizes unrelated data and migration risk.

## Ordered plan

1. **Record the current HTTP contract.**  
   Inventory all paths, methods, response envelopes, status codes, authentication inputs, CORS/security headers, static fallback rules, and application-factory test conveniences.

2. **Install and configure the Django runtime.**  
   Replace Flask dependencies, add project settings and WSGI configuration, choose the session backend, define middleware order, and establish static and upload-limit settings.

3. **Preserve configuration and database initialization.**  
   Refactor configuration resolution so it produces a framework-independent mapping. Ensure all existing selection forms work before constructing the WSGI facade, then configure the current SQLite singleton.

4. **Build request, response, and context primitives.**  
   Add safe JSON parsing, Django JSON envelope helpers, request-local storage, and any legacy client/response adapter required by the suite.

5. **Migrate authentication.**  
   Move identity resolution onto Django request state, preserve header/session/cookie precedence and local fallback, configure sessions, switch new hashes to Django-compatible storage, and add old-hash verification.

6. **Add application middleware.**  
   Bind and restore request context, integrate API authentication behavior, and preserve shared response headers. Verify cleanup on success, 404, validation failure, and raised exceptions.

7. **Convert route modules to Django views.**  
   Start with authentication, then collections and requests, then instances and imports, and finally the proxy. Pass the request explicitly into user resolution and use the shared JSON parser.

8. **Declare URL routing and method restrictions.**  
   Register specific API routes before dynamic and catch-all routes. Verify integer conversion, nested paths, and 405 behavior.

9. **Migrate static and SPA serving.**  
   Add MIME detection and canonical containment checks, then preserve favicon, asset 404, and extensionless fallback behavior.

10. **Update proxy configuration access.**  
    Remove the final Flask context dependency and verify factory overrides affect outbound timeout behavior.

11. **Update launch and deployment entry points.**  
    Expose the WSGI application and point the local server at it while retaining port-selection and retry logic.

12. **Run compatibility and behavior tests.**  
    Exercise both native Django requests and any historical test facade, including sessions across calls, malformed JSON, legacy passwords, wrong methods, unknown routes, traversal attempts, and injected test databases.

13. **Update documentation and remove stale Flask references.**  
    Ensure install, project layout, startup, configuration, and security guidance describe the final runtime accurately.

## Pitfalls

- Merely wrapping the existing Flask application in WSGI does not constitute a Django migration.
- A local package named like the framework can shadow the installed Django distribution. If this approach is used, its supported surface must be deliberate and complete; otherwise native imports and third-party integrations fail unpredictably.
- Django settings are process-global and normally initialized once. Repeated factory calls in tests can leak configuration unless mutable values and database state are synchronized carefully.
- Initializing the WSGI handler before selecting the settings module causes import-order failures.
- Replacing Flask response tuples without updating callers can return tuples from Django views instead of valid response objects.
- Django’s test client and Flask’s client differ in JSON submission, response body attributes, and JSON decoding. Compatibility must be intentional rather than accidental.
- URL declarations do not automatically enforce the old method lists. A view that accepts every method can mutate data or return 200 where the old application returned 405.
- Dynamic routes can capture fixed routes such as reorder operations if route ordering is careless.
- Applying CSRF exemption to only a dispatcher and not the effective write view, or vice versa, can produce unexpected 403 responses.
- Django header lookup through request metadata uses normalized names. Reading Flask-style header keys from the wrong mapping breaks explicit user selection.
- Request-global state implemented with a module variable or thread-local can leak between concurrent requests. Context binding must be restored in a `finally` path.
- Catching authentication exceptions in middleware is ineffective if invalid identities are represented only as a missing user. The selected error contract must be consistent across middleware and views.
- Signed-cookie sessions require a stable secret and correct middleware order. A plain dictionary session shim does not provide persistence by itself.
- Switching password APIs without legacy verification locks out users created by older releases.
- Password comparison must be constant-time, malformed hashes must not crash the request, and memory settings for legacy scrypt verification must be sufficient but bounded.
- Django JSON responses may reject non-mapping top-level values unless configured appropriately. Preserve the actual payload shapes used by each endpoint.
- The proxy endpoint does not use the same success envelope as CRUD endpoints; normalizing it would be a behavior regression.
- Naively joining the public directory and request path permits traversal. Prefix checks must use canonical absolute paths and directory-boundary-aware containment.
- Treating every missing static path as the SPA shell incorrectly returns 200 for missing JavaScript, CSS, images, or other asset-like requests.
- Using a generic “OK” phrase for every WSGI status is invalid or misleading for non-200 responses; a compatibility runtime should emit correct HTTP status lines.
- Updating only comments and dependencies while leaving Flask imports in route or service modules creates a mixed-framework backend.
- Rewriting the SQLite persistence layer into Django models is unnecessary and risks schema, migration, ownership, and serialization regressions.

## Cheat surface

A superficial solution could appear green without satisfying the migration by:

- Keeping Flask as the real server and exposing it behind a Django-named wrapper.
- Adding Django to dependencies while route modules still import and execute Flask.
- Creating stub framework modules that only satisfy imports but omit real session persistence, middleware cleanup, method handling, WSGI correctness, or password security.
- Hard-coding endpoint responses expected by visible tests rather than calling repositories and services.
- Returning the default local user regardless of supplied identity, which hides broken header, cookie, and session handling.
- Disabling authentication or ownership filtering globally to make CRUD tests pass.
- Accepting every HTTP method because tests cover only happy paths.
- Replacing session behavior with per-request dictionaries so a single-request test passes while login persistence fails.
- Dropping legacy password support and testing only newly registered users.
- Serving the SPA shell for all missing paths, masking both missing assets and traversal errors.
- Leaving the production WSGI module unusable while testing only the factory facade.
- Depending on an undeclared globally installed package or, conversely, shadowing the declared framework with an incomplete local substitute.
- Special-casing the test database or proxy timeout rather than honoring the configuration mapping supplied to the application factory.
- Editing or weakening existing tests instead of preserving behavior.

Verification should therefore inspect architecture and dependencies in addition to running endpoint tests.

## Success criteria

A grader can confirm completion when all of the following hold:

- `requirements.txt` pins Django 5.0.6 and contains no Flask or Flask-CORS dependency.
- Backend modules no longer rely on Flask application, request, session, blueprint, response, static-file, CORS, or context-global APIs.
- A valid Django settings module, URL configuration, and importable WSGI application exist.
- The root launcher serves that WSGI application and retains the established port behavior.
- The application factory still supports default, named, mapping, object, import-path, environment-selected, and test-database configuration.
- Existing tests pass unchanged, including tests that use the historical client and response conveniences.
- Every pre-migration endpoint remains reachable at the same path and accepts only the intended methods.
- CRUD, reorder, move, duplicate, instance, import, and proxy operations retain their prior payloads and status codes.
- User ownership remains enforced across collections, requests, instances, and imports.
- Identity resolution works through both supported headers, session state, both supported cookies, and default-local-user fallback.
- Registration and login work with new Django-compatible password hashes, while users with supported legacy Werkzeug hashes can still log in.
- Login and registration persist user identity through the configured session mechanism; logout clears it and restores local-mode behavior.
- Blank and malformed JSON do not produce framework-generated HTML errors where the old API treated them as empty input.
- API responses remain JSON with the expected envelopes; the proxy endpoint retains its separate response contract.
- Shared responses include content-sniffing protection and expected credentialed CORS behavior, without stale CSP headers.
- Root, favicon, ordinary static assets, extensionless SPA routes, missing asset paths, MIME types, and traversal attempts all behave correctly.
- Runtime proxy-timeout overrides are honored.
- Unknown routes return 404, unsupported methods return 405 with allowed-method information, and WSGI responses carry valid status and headers.
- Request context and database state do not leak between requests or repeated test application creation.
- Documentation consistently presents PostBoy as a Django backend and accurately describes startup, structure, configuration, and local-first authentication.

## Verification

Run the existing test suite on the migrated tree and confirm it passes; this bundle does not enumerate it.

## Provenance

```yaml
uuid: 394d9d5c-357d-56c2-81e5-e0a2d32ab101
instance_id: dan-nor98__pypostboy-45
fix_patch_sha256: 8c94313cb18030c7c44915c6f16542e387f47944b0f7a5c8f7679252eafc853e
language: python
targets_total: 0
preserve_total: 0
authored_by: generated
status: unverified_reference
golden_score_measured: null
golden_score_runs: 0
truth_generator: assay.truthgen/kaiju
spec_source: instruction.md
```
