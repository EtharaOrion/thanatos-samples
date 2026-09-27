# truth.md - Repl, MCP SDK 1.4.1 to 2.2.0 dual-era

## Provenance

This is the private golden-trajectory projection for bundle `7035333c-d9a3-530d-89f4-4ff9e95e6f36`, the `ModelContextProtocol` 1.4.1 to 2.2.0 migration of `yllibed/repl` from base commit `a04f10b0e2c2ee68debb913d01aab702719d43f4` to reference commit `bb56e2d2ca6f9c8ffe81106280f0bd643cfbe4b1`, published as pull request 71 under evaluation version `mcp-dual-era-native-2026-09-24`. It is derived from frozen bundle bytes alone: `instruction.md`, `task.toml`, `tests/config.json`, `tests/test_weights.json`, `tests/score_tests.py`, `tests/test_outputs.py`, `tests/test.sh`, `tests/rubric.json`, and `solution/fix.patch`. It records the reference route through the task and the checker identifier each step discharges.

This file is private. `tests/test_outputs.py` copies the candidate workspace into a disposable scratch tree, deletes `src/Repl.McpTests` outright and writes the frozen suite in its place, so nothing here reaches the agent under test. No byte of this document may appear on the agent-visible surface, and no value stated here may be restated in `instruction.md`.

## Scope boundary

`config['source_provenance'].adaptations` in `tests/config.json` records two deliberate reductions, and `instruction.md` names four exclusions. No step below may contradict them.

- The verifier owns its own pinned test project and omits inspector, external-executable and implementation-level unit tests. The candidate's own `src/Repl.McpTests` tree is deleted before grading, so the repository tests the reference patch touches under `Given_McpDebounce.cs`, `Given_McpResourceParameters.cs` and `Given_McpToolAdapter.cs` are development aids that score nothing. Repository tests remain available for development.
- Private protocol-constant references are replaced by protocol revision literals. The frozen suite pins the eras as the literal strings `2025-11-25` and `2026-07-28` rather than naming an SDK constant, so an implementation must recognise those revision values directly; no step prescribes a particular constant, type or identifier through which they are expressed.
- Tasks extensions, request-specific authorization graphs, application-owned DI state isolation and reusable-options list-change notification generation are out of scope, and tasks must not be advertised. These appear in no step.
- Legacy sessions may retain their previous catalog until a rebuild succeeds, and the metadata-resync side effect is outside the authentication and discovery contract. A legacy session serving its prior catalog after a failed rebuild is conformant; only the modern era forbids per-connection stale catalogs.

## Deliverable manifest

