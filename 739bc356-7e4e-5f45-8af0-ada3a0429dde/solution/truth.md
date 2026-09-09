# TRUTH.md - MorAlekss__cli-migration-test-3-5

## Defect

The currency, geocoding, news, and weather integrations perform blocking HTTP requests. Calling them from an asynchronous application can block the event loop and prevent unrelated work from progressing while a remote service responds.

The migration specifically requires the HTTP operations to use `httpx` asynchronously while preserving the existing endpoints, request parameters, response validation, JSON extraction, and higher-level results.

## Root cause

Each integration imports the synchronous `requests` library and calls its blocking request API. Functions that depend on those requests are synchronous as well, including helper functions that invoke another HTTP-backed function internally. Merely replacing the imported library would not make the operations asynchronous: the request must be awaited, and every caller in the local call chain must propagate that asynchronous contract.

## Solution shape

A correct implementation must have these properties:

- Currency, geocoding, news, and weather HTTP traffic uses the asynchronous `httpx` API rather than `requests`.
- Every public operation that performs HTTP I/O, directly or through another local function, is awaitable.
- HTTP requests are awaited rather than merely returning coroutine objects.
- HTTP client resources are closed reliably, including when a request, status check, or response processing raises.
- The existing remote-service contracts remain unchanged:
  - Currency rates are fetched for the requested base currency.
  - Currency conversion multiplies the supplied amount by the selected target rate.
  - Forward geocoding sends the address and requests JSON output.
  - Reverse geocoding sends latitude, longitude, and JSON-output parameters.
  - Top-news retrieval uses the existing top-stories endpoint and returns only the first ten entries.
  - Individual news retrieval uses the requested story identifier.
  - Weather retrieval uses the city-specific JSON endpoint.
  - Temperature retrieval returns the Celsius value from the same nested response location.
- Every response is checked for an unsuccessful HTTP status before its JSON result is consumed.
- Existing default arguments, URL construction, slicing behavior, dictionary indexing, and exception propagation remain semantically consistent.
- No synchronous `requests` call remains in the migrated integration modules.

## Load-bearing work

- `src/currency.py`
  - Replace blocking currency requests with awaited `httpx` requests.
  - Make rate retrieval awaitable.
  - Make conversion await rate retrieval before performing the existing multiplication.
  - Preserve the default base currency, endpoint shape, status validation, and extraction of the rates mapping.

- `src/geo.py`
  - Replace both blocking geocoding requests with awaited `httpx` requests.
  - Make forward and reverse geocoding awaitable.
  - Preserve the search and reverse endpoints and all existing query parameter names and values.
  - Continue returning each service response’s decoded JSON body after status validation.

- `src/news.py`
  - Replace blocking news requests with awaited `httpx` requests.
  - Make both top-story and individual-story retrieval awaitable.
  - Preserve the endpoint paths and status validation.
  - Continue limiting top-story identifiers to ten while returning an individual story body unchanged.

- `src/weather.py`
  - Replace blocking weather requests with awaited `httpx` requests.
  - Make weather retrieval awaitable.
  - Make temperature retrieval await the weather helper before indexing its result.
  - Preserve the city URL, JSON format selection, status validation, and Celsius-field extraction.

## Solution space

Several implementation strategies are valid if they retain the required behavior:

1. **A short-lived asynchronous client per operation**
   - Open a client within each HTTP-backed function and close it through an asynchronous context manager.
   - This is simple and gives each operation clear resource ownership.

2. **A shared client with explicit lifecycle management**
   - Reuse one asynchronous client across calls for connection pooling.
   - The application must provide deterministic startup and shutdown handling so sockets are not leaked or used after closure.

3. **Client injection**
   - Accept or otherwise provide an asynchronous client from the caller while preserving compatibility with the intended public API.
   - This can improve testability and pooling, but ownership and closure responsibilities must be unambiguous.

4. **A private request helper**
   - Centralize client creation, awaiting, status validation, or JSON decoding in an internal helper.
   - Service-specific functions must still preserve their exact URLs, parameters, transformations, and awaitable behavior.

5. **Directly asynchronous dependent helpers**
   - Higher-level functions such as conversion and temperature lookup may remain thin wrappers, provided they await their lower-level helpers and return the same computed values.

Different client-lifetime or factoring choices are acceptable. A synchronous wrapper around asynchronous work is not equivalent because it can conflict with an already-running event loop and defeats the requested asynchronous API.

