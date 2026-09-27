# Migrate Repl's MCP integration to SDK 2.2.0

Upgrade `/workspace` from `ModelContextProtocol` 1.4.1 to **2.2.0**, adapting
production code to support legacy `2025-11-25` and modern `2026-07-28` requests
while preserving the behavior below.

## Project and interfaces

Keep existing project layout and assembly names, including
`src/Repl.Mcp/Repl.Mcp.csproj`, its production references and central package
versions in `src/Directory.Packages.props`. Target .NET 10; SDK 10.0.401 is
installed and `global.json` permits roll-forward from 10.0.102. Base and target
NuGet packages are cached at `/opt/nuget/packages`; verification has no external
network access.

Preserve public ReplApp/CoreReplApp, command/module mapping,
`BuildMcpServerOptions()`, `UseMcpServer()`, transport, roots, sampling,
elicitation, interaction, feedback, resource, prompt, app and session I/O
interfaces. Replace the SDK `LoggingLevel` parameter on `IMcpFeedback` with:

```csharp
namespace Repl.Mcp;
public enum McpMessageLevel {
    Debug = 0, Info = 1, Notice = 2, Warning = 3,
    Error = 4, Critical = 5, Alert = 6, Emergency = 7
}
ValueTask SendMessageAsync(McpMessageLevel level, object? data,
                          CancellationToken cancellationToken = default);
```

Support overlapping calls on one handler and multiple SDK servers sharing one
`BuildMcpServerOptions()` result. Transport factories receive a name and
`IReplIoContext`, and may return `StreamServerTransport` using its input/output
pipes.

Preserve `InternalsVisibleTo` access for `Repl.McpTests` and these existing
interfaces with their current signatures; they may remain internal:

- `Repl.Mcp.McpServerHandler(ICoreReplApp, ReplMcpServerOptions, IServiceProvider)`,
  `RunAsync(IReplIoContext, CancellationToken)`, `BuildSnapshotForTests()` and
  the returned snapshot's `Tools`, `Resources`, `Prompts`.
- `Repl.Mcp.McpInteractionChannel`'s constructor and interaction-interface methods.
- `McpAppMetadata.ExtensionName`, `McpAppValidation.ResourceMimeType` and
  `McpResultFlowArgumentNames.Cursor` in `Repl.Mcp`.
- `Repl.ReplSessionIO.CurrentSessionId`, `TryGetSession`, `IsProgrammatic`.

## Behavior

**Protocol and bootstrap.** Legacy clients use `initialize`; modern requests
carry revision, identity and capabilities in per-request `_meta`. Select
semantics per request, including mixed eras on one connection. Unpinned SDK
clients use the modern revision. Legacy list results omit cache hints; private
scope and zero TTL apply to list/resource results only in the modern era. With
`DiscoverAndCallShim`, each legacy session first lists `discover_tools` and
`call_tool`, then its real catalog; routing changes restart the introduction.
Modern requests always receive the real catalog.

**Discovery and execution.** Modern discovery must be independent of client
capabilities, roots data, session state/information and interaction answers,
including changes made by commands. Listing causes no roots round-trip.
Presence predicates observe:

| Member | Modern discovery answer |
| --- | --- |
| Roots/sampling/elicitation `IsSupported`; feedback `IsLoggingSupported`, `IsProgressSupported` | `true` |
| `HasSoftRoots` | `false` |
| Roots `Current`, `GetAsync()` | Empty |
| `IReplInteractionChannel` questions | Declared defaults; no prefilled answers or client elicitation/sampling |

Use those predicate results for both discovery and call eligibility: included
commands remain callable despite missing client capabilities; excluded commands
remain absent. Invocation answers cannot retract their own command. Handlers
receive the real client's context. Preserve callable gated tools in legacy
static catalogs and legacy capability-, session-state- and soft-root-dependent
discovery. Setting soft roots still affects execution in both eras.

Application-global routing changes may change everyone's catalog. Failed modern
rebuilds return errors without serving per-connection stale catalogs; subsequent
requests retry without another invalidation. Legacy sessions may retain their
previous catalog until rebuilding succeeds.

**Isolation and lifetime.** Overlapping requests retain their own capabilities,
roots, catalogs and output throughout execution, on shared-handler and
reusable-options paths. Tool sub-invocations preserve launch-global values and
`HasValue`, and release temporary session registrations on completion.

Closing one session must not stop routing notifications to survivors. Legacy
clients receive list-change broadcasts without subscribing. Preserve modern
subscription acknowledgement/filtering, including prompts-only subscriptions.

**Roots.** Under `mcp serve`, a handler's first `Current` read sees its client's
roots. With reusable options, `Current` is empty until that request calls
`GetAsync`, never inheriting another request's roots. Overlapping first calls on
one connection share one native fetch; repeated lookups within a reusable-options
request use one round-trip. Invalidation forces fresh retrieval: a pending
obsolete answer is neither cached nor returned to waiters. Failed fetches allow
retries within the same request and after the last waiter leaves; `Current`
falls back to configured soft roots. A waiter's own cancellation token releases it.

**Feedback and errors.** Modern requests without a declared log level receive
feedback in results rather than message notifications. Declared levels filter
notifications by severity; legacy feedback uses notifications subject to session
thresholds. Preserve structured progress. For modern requests without a log
level, append feedback after successful prompt content and retain it in prompt,
resource and UI-resource failures, including a handler's own cancellation.
Successful raw UI bodies retain their content and MIME type without appended feedback.

Suppress uncaught handler, dependency-factory and binding-callback exception
messages, types, connection strings and paths. Preserve deliberate application
failure text, MCP errors, actionable binder diagnostics and reported feedback.
Distinguish handler cancellation from the requesting caller abandoning the request.

**Prompts and apps.** When appending feedback, retain SDK `GetPromptResult`
fields `Messages`, `Description`, `Meta`, `ResultType`. Explicit prompt handlers
resolve roots; prompt instructions reach clients without prefilled responses.
Advertise the apps extension for registered apps even when capability/data gates
exclude them or registrations are shadowed. UI-resource capability calls and
roots reads use the requesting client's context. Preserve app metadata and
successful MIME-typed bodies.

**Regressions.** Preserve command projection, schemas, option binding/visibility,
resource/prompt/app mapping and metadata, fallbacks, interaction capabilities,
pagination, exit-code semantics, subscriptions, routing refresh, enum-level
equivalence, launch routes and reusable server-options behavior.

Tasks extensions, request-specific authorization graphs, application-owned DI
state isolation and reusable-options list-change notification generation are
outside scope. Do not advertise tasks. Keep roots, sampling and logging
compatibility despite modern SDK deprecation.

## Scoring

Independent immutable fixtures grade 22 equally weighted groups; every native
assertion in a group must pass. Reward is passed groups / 22. Repository tests
remain available for development; do not modify tests to produce a score.

An unchanged 1.4.1 dependency or empty implementation scores zero as an absent
migration, reported separately from executed assertions. Missing dependencies,
unsupported layouts/interfaces, verifier compilation incompatibility or
infrastructure failures are ungraded (`score: null`).