| id | deliverable | established by | graded through |
| :-- | :-- | :-- | :-- |
| D1 | `ModelContextProtocol` pinned at exactly `2.2.0` in central package management, with the project layout and assembly names unchanged | patch modifies `src/Directory.Packages.props` | dependency precondition, every group |
| D2 | Retained `AwesomeAssertions` and `Microsoft.Extensions.TimeProvider.Testing` package versions the frozen suite resolves centrally | patch leaves both `PackageVersion` rows in `src/Directory.Packages.props` | offline restore precondition, every group |
| D3 | Retained `InternalsVisibleTo` grant and internal surface the frozen suite compiles against | patch leaves `<InternalsVisibleTo Include="Repl.McpTests" />` in `src/Repl.Mcp/Repl.Mcp.csproj` | compilation precondition, every group |
| D4 | Dual-era revision selection and per-request session context | patch adds `src/Repl.Mcp/McpProtocolRevisions.cs` and `McpSessionContext.cs`, modifies `McpServerHandler.cs` | `protocol_revisions`, `bootstrap_and_request_era` |
| D5 | Era-scoped cache hints on list and resource results | patch adds `src/Repl.Mcp/McpCacheHints.cs` | `protocol_revisions` |
| D6 | Fixed modern discovery predicate surface | patch adds `src/Repl.Mcp/McpDiscoveryCapabilities.cs` | `modern_capability_discovery`, `modern_state_invariance`, `advertised_execution`, `catalog_rebuild_retry`, `apps_discovery_and_context` |
| D7 | Request-scoped server accessor over a shared options instance | patch adds `src/Repl.Mcp/McpRequestServerAccessor.cs`, modifies `McpServiceProviderOverlay.cs` | `capability_binding`, `roots_isolation`, `concurrent_output` |
| D8 | Roots scope providing coalescing, invalidation, retry, cancellation and soft-root fallback | patch adds `src/Repl.Mcp/McpRootsScope.cs`, modifies `McpClientRootsService.cs` and `IMcpClientRoots.cs` | `roots_isolation`, `roots_coalescing`, `roots_invalidation`, `roots_failure_retry`, `roots_cancellation` |
| D9 | `McpMessageLevel` replacing the SDK logging-level parameter on `IMcpFeedback` | patch adds `src/Repl.Mcp/McpMessageLevel.cs`, modifies `IMcpFeedback.cs` and `McpFeedbackService.cs` | `feedback_routing`, `preserved_mcp_behavior` |
| D10 | Result-carried feedback across prompts, resources and UI resources | patch modifies `ReplMcpServerPrompt.cs`, `ReplMcpServerResource.cs`, `ReplMcpServerUiResource.cs`, `McpAppResource.cs` | `prompt_and_resource_feedback`, `apps_discovery_and_context` |
| D11 | Explicit prompt wrapper copying every SDK `GetPromptResult` field | patch adds `src/Repl.Mcp/McpExplicitPrompt.cs` | `explicit_prompt_metadata` |
| D12 | Exception-detail suppression that preserves deliberate text and binder diagnostics | patch adds `src/Repl.Core/ReplBindingCallbackException.cs`, modifies `Parsing/HandlerArgumentBinder.cs`, `ReplMcpServerTool.cs` and `McpToolAdapter.cs` | `exception_privacy` |
| D13 | Sub-invocation outcome preserving launch globals and releasing session registrations | patch adds `src/Repl.Core/SubInvocationOutcome.cs`, modifies `CoreReplApp.Execution.cs`, `CoreReplApp.cs`, `ISubInvocableReplApp.cs`, `Parsing/GlobalOptionsSnapshot.cs` and `Session/ReplSessionIO.cs` | `launch_globals_and_cleanup`, `concurrent_output` |
| D14 | Interaction, sampling and elicitation channels preserved under the modern SDK | patch modifies `McpInteractionChannel.cs`, `McpSamplingService.cs`, `McpElicitationService.cs` | `modern_capability_discovery`, `advertised_execution`, `preserved_mcp_behavior` |
| D15 | Routing notifications and subscription handling across session lifetime | patch modifies `McpServerHandler.cs` and adds the shared-options and pipe-session fixtures the suite mirrors | `notification_lifetime`, `legacy_dynamic_catalog` |

Every graded group in the Checker identifier set closes over at least one manifest row, and every manifest row is named by at least one trajectory step.

## Checker identifier set

Reward is `passed_groups / 22` over equally weighted groups. `tests/score_tests.py` refuses to grade unless `tests/test_weights.json` equals `dict.fromkeys(config['groups'], 1)`, so the twenty-two weights are structurally pinned at 1 each and no group may be re-priced. `tests/test_outputs.py` marks a group `passed` only when every test method in its `tests` list reported outcome `Passed` for every case that method produced, so a data-driven method contributes as many cases as it has rows and one non-passing row fails the whole group. A group is one whole share: it earns nothing for the methods it does satisfy, and adding failures inside an already-failing group costs nothing further.

| group | methods | trajectory step |
| :-- | --: | :-- |
| `protocol_revisions` | 4 | S2 |
| `bootstrap_and_request_era` | 4 | S3 |
| `capability_binding` | 2 | S4 |
| `modern_capability_discovery` | 4 | S5 |
| `modern_state_invariance` | 2 | S6 |
| `advertised_execution` | 4 | S7 |
| `legacy_dynamic_catalog` | 3 | S8 |
| `catalog_rebuild_retry` | 1 | S9 |
| `roots_isolation` | 4 | S10 |
| `roots_coalescing` | 2 | S11 |
| `roots_invalidation` | 3 | S12 |
| `roots_failure_retry` | 4 | S13 |
| `roots_cancellation` | 1 | S14 |
| `notification_lifetime` | 4 | S15 |
| `concurrent_output` | 2 | S16 |
| `launch_globals_and_cleanup` | 2 | S17 |
| `feedback_routing` | 5 | S18 |
| `prompt_and_resource_feedback` | 7 | S19 |
| `exception_privacy` | 10 | S20 |
| `explicit_prompt_metadata` | 5 | S21 |
| `apps_discovery_and_context` | 6 | S22 |
| `preserved_mcp_behavior` | 139 | S23 |