## Ordered plan

1. Inspect all four service modules and identify both direct HTTP calls and functions that depend on HTTP-backed helpers.
2. Replace the blocking HTTP dependency in those modules with `httpx`.
3. Convert each direct network-facing function to an asynchronous callable.
4. Perform each outbound request through an asynchronous client and await completion.
5. Ensure the client is always closed, preferably using structured asynchronous resource management or an application-managed lifecycle.
6. Retain each original endpoint, path component, query parameter, and default argument.
7. Retain status checking before JSON processing.
8. Propagate asynchrony through local call chains:
   - Conversion must await rate retrieval.
   - Temperature lookup must await weather retrieval.
9. Preserve post-processing exactly: rates-map extraction, conversion multiplication, ten-item news truncation, unchanged JSON returns, and nested Celsius extraction.
10. Update or verify test doubles so they model asynchronous client usage rather than masking a missing await.
11. Run the complete existing suite and, where possible, add checks that invoke the migrated functions from an event loop and confirm client cleanup and failure propagation.

## Pitfalls

- Changing the import but still using a synchronous client or request method.
- Declaring a function asynchronous but forgetting to await the request.
- Forgetting to await `get_rates` or `get_weather`, causing downstream code to index or multiply a coroutine.
- Returning the response object or coroutine instead of the established decoded or transformed value.
- Removing the status check, which would silently change error handling for non-success responses.
- Altering endpoint paths, URL formatting, query parameter names, or the weather format selector.
- Returning all top stories instead of retaining the ten-item limit.
- Changing the currency default or conversion arithmetic.
- Failing to close clients on success and exception paths.
- Creating a global client without a reliable shutdown mechanism.
- Calling an event-loop runner inside a nominally synchronous compatibility wrapper; this fails under an existing event loop and does not provide true asynchronous composition.
- Using blocking work in a thread as the primary migration while continuing to send requests through `requests`; that does not satisfy the required library migration.
- Updating only currency and news while leaving geocoding and weather on the blocking stack.
- Writing mocks that are synchronous even though production client operations are awaitable, or patching the wrong import location.
- Catching and replacing HTTP or JSON errors when the prior behavior allowed them to propagate.

## Cheat surface

A superficial change could pass weak tests without completing the migration by:

- Marking functions asynchronous while retaining blocking `requests` calls.
- Returning hard-coded payloads or computed values rather than issuing the service request.
- Detecting test inputs or mocked objects and using a special code path.
- Leaving some modules on `requests` because tests happen to cover only currency and news.
- Omitting awaits while tests use permissive mocks that do not expose coroutine misuse.
- Skipping status validation because mocked responses are always successful.
- Leaking clients because tests do not inspect resource cleanup.
- Replacing network behavior with fixtures in production code.
- Modifying or weakening tests instead of preserving application behavior.
- Keeping dead `requests` code or a fallback path that production execution can still reach.

Verification should therefore inspect implementation structure as well as outputs: the actual network path must use awaited `httpx` operations in every affected module.

## Success criteria

- `src/currency.py`, `src/geo.py`, `src/news.py`, and `src/weather.py` no longer use `requests` for outbound HTTP calls.
- All functions that directly or indirectly perform those calls can be awaited.
- The outbound `httpx` operations themselves are awaited.
- HTTP clients are deterministically closed or are managed by an explicit reusable lifecycle.
- Currency requests preserve their base-currency path, rates extraction, default, and conversion result.
- Forward and reverse geocoding preserve their endpoints and query parameters.
- News requests preserve their endpoints, individual-story result, and ten-story limit.
- Weather requests preserve their city-specific JSON URL and nested Celsius extraction.
- Non-success HTTP responses still raise before JSON data is returned or transformed.
- Existing malformed-payload and lookup failures continue to propagate naturally unless prior behavior explicitly handled them.
- The full existing test suite passes on the migrated tree.
- Tests or inspection confirm that no blocking HTTP call occurs on these execution paths and that dependent helpers await rather than manipulate coroutine objects.

## Verification

Run the existing test suite on the migrated tree and confirm it passes; this bundle does not enumerate it.

## Provenance

```yaml
uuid: 739bc356-7e4e-5f45-8af0-ada3a0429dde
instance_id: MorAlekss__cli-migration-test-3-5
fix_patch_sha256: 4af44f4115215cec41a0c152ae404fce638d7ce9dbdc6be7ca3e3e69d7d6c830
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
