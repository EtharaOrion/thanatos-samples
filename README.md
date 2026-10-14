<p align="center"><img src="images/hero.svg" alt="THANATOS" width="720"></p>

# THANATOS: samples

<p align="center"><b>The samples lane: 3 of 30 Harbor task bundles.</b></p>

<p align="center"><a href="#summary"><img src="https://img.shields.io/badge/bundles-3_of_30-845EF7" alt="bundles: 3 of 30"></a> <a href="#evidence-status"><img src="https://img.shields.io/badge/sealed-0-845EF7" alt="sealed: 0"></a> <a href="#difficulty-tiers"><img src="https://img.shields.io/badge/difficulty-measured-845EF7" alt="difficulty: measured"></a></p>

<p align="center"><sub><a href="#abstract">Abstract</a> | <a href="#summary">Summary</a> | <a href="#difficulty-tiers">Difficulty tiers</a> | <a href="#evidence-status">Evidence status</a> | <a href="#coverage">Coverage</a> | <a href="#dataset-structure">Dataset structure</a> | <a href="#trajectory-structure">Trajectory structure</a> | <a href="#verification-and-quality-assurance">Verification and quality assurance</a> | <a href="#reproduction">Reproduction</a> | <a href="#cite">Cite</a> | <a href="#license">License</a> | <a href="#contact">Contact</a></sub></p>

## Abstract

The curated lane of this corpus: at most 30 Harbor task bundles, every anchor seated first and every other bundle in seal order. Bundles past that ceiling live in `delivery/`.

Each bundle is one Harbor task in a directory named by its content-derived uuid5, so the name doubles as an integrity check. This page is rendered from the resident bundles on every reconcile; a value a bundle does not carry reads `absent`, and the page never fills one in.

## Summary

| Property | Value |
| --- | --- |
| Bundles | 3 of 30 |
| Sealed | 0 of 3 |
| Registrations | unregistered (3) |
| Audit verdicts | none (3) |
| Harbor schema | 1.4 (3) |

## Difficulty tiers

Difficulty is measured by the signed pilot alone and never declared in a bundle, so this page states no tier a bundle claims.

## Evidence status

The verdict is the audit outcome recorded at the sealed digest, and `none` means no verdict has landed for that digest yet. Only an authoring run removes a bundle from this lane, so removal waits for the next one.

| uuid | Verdict | Sealed digest | Stream |
| --- | --- | --- | --- |
| 3242f8bb-bd4f-5c31-a2a6-663dbc2f3212 | none | absent | none |
| 407a8115-5169-55d1-8aea-12b0a93bea74 | none | absent | none |
| 7035333c-d9a3-530d-89f4-4ff9e95e6f36 | none | absent | none |

## Coverage

| Keyword | Bundles |
| --- | --- |
| concurrency | 2 |
| authentication | 1 |
| csharp | 1 |
| database | 1 |
| dotnet | 1 |
| mcp | 1 |
| protocol-migration | 1 |
| react | 1 |
| typescript | 1 |

## Dataset structure

| Bundle | Task | Keywords | Registration | Sealed at | Tier |
| --- | --- | --- | --- | --- | --- |
| [`3242f8bb-bd4f-5c31-a2a6-663dbc2f3212`](3242f8bb-bd4f-5c31-a2a6-663dbc2f3212/) | `hard-migrations/3242f8bb-bd4f-5c31-a2a6-663dbc2f3212` | absent | unregistered | unsealed | - |
| [`407a8115-5169-55d1-8aea-12b0a93bea74`](407a8115-5169-55d1-8aea-12b0a93bea74/) | `twentyhq/twenty-cookie-sessions` | authentication, concurrency, database, react, typescript | unregistered | unsealed | - |
| [`7035333c-d9a3-530d-89f4-4ff9e95e6f36`](7035333c-d9a3-530d-89f4-4ff9e95e6f36/) | `yllibed/repl-mcp-sdk-2` | concurrency, csharp, dotnet, mcp, protocol-migration | unregistered | unsealed | - |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    bundle["&lt;uuid&gt;/"]
    bundle --> n0["task.toml<br/>runner manifest"]
    bundle --> n1["instruction.md<br/>objective the agent reads"]
    bundle --> n2["environment/<br/>agent sandbox image"]
    bundle --> n3["tests/<br/>verifier, hidden from the agent"]
    bundle --> n4["solution/<br/>private oracle"]
    bundle --> n5["trajectories/<br/>private rollout evidence"]
    bundle --> n6["trajectory-attestation.json"]
    bundle --> n7["trajectory-manifest.json"]
```

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    staging["staging/"]
    staging --> samples["samples/<br/>3 of 30"]
    samples --> delivery["delivery/<br/>0 of 150"]
    delivery --> stock["stock/<br/>0 of 10000"]
```

## Trajectory structure

3 of 3 resident bundles carry a `trajectories/` subtree of private rollout evidence. The signed pilot reads it; this page never restates a rollout.

## Verification and quality assurance

Each bundle's signed provenance carrier holds its screening roots, screening instant, and absolute expiry. Placement moves that carrier into the private derivation set, which this page never reads, so reconcile lists no root it cannot verify here.

## Reproduction

Each bundle directory is a complete Harbor task: `task.toml` is the runner manifest, `instruction.md` the objective, `environment/` the sandbox image, and `tests/` the verifier. Point a Harbor runner at one bundle directory to reproduce it; `solution/` and `trajectories/` stay private.

## Cite

```bibtex
@misc{ethara2026thanatos,
  title  = {THANATOS: A Reinforcement Learning Environment and Benchmark for Behaviour-Preserving Code Migration},
  author = {{Ethara.AI}},
  year   = {2026},
  url    = {https://github.com/Ethara-Ai/thanatos}
}
```

## License

MIT. See [LICENSE](LICENSE).

## Contact

- Organization: [Ethara.AI on GitHub](https://github.com/Ethara-Ai)
- Vulnerability and benchmark-integrity disclosure: security@ethara.ai, route documented in [SECURITY.md](SECURITY.md)
- Conduct: conduct@ethara.ai, per [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Contributions: [CONTRIBUTING.md](CONTRIBUTING.md) is the route in, and the reading path for everything else starts at [INDEX.md](INDEX.md)