The twenty-two method lists partition `config['test_methods']` exactly: they sum to 218 methods with no method in two groups and none outside a group. `tests/test_outputs.py` compares discovered method names against that set and takes the run ungraded on any missing or unexpected name, so discovery is an all-or-nothing gate rather than a per-group one.

`tests/rubric.json` declares twenty-two equally weighted criteria whose ids are the same group names and whose `test_ids` name the same method lists, with `contributes_to_reward` set to `false` because each criterion is already scored once by its deterministic group. Steps below cite those ids to show the reference route does not contradict the written contract; they add nothing to the reward.

## Preconditions

Every group fails or the run goes ungraded, before any behavioural check runs, if a condition below is unmet. Treat these as gate zero rather than as one group among twenty-two. The two classes are not interchangeable: an absent migration is a graded zero, while an unavailable measurement is `score: null`.

1. `dotnet` resolves on `PATH` and `/opt/nuget/packages/modelcontextprotocol/2.2.0` exists. Otherwise the run is ungraded.
2. At least one `.cs` file exists in the workspace. An empty submission returns `migration_absent` for all twenty-two groups, which is a graded reward of `0.0` rather than an ungraded run.
3. `src/Repl.Mcp/Repl.Mcp.csproj` and `src/Directory.Packages.props` are both present at those exact paths, and the manifest parses as XML. A relocated project or an unparseable manifest is ungraded.
4. `src/Directory.Packages.props` declares exactly one `PackageVersion` for `ModelContextProtocol`. A sole `1.4.1` entry returns `migration_absent` for all twenty-two groups, a graded zero. A sole `2.2.0` entry proceeds. Anything else, including a duplicated or absent entry or any third version, is ungraded.
5. `dotnet restore` succeeds for the frozen suite project against a NuGet configuration whose package sources are cleared, so every package the suite resolves must already sit in the local cache. Central package management supplies the suite's unversioned `AwesomeAssertions` and `Microsoft.Extensions.TimeProvider.Testing` references from the candidate's own `src/Directory.Packages.props`.
6. `dotnet build --configuration Release` succeeds for that project. The suite compiles against the submitted production API through `ProjectReference` to `../Repl.Mcp/Repl.Mcp.csproj` and reaches internal members through the `Repl.McpTests` friend grant, so any signature change the suite does not expect is a compilation failure and therefore ungraded rather than a low score.
7. The built assembly appears at `src/Repl.McpTests/bin/Release/net10.0/Repl.McpTests.dll`. The frozen project pins `net10.0` and `AssemblyName` `Repl.McpTests`, so the target framework must remain net10.0.
8. The runner emits a TRX report, every outcome is `Passed` or `Failed`, and the process exit status agrees with those outcomes. An incomplete or contradictory run is ungraded.

## Golden trajectory

### S1 - Move the dependency to 2.2.0 without disturbing the graded surface

Bump the single `ModelContextProtocol` `PackageVersion` in `src/Directory.Packages.props` to `2.2.0` and adapt production code to the new SDK. Keep the project layout, assembly names and production references; keep `src/Repl.Mcp/Repl.Mcp.csproj` at its path with its `Repl.McpTests` friend grant; keep the `AwesomeAssertions` and `Microsoft.Extensions.TimeProvider.Testing` package versions; and keep the retained internal members named in the integration contract at their current signatures, including `McpServerHandler`'s constructor, `RunAsync`, `BuildSnapshotForTests()` and the snapshot's `Tools`, `Resources` and `Prompts`.

- Established state: a workspace that restores and compiles the frozen suite offline and exposes every member it binds.
- Drift survived: the candidate deletes or rewrites its own test project during a migration of this size, and the natural tidy-up is to drop the now-unused test package versions from central package management. The verifier replaces the test project but not the manifest, so the frozen suite then fails to restore and the entire run returns `score: null` with no behavioural verdict at all. Dropping the `InternalsVisibleTo` grant, or retargeting away from net10.0, fails the same way and for the same invisible reason.
- Satisfies: preconditions for all twenty-two groups.

### S2 - Serve both revisions with era-correct cache hints

Accept the legacy `initialize` handshake and the modern revision, treating an unpinned SDK client as modern. Read revision, identity and capabilities from per-request `_meta` in the modern era. Omit cache hints from legacy list results entirely, and mark list and resource results private with zero TTL only in the modern era. Two sessions sharing one handler must each negotiate the modern revision independently.

- Established state: one handler whose wire output is a function of the era the request declares.
- Drift survived: applying the modern private, zero-TTL annotation unconditionally is the tidier implementation and it changes legacy list payloads on a field legacy clients were never sent. The assertion is on absence, so a hint added "harmlessly" to the legacy path fails while every functional list test still passes.
- Satisfies: `protocol_revisions`. Consistent with rubric criterion `protocol_revisions`.

### S3 - Keep the legacy bootstrap per session and the modern catalog real

With `DiscoverAndCallShim` enabled, give each legacy session `discover_tools` and `call_tool` on its first list and its real catalog afterwards, and restart that introduction when routing changes. Give every modern request the real catalog every time, and serve both eras correctly when one connection carries both.

- Established state: a bootstrap whose state is keyed to the session and the era, not to the process.
- Drift survived: holding the shim's "already introduced" flag on the handler rather than per session gives the second legacy session the real catalog immediately, which looks like a cache working correctly and breaks the client that needed the introduction. The mixed-era connection case catches the mirror error, an era decision cached per connection from the first request.
- Satisfies: `bootstrap_and_request_era`. Consistent with rubric criterion `bootstrap_and_request_era`.

### S4 - Bind client capabilities per request

Keep each overlapping request's own client capabilities in scope for its whole execution, on the shared-handler path and on the path where several SDK servers reuse one `BuildMcpServerOptions()` result.

- Established state: a capability lookup that resolves against the requesting client rather than the most recent one.
- Drift survived: caching the negotiated capabilities on the options object is correct for every single-client test and wrong the moment two clients overlap, because the second connection overwrites the first's view mid-execution. The failure is timing-dependent and reads as a flake rather than a defect.
- Satisfies: `capability_binding`. Consistent with rubric criterion `capability_binding`.

### S5 - Make modern discovery independent of the client

Answer the modern discovery predicates from the fixed table rather than from the real client: report roots, sampling and elicitation `IsSupported` and feedback `IsLoggingSupported` and `IsProgressSupported` as `true`, report `HasSoftRoots` as `false`, return empty for roots `Current` and `GetAsync()`, and answer interaction questions with declared defaults and no prefilled answers, client elicitation or sampling. Make no roots round-trip while listing, and keep the advertised set invariant when a predicate reads the roots data or when a client declares no capabilities at all.

- Established state: one advertised catalog per routing configuration, identical for every modern client.
- Drift survived: evaluating presence predicates against the live client is exactly what the legacy era does and what this era forbids, and it yields a per-client catalog that is individually plausible and collectively unstable. The no-round-trip assertion is the specific trap: a predicate that merely reads `Current` triggers a roots fetch during listing unless discovery short-circuits it, so an otherwise correct gate still fails on an observable side effect.
- Satisfies: `modern_capability_discovery`. Consistent with rubric criterion `modern_capability_discovery`.

### S6 - Keep modern discovery invariant under state writes

Hold the modern advertised set constant after a tool mutates session state and after a modern client sets soft roots, while still letting those soft roots affect execution.

- Established state: a discovery result that no request can move, separated from an execution path that still honours the same data.
- Drift survived: invalidating the modern catalog on a session-state write is the intuitive cache-correctness move and it reintroduces exactly the per-session variability the era removes. The pairing matters: the same soft roots that must not change discovery must still change execution, so suppressing them everywhere fails `advertised_execution` instead.
- Satisfies: `modern_state_invariance`. Consistent with rubric criterion `modern_state_invariance`.

### S7 - Use the discovery predicate for call eligibility too

Keep an advertised capability-gated command callable with the real client even when that client lacks the capability the gate names, keep a command the fixed predicate excludes absent rather than callable, and prevent an invocation-time answer from retracting the command being invoked. Keep a gated tool in a legacy static catalog callable.

- Established state: one eligibility decision shared by listing and dispatch.
- Drift survived: re-evaluating the gate against the live client at call time is the obvious symmetry and it produces a tool that lists and then reports itself not found, which is worse than either consistent behaviour. Handlers still receive the real client's context, so the fix is to reuse the discovery answer for eligibility while passing the genuine client into execution, not to neutralise the client everywhere.
- Satisfies: `advertised_execution`. Consistent with rubric criterion `advertised_execution`.

### S8 - Preserve legacy dynamic discovery

Keep legacy discovery dependent on client capabilities, session state and soft roots: legacy sessions sharing a gated graph each see their own tools, a legacy tool that mutates session state changes the advertised set, and soft roots can initialise a workspace for a legacy client that does not support roots.

- Established state: the pre-migration dynamic semantics, retained unchanged on the legacy path.
- Drift survived: the migration's centre of gravity is making discovery static, and applying that uniformly is a one-line simplification that silently removes a feature legacy clients depend on. This group exists to make the era split real in both directions rather than only in the new one.
- Satisfies: `legacy_dynamic_catalog`. Consistent with rubric criterion `legacy_dynamic_catalog`.

### S9 - Surface a failed modern rebuild without serving stale catalogs

Return an error when a modern catalog rebuild fails transiently, without any session serving its own stale catalog, and let a subsequent request retry without requiring another invalidation.

- Established state: a rebuild failure that is visible and self-healing rather than papered over per connection.
- Drift survived: falling back to the last good per-session catalog is standard resilience practice and it is precisely the per-connection divergence the modern era forbids, so the safer-looking choice is the failing one. Latching the failure so that recovery needs a fresh invalidation is the opposite error and fails the retry half of the same single method.
- Satisfies: `catalog_rebuild_retry`. Consistent with rubric criterion `catalog_rebuild_retry`.

### S10 - Never let one client see another's roots

Resolve a handler's first `Current` read under `mcp serve` to its own client's roots, and keep `Current` empty on the reusable-options path until that request itself calls `GetAsync`, never inheriting another request's roots. Two root-capable clients must each see only their own, on the shared-handler path and on the shared-options path.

- Established state: a roots view scoped to the request that asked for it.
- Drift survived: a roots cache keyed by anything coarser than the request, most naturally the options instance or a static field, leaks one tenant's workspace paths into another's handler. The two paths differ deliberately: `Current` resolves eagerly under `mcp serve` and stays empty under reusable options, so a single uniform policy fails one of them whichever way it is chosen.
- Satisfies: `roots_isolation`. Consistent with rubric criterion `roots_isolation`.

### S11 - Coalesce the roots round-trip

Share one native fetch between overlapping first calls on one connection, and issue one round-trip when a single reusable-options request resolves roots twice.

- Established state: at most one outstanding roots request per scope, with every caller served from it.
- Drift survived: the assertion counts round-trips, not results, so an implementation that fetches per caller returns correct roots to everyone and still fails. Caching the answer without deduplicating the in-flight request fixes the repeat case and leaves the race case fetching twice.
- Satisfies: `roots_coalescing`. Consistent with rubric criterion `roots_coalescing`.

### S12 - Make invalidation defeat both completed and in-flight fetches

Refetch after a `roots/list_changed` that follows a completed fetch. When invalidation arrives while a fetch is still unanswered, neither cache the late answer nor hand it to a waiting caller, and when an in-flight fetch is retired, do not give it to the direct waiter.

- Established state: an invalidation that retires the answer as well as the cache entry.
- Drift survived: clearing the cache entry alone leaves the outstanding request live, and its answer lands afterwards and repopulates the cache with data the invalidation was sent to discard. The waiter case is sharper still: the caller receives roots that were already known to be obsolete when they arrived, which no test that invalidates between fetches can reach.
- Satisfies: `roots_invalidation`. Consistent with rubric criterion `roots_invalidation`.

### S13 - Allow retries after failure and fall back to soft roots

Let the next caller reach the client again after a connection-scoped fetch fails, let a later call in the same request retry after its first roots request failed, and let a later call retry even when the last waiter left before the fetch failed. Resolve `Current` to the configured soft roots when the native fetch fails.

- Established state: a failure that is not cached and a `Current` that degrades to configuration rather than to emptiness.
- Drift survived: storing the failure as a completed result permanently disables roots for that scope, which looks like a legitimate negative cache. The last-waiter case is the subtle one: an implementation that disposes the shared fetch state when its waiter count reaches zero can leave a poisoned or missing entry that no later caller can retry through, and it only triggers when cancellation and failure interleave in that order.
- Satisfies: `roots_failure_retry`. Consistent with rubric criterion `roots_failure_retry`.

### S14 - Release a waiting caller on its own token

Release a caller waiting for outstanding roots when that caller's own cancellation token fires.

- Established state: cancellation that is per waiter rather than per fetch.
- Drift survived: awaiting the shared fetch task directly ignores the caller's token, so one slow client blocks another's cancellation, and linking the tokens the other way lets one caller's cancellation abort the fetch every other waiter is depending on. Only the per-waiter release satisfies both this group and the coalescing group together.
- Satisfies: `roots_cancellation`. Consistent with rubric criterion `roots_cancellation`.

### S15 - Keep notifications flowing after a session closes

Keep delivering routing notifications to a surviving session after another session on the same server closes. Broadcast list-change notifications to legacy clients that never subscribed, acknowledge a modern subscription request, and filter modern deliveries so that a prompts-only subscriber receives no tool list-change notification.

- Established state: a notification fan-out whose failures are per subscriber and whose filtering is per subscription.
- Drift survived: a broadcast loop that propagates the first disposed-session exception stops at the dead subscriber and silently starves every live one, which is invisible until a client disconnects. Requiring a subscription before broadcasting is the mirror error and breaks every legacy client, since the legacy era never subscribes.
- Satisfies: `notification_lifetime`. Consistent with rubric criterion `notification_lifetime`.

### S16 - Keep concurrent sessions' tools and output apart

Keep each of two concurrently running sessions on its own tool catalog, and keep command output isolated when tools are invoked concurrently.

- Established state: per-session catalog and output channels that survive real overlap.
- Drift survived: routing output through an ambient current-session lookup rather than the invocation's own context interleaves two clients' command output under concurrency, and each client sees a plausible transcript containing the other's lines.
- Satisfies: `concurrent_output`. Consistent with rubric criterion `concurrent_output`.

### S17 - Preserve launch globals across sub-invocations and clean up after them

Preserve launch-global values and their `HasValue` state through a tool's sub-invocations, and release the temporary session registration a tool call creates when that call completes.

- Established state: sub-invocations that inherit the launch configuration and leave no registration behind.
- Drift survived: resetting globals for a sub-invocation is defensible isolation and it drops the launch configuration the outer command was started with, while `HasValue` is the tell that distinguishes an unset global from one explicitly set to its default. The cleanup half leaks a registration per tool call, which no functional assertion notices and which grows without bound in a long-lived server.
- Satisfies: `launch_globals_and_cleanup`. Consistent with rubric criterion `launch_globals_and_cleanup`.

### S18 - Route feedback by declared log level

Carry feedback in the tool result rather than as message notifications when a modern request declares no log level. When a level is declared, notify messages at or above it and withhold those below, including withholding lower severities from a client that requested error level. Keep legacy feedback on notifications subject to session thresholds, and preserve structured progress alongside messages.

- Established state: one feedback pipeline with two delivery shapes chosen by what the request declared.
- Drift survived: `McpMessageLevel` replaces the SDK logging level and its numeric ordering runs from `Debug = 0` to `Emergency = 7`, so a severity comparison written in the wrong direction still filters, still looks like a threshold, and delivers exactly the complement of the intended set. Defaulting an absent log level to a permissive one reroutes result-carried feedback onto notifications, where a modern client that declared nothing is not listening.
- Satisfies: `feedback_routing`. Consistent with rubric criterion `feedback_routing`.

### S19 - Keep feedback attached through prompts, resources and UI failures

For a modern request without a declared log level, append feedback after successful prompt content, and retain it in a failing prompt, a failing resource read, a failing UI-resource read, a raw UI resource that reports and then fails, and a raw UI resource that reports and then cancels itself. Leave a successful raw UI body carrying its own content and MIME type with no feedback appended.

- Established state: feedback that survives the error path, which is where it is most needed, without contaminating successful binary or markup bodies.
- Drift survived: feedback collected into the result builder is discarded the moment the handler throws, so the ordinary implementation loses exactly the diagnostics the failure case exists to deliver. Self-cancellation is the case most often missed, because it is usually handled as an abandoned request rather than as a completed failure that still owes its reports. Appending to a successful raw UI body is the opposite error and corrupts the payload.
- Satisfies: `prompt_and_resource_feedback`. Consistent with rubric criterion `prompt_and_resource_feedback`.

### S20 - Withhold exception detail and keep deliberate text

Suppress the message, type, connection strings and paths of uncaught handler, dependency-factory and binding-callback exceptions, including a dependency factory that cancels itself and an options-group setter that throws. Keep a handler's own deliberate failure text, MCP exception messages, actionable binder diagnostics for a missing required dependency, and reported feedback. Distinguish handler cancellation from the requesting caller abandoning the request.

- Established state: an error surface where only text the application chose to emit reaches the client.
- Drift survived: a single catch-all that stringifies the exception is the normal implementation and it leaks connection strings and filesystem paths into a client-visible error. Over-correcting is equally graded: blanket suppression also swallows the deliberate failure text, the MCP error message and the binder diagnostic that tells the operator which dependency is missing, so seven of these ten methods assert withholding and the remaining three assert survival.
- Satisfies: `exception_privacy`. Consistent with rubric criterion `exception_privacy`.

### S21 - Copy every prompt result field when appending feedback

Retain the SDK `GetPromptResult` fields `Messages`, `Description`, `Meta` and `ResultType` when appending feedback, resolve roots inside explicit prompt handlers, and deliver a prompt instruction to the client with no prefilled response when the prompt has no prefill.

- Established state: a prompt wrapper that is a superset of the SDK result rather than a reconstruction of it.
- Drift survived: rebuilding the result to attach feedback copies the fields the author happened to think of, so `Meta` and `ResultType` are dropped silently and every message-content assertion still passes. One method asserts field-by-field copying directly, which is why the wrapper must copy rather than re-create.
- Satisfies: `explicit_prompt_metadata`. Consistent with rubric criterion `explicit_prompt_metadata`.

### S22 - Keep the apps extension advertised and its context real

Advertise the apps extension for a registered app that a capability gate excludes, that a data gate excludes, or whose registration is shadowed, as well as for one in the catalog. Resolve a capability injected into a UI-resource handler against the calling client's request, and let a raw UI resource's first `Current` read see that client's roots.

- Established state: an extension advertisement driven by registration rather than by gate outcome, and UI handlers bound to the real caller.
- Drift survived: deriving the extension advertisement from the visible app set means a fully gated deployment stops advertising a capability it still implements, and the client then never attempts the call. The context half is the roots-isolation bug in a different surface: a UI resource handler that resolves capabilities from ambient state rather than the request serves one client from another's connection.
- Satisfies: `apps_discovery_and_context`. Consistent with rubric criterion `apps_discovery_and_context`.

### S23 - Carry the whole pre-migration contract across the SDK change

Preserve command projection and schemas, option binding and visibility including hidden, automation-hidden, alias and case-distinct destinations, resource, prompt and app mapping and metadata, fallback promotion in both directions, interaction capabilities including prefill resolution and its failure modes, pagination and cursor handling, exit-code semantics, subscriptions, routing refresh, enum-level equivalence between `McpMessageLevel` and the protocol level, launch routes, and reusable server-options behaviour.

- Established state: a migration that changes the protocol layer and nothing a client could already observe.
- Drift survived: this group carries 139 of the suite's 218 methods in one indivisible share, so a single regression anywhere in the pre-existing surface costs the same as failing an entire new feature, and it is the cheapest group to lose while feeling finished. A pass here depends on the whole adapter being sound rather than on any one behaviour, so treat it as the integration gate rather than an independent feature.
- Satisfies: `preserved_mcp_behavior`. Consistent with rubric criterion `preserved_mcp_behavior`.

## Red lines

- Leaving `ModelContextProtocol` at `1.4.1`, or declaring any version other than exactly one `2.2.0` entry. The first is a graded zero as an absent migration; the second is ungraded.
- Removing the `AwesomeAssertions` or `Microsoft.Extensions.TimeProvider.Testing` package versions from `src/Directory.Packages.props`, or dropping the `Repl.McpTests` friend grant, or retargeting away from `net10.0`. Each takes the run to `score: null` rather than to a low score.
- Relocating `src/Repl.Mcp/Repl.Mcp.csproj` or `src/Directory.Packages.props`, or changing the `Repl.Mcp` assembly name the suite references.
- Adding a package the pinned offline cache does not hold. Restore runs with package sources cleared.
- Editing tests in the expectation that they will be graded. The verifier deletes `src/Repl.McpTests` and writes its own suite from `config['source_files']`.
- Advertising tasks, which `instruction.md` places out of scope and forbids.
- Applying the modern private, zero-TTL cache annotation to legacy list results.
- Evaluating presence predicates against the live client during modern discovery, or triggering a roots round-trip while listing.

## Rejected routes

Each route below is a plausible implementation that a reviewer might accept and the graded surface rejects. The named control is the check that catches it.

| rejected route | why it looks correct | control that rejects it |
| :-- | :-- | :-- |
| Drop the unused test package versions while replacing the test project | the candidate's own tests are gone | offline restore precondition |
| Apply modern cache hints in both eras | one uniform annotation path | `protocol_revisions` |
| Hold the shim introduction flag on the handler | the introduction is served once | `bootstrap_and_request_era` |
| Cache negotiated capabilities on the options instance | correct for every single client | `capability_binding` |
| Evaluate presence predicates against the live client | mirrors the legacy behaviour exactly | `modern_capability_discovery`, `advertised_execution` |
| Let a predicate read `Current` during listing | the predicate needs the data | `modern_capability_discovery` |
| Invalidate the modern catalog on a session-state write | ordinary cache correctness | `modern_state_invariance` |
| Neutralise soft roots in execution as well as discovery | consistent with the fixed table | `modern_state_invariance`, `legacy_dynamic_catalog` |
| Re-evaluate the gate at call time | symmetric with discovery | `advertised_execution` |
| Make discovery static in both eras | the migration's whole point | `legacy_dynamic_catalog` |
| Serve the last good catalog when a modern rebuild fails | standard resilience | `catalog_rebuild_retry` |
| Latch a rebuild failure until the next invalidation | avoids retry storms | `catalog_rebuild_retry` |
| Key the roots cache to the options instance | one cache per server | `roots_isolation`, `roots_coalescing` |
| Fetch roots once per caller | every caller gets correct roots | `roots_coalescing` |
| Clear the cache entry and let the in-flight fetch land | the entry is the cache | `roots_invalidation` |
| Cache a failed roots fetch as a result | a negative cache | `roots_failure_retry` |
| Dispose shared fetch state when the waiter count reaches zero | nobody is waiting | `roots_failure_retry` |
| Await the shared fetch task without the caller's token | one fetch, one await | `roots_cancellation` |
| Propagate a disposed-session exception out of the broadcast loop | surfaces the dead session | `notification_lifetime` |
| Require a subscription before broadcasting list changes | the modern model | `notification_lifetime` |
| Resolve output through an ambient current-session lookup | correct without concurrency | `concurrent_output` |
| Reset launch globals for a sub-invocation | clean isolation | `launch_globals_and_cleanup` |
| Default an absent log level to a permissive threshold | nothing is lost | `feedback_routing` |
| Compare severities in the wrong direction | still a working threshold | `feedback_routing` |
| Discard collected feedback when a handler throws | the result was never built | `prompt_and_resource_feedback` |
| Treat handler self-cancellation as an abandoned request | cancellation is cancellation | `prompt_and_resource_feedback`, `exception_privacy` |
| Append feedback to a successful raw UI body | consistent with every other path | `prompt_and_resource_feedback` |
| Stringify the exception into the client error | maximal diagnostics | `exception_privacy` |
| Suppress every error message uniformly | maximal privacy | `exception_privacy` |
| Rebuild the prompt result instead of copying it | every message is preserved | `explicit_prompt_metadata` |
| Advertise the apps extension from the visible app set | matches what the client can call | `apps_discovery_and_context` |
| Resolve UI-resource capabilities from ambient state | one accessor for every surface | `apps_discovery_and_context`, `roots_isolation` |

## Reconciliation

The trajectory step set is `{S1..S23}`. The graded group set named by the steps is `{protocol_revisions, capability_binding, roots_isolation, notification_lifetime, modern_state_invariance, modern_capability_discovery, advertised_execution, launch_globals_and_cleanup, catalog_rebuild_retry, legacy_dynamic_catalog, bootstrap_and_request_era, concurrent_output, roots_coalescing, roots_invalidation, roots_failure_retry, roots_cancellation, feedback_routing, prompt_and_resource_feedback, exception_privacy, explicit_prompt_metadata, apps_discovery_and_context, preserved_mcp_behavior}`, which is exactly the key set of `tests/test_weights.json` and exactly the key set of `config['groups']` in `tests/config.json`, in both directions and with no surplus on either side. S1 binds the preconditions rather than a group, which is why twenty-three steps close over twenty-two groups.

Every manifest row D1 through D15 is named by at least one step, and every step names at least one manifest row. The rubric criterion ids in `tests/rubric.json` are the same twenty-two identifiers as the groups; they are cited for consistency only and contribute nothing to the deterministic reward, because that file sets `contributes_to_reward` to `false`.

The reductions and exclusions in the Scope boundary section appear in no step, matching `config['source_provenance'].adaptations` and the out-of-scope paragraph of `instruction.md`.

Open gaps recorded against this bundle: `solution/grounding.yaml` and `solution/recompute.py` are absent, so this file is hand-derived and not regenerated; no feasibility bundle exists, so the rejected routes above are reasoned from committed bytes rather than measured against executed negative controls.
