# truth.md - direnv, Go to Rust

## Provenance

This is the private golden-trajectory projection for bundle `3242f8bb-bd4f-5c31-a2a6-663dbc2f3212`, the Go to Rust migration of `Zahgon/direnv` from base commit `b00e451f547f39be7ab836d969054114a465a0f9` to golden commit `ffec0a00bebec3380cc963f21206caba377bb01d`. It is derived from frozen bundle bytes alone: `instruction.md`, `task.toml`, `tests/test_weights.json`, `tests/config.json`, `tests/score_tests.py`, `tests/test_outputs.py`, `tests/rubrics.json`, `/workspace/TARGET_API.md`, and `solution/fix.patch`. It records the reference route through the task and the checker identifier each step discharges.

This file is private. `tests/test_outputs.py` copies the candidate workspace into a private subject tree and materialises the frozen suite separately, so nothing here reaches the agent under test. `instruction.md` states that the verifier uses independent frozen integration tests rather than tests the candidate adds or edits, so no value stated here may be restated on the agent-visible surface.

## Scope boundary

`instruction.md` incorporates `TARGET_API.md` as the required Rust compatibility surface, and `tests/config.json` fixes two boundaries that this projection must not contradict.

- No `file_times` suite is graded. `tests/config.json` declares twelve suites and twelve frozen test assets, and none of them exercises `FileTime` or `FileTimes`, so that surface never compiles into the private package and never scores. `FileTime` and `FileTimes` remain part of the documented `TARGET_API.md` compatibility surface and remain reviewable under rubric R-11, but they carry no group weight and wiring them in would move the denominator from 12 to 13.
- The frozen `deps_test.rs` asset checks user-configured log filters through three `audited_config` cases (`configured_filter_preserves_literal_braces_and_quoting`, `configured_filter_preserves_ascii_classes_and_named_groups`, `configured_filter_rejects_invalid_repetition`) that assert accepted and rejected inputs and actual matching behaviour, with positive controls, and no case asserts an intermediate translation string. Rubric R-15 states the requirement explicitly as preserving acceptance, rejection and matching behaviour "without requiring any particular intermediate translation string". No step below prescribes a translation string, and any implementation that reaches the same accept, reject and match decisions is conformant.

## Deliverable manifest

| id | deliverable | established by | graded through |
| :-- | :-- | :-- | :-- |
| D1 | Root `Cargo.toml` and `Cargo.lock` exposing crate and executable `direnv` | reference patch adds both | `config.required_manifests`, lockfile precondition |
| D2 | Command dispatch covering the retained `cmd_*` surface | `internal/cmd/commands.go` replaced by Rust equivalents | every group, rubric R-11 |
| D3 | Shell export and escaping backends for ten shells | `shell_bash`, `shell_elvish`, `shell_fish`, `shell_json`, `shell_murex`, `shell_pwsh`, `shell_gzenv`, `shell_gha`, plus tcsh, vim, zsh and systemd renderers | `direnv_shells_test`, `direnv_shell_test`, `direnv_shell_systemd_test` |
| D4 | Dotenv parser with original error behaviour | `internal/cmd/cmd_dotenv.go` replaced | `direnv_dotenv_parse_test` |
| D5 | Reversible environment diff preserving empty and unset | `internal/cmd/env_diff.go` replaced | `direnv_env_diff_test`, `direnv_env_test`, `direnv_lifecycle` |
| D6 | Compressed environment serialisation | `gzenv/gzenv.go` replaced | `direnv_env_test`, `direnv_packages_test` |
| D7 | Subresource integrity digest support | SRI parser and writer | `direnv_sri_test`, `direnv_packages_test` |
| D8 | XDG base-directory resolution with fallbacks | XDG resolver | `direnv_packages_test` |
| D9 | Authorization, denial and directory traversal | `internal/cmd/rc.go` replaced | `direnv_rc_test`, `direnv_lifecycle` |
| D10 | Go standard-library behavioural equivalents | path, duration, expand, JSON, semver, RFC 3339 helpers | `direnv_deps_test`, `direnv_cmd_version_test` |
| D11 | Configured log-filter regex behaviour | `internal/cmd/config.go` replaced | `direnv_deps_test`, rubric R-15 |
| D12 | Retained shell support files and `version.txt` | patch keeps the support tree | `direnv_cmd_version_test`, `direnv_shells_test`, rubric R-10 |

Every graded suite closes over at least one manifest row, and every manifest row is named by at least one trajectory step.

## Checker identifier set

Reward is the summed weight of completely passing groups divided by total weight. All twelve weights are 1, so reward is `passed_groups / 12`. Per `tests/test_outputs.py`, a group passes only when `cargo test` exits zero, its final summary reads `ok`, it runs at least the `minimum_tests` declared for the suite in `tests/config.json`, and it reports no ignored tests. This is a group score, not a fraction of passing assertions, and adding failures inside an already-failing group does not reduce it again.

| group | minimum native tests | trajectory step |
| :-- | --: | :-- |
| `direnv_cmd_version_test` | 1 | S2 |
| `direnv_deps_test` | 18 | S3 |
| `direnv_dotenv_parse_test` | 14 | S4 |
| `direnv_env_diff_test` | 5 | S5 |
| `direnv_env_test` | 3 | S6 |
| `direnv_packages_test` | 7 | S7 |
| `direnv_rc_test` | 1 | S8 |
| `direnv_shell_systemd_test` | 3 | S9 |
| `direnv_shell_test` | 2 | S10 |
| `direnv_shells_test` | 19 | S11 |
| `direnv_sri_test` | 4 | S12 |
| `direnv_lifecycle` | 3 | S13 |

`tests/rubrics.json` declares fifteen equally weighted binary criteria `R-01` through `R-15` for independent human review. Per the `rubric_evaluation` block of `tests/config.json` the rubric score is reported separately from the deterministic reward, `tests/score_tests.py` computes reward from suite states alone, and there are no separate instruction-following or code-quality channels. Steps cite rubric ids only to show the reference route does not contradict them.

## Preconditions

All twelve groups fail as a block, before any suite runs, if any precondition below is unmet.

1. `Cargo.toml` exists at the workspace root. `tests/test_outputs.py` checks `required_manifests` first and fails every suite with `missing_target_manifests` when it is absent.
2. No production Go source remains. The verifier globs `**/*.go` and reports `remaining_production_source` for any match, after excluding paths containing a `target`, `node_modules`, `.git`, `tests`, `test`, `testdata`, `examples` or `fixtures` component, and excluding filenames ending `_test.go`, `.test.ts`, `.spec.ts` or `.d.ts`. Original tests, fixtures and documentation are permitted to remain and are expected to; only production sources must go.
3. `cargo generate-lockfile --offline` succeeds against the private suite manifest, which points at the copied subject tree. Failure returns `Submitted package dependencies do not resolve in the documented offline runtime` for all twelve suites.
4. Direct runtime dependencies stay inside the allowed families and versions: `base64` 0.22, `flate2` 1, `getrandom` 0.2, `libc` 0.2, `regex` 1, `serde_json` 1, `sha2` 0.10, `toml` 0.8 and `ureq` 2, at the versions present in the cached registry. Transitive dependencies of those crates are permitted.
5. Suites execute under `cargo test --locked --offline --test <target> -- --test-threads=1 --exact`. Tests are single-threaded and name-exact, so a suite that relies on parallel execution or on fuzzy name matching will not run as the verifier runs it.

## Golden trajectory

### S1 - Stand up the Rust crate and remove production Go

Add a root `Cargo.toml` exposing the library and the executable under the name `direnv`, commit `Cargo.lock`, and port the `internal/cmd` command surface and `gzenv` package to Rust. Delete the production `.go` sources across `internal/cmd`, `gzenv` and the module root, and remove the Go build wiring. Keep the original `_test.go` files, fixtures, documentation and the shell support tree, which the verifier's exclusion rules permit and which rubric R-12 explicitly does not penalise. Preserve `version.txt` at the repository root, which the verifier copies into the private suite as a root fixture.

- Established state: an offline-resolvable Rust crate and executable with no production Go left for the legacy scan to find.
- Drift survived: the legacy scan excludes test and fixture paths, so a migration that leaves a production `.go` file inside a directory named `test` passes the scan while leaving real Go on the production path. That is a defect the scan will not catch and rubric R-12 will.
- Satisfies: preconditions 1 through 4 for all twelve suites. Consistent with rubrics R-11, R-12 and R-14.

### S2 - Preserve version reporting and comparison

Read the retained root `version.txt` and expose the version through the command surface, keeping semantic-version validity and ordering semantics identical to the original. The verifier copies `version.txt` from the subject into the private suite before running, so the value the suite reads is the value the candidate ships.

- Established state: a version command whose source of truth is the committed fixture rather than a compiled-in constant.
- Drift survived: hard-coding the version string into the binary passes a smoke test and diverges the moment the fixture changes, which is exactly what this suite exercises.
- Satisfies: `direnv_cmd_version_test`, at least 1 native test. Consistent with rubric R-07.

### S3 - Reproduce the Go standard-library behaviours direnv depends on

Port the standard-library surface the original relied on so that observable behaviour matches, not merely compiles. Cover lexical path handling for base, directory, clean and relative operations; the Go duration grammar for both parsing and rendering, including the rejections; the `os.Expand` awkward cases; JSON encoding including control-character escaping, HTML-like escaping, indentation and number round-tripping; semantic-version validity and comparison; strict RFC 3339 text marshalling; and the hook template that substitutes the executable's own path. Implement the configured log-filter regex so that acceptance, rejection and matching decisions match the original, including ASCII-only Perl classes, literal braces and quoting, named-group handling, and rejection of invalid repetition.

- Established state: a compatibility layer whose decisions match the original across the eighteen cases this suite names.
- Drift survived: three of these are silent by construction. Go's `encoding/json` escapes `<`, `>` and `&` into `\u003c`, `\u003e` and `\u0026` by default and `serde_json` does not, so output stays valid JSON and stops matching. Go's `path.Clean` is purely lexical while `Path::canonicalize` touches the filesystem, so the Rust version succeeds on the same inputs and resolves symlinks the original never resolved. Go's duration renderer has a specific unit-selection rule that a hand-rolled formatter reproduces for round numbers and misses in the tail.
- Satisfies: `direnv_deps_test`, at least 18 native tests. Consistent with rubrics R-07 and R-15. Prescribes no intermediate regex translation string.

### S4 - Parse dotenv files with the original acceptance and failure behaviour

Implement dotenv parsing across the plain, quoted, exported, YAML-style, nested JSON, multiline and mixed-multiline forms, the solo empty assignment, comment override, and variable expansion with and without defaults. Preserve the original failure behaviour for an unclosed quote and for the must-parse entry point: both cases are declared `#[should_panic]` in the frozen `dotenv_parse_test.rs` asset (`test_dot_env_unclosed_quote`, `test_failing_must_parse`), so they must fail loudly rather than returning a partial or empty environment.

- Established state: a parser whose accepted set and failure set both match the original.
- Drift survived: the tempting Rust idiom is to return `Result` and let the caller decide. For these two cases the suite asserts a panic, so a parser that swallows an unclosed quote and returns the successfully parsed prefix reads as robust and fails the case.
- Satisfies: `direnv_dotenv_parse_test`, at least 14 native tests. Consistent with rubric R-02.

### S5 - Keep environment diffs reversible and distinguish empty from unset

Compute the forward and reverse diff between two environments so that applying the reverse restores the original exactly. Treat an empty value and an absent variable as distinct states in both directions, and honour the ignored-variable set so that shell bookkeeping does not leak into the diff.

- Established state: a diff that round-trips without loss for the five cases this suite names.
- Drift survived: representing an unset variable as an empty string collapses two distinct states into one, which round-trips cleanly in every test that does not contain an empty value and corrupts the environment in every test that does.
- Satisfies: `direnv_env_diff_test`, at least 5 native tests. Consistent with rubric R-03.

### S6 - Serialise and restore the compressed environment

Implement the compressed environment codec over the allowed `flate2` and `base64` crates so that a serialised environment round-trips. Accept CR and LF inside the encoded payload rather than rejecting a wrapped base64 body, which the frozen `env_test.rs` asset checks in `compressed_environment_accepts_base64_line_breaks`, and retain original-input error positions when the payload is malformed. Ensure the serialised diff reverses empty, unset and changed values together.

- Established state: a codec that accepts what the original accepted, including line-wrapped payloads, and reports position-accurate errors on what it rejects.
- Drift survived: a strict base64 decoder rejects a payload wrapped at a line width, which never occurs in short fixtures and occurs routinely in real environments. Recomputing error positions against the decoded buffer rather than the original input reports offsets that do not correspond to anything the caller can see.
- Satisfies: `direnv_env_test`, at least 3 native tests. Consistent with rubrics R-03 and R-05.

### S7 - Complete the package-level surfaces for gzenv, SRI and XDG

Report compressed-environment failures the way the original did, support every integrity algorithm the original supported with its digest encoding, and reject bad hashes on the same terms. Resolve XDG base directories with the original fallback order: prefer an explicit XDG home, fall back to the user home when it is unset, and resolve to empty when no home is available at all rather than substituting a default path.

- Established state: the package-level behaviours that the command layer composes over.
- Drift survived: the empty-without-home case is the one most often coded away. Substituting a plausible default such as `/root/.config` when `HOME` is unset turns a deliberate empty result into a path that may exist and may be written to.
- Satisfies: `direnv_packages_test`, at least 7 native tests. Consistent with rubrics R-04, R-05 and R-06.

### S8 - Preserve authorization and directory traversal

Port the rc layer so that authorization is required before an environment file is applied, denial is recorded and honoured, a changed file invalidates its prior authorization, and the whitelist behaviour matches the original. Traverse directories and select configuration files by the original rules.

- Established state: an authorization gate whose state is keyed to file content, not only to path.
- Drift survived: keying authorization to the path alone makes an edited file remain authorized, which is the exact failure the changed-file invalidation exists to prevent and which no happy-path test surfaces.
- Satisfies: `direnv_rc_test`, at least 1 native test. Consistent with rubrics R-08 and R-09.

### S9 - Preserve systemd export and encapsulation

Render the systemd export form and preserve the encapsulation cut behaviour the original implemented, so that values carrying delimiters survive the round trip through a systemd environment block.

- Established state: a systemd renderer that matches the original on both the ordinary export and the encapsulated case.
- Drift survived: systemd environment syntax has its own quoting rules that differ from POSIX shell quoting, so reusing the bash escaper here produces output that looks correct and is parsed differently by systemd.
- Satisfies: `direnv_shell_systemd_test`, at least 3 native tests. Consistent with rubrics R-01 and R-10.

### S10 - Preserve bash escaping and shell detection

Implement bash value escaping to match the original byte for byte across the special-character set, and preserve the shell-detection logic that picks a backend from the invoking environment.

- Established state: the escaping and detection pair the hook path depends on.
- Drift survived: several distinct escaping strategies produce output bash evaluates identically, so a rewritten escaper can be functionally correct under evaluation and still fail a string comparison against the original rendering.
- Satisfies: `direnv_shell_test`, at least 2 native tests. Consistent with rubric R-01.

### S11 - Render every supported shell to match the original

Provide renderers for bash, elvish, fish, json, murex, pwsh, systemd, tcsh, vim and zsh, each matching the original's output. Keep the retained shell support files operational against these renderers so the generated hooks and the Rust executable work together under the original calling conventions.

- Established state: ten renderers, one per supported shell, each asserted against the original rendering.
- Drift survived: this suite requires at least nineteen native tests spread across the ten renderers, so dropping a niche shell such as murex or elvish removes its cases, drops the observed count below the minimum and fails the whole group even when every retained renderer is correct.
- Satisfies: `direnv_shells_test`, at least 19 native tests. Consistent with rubrics R-01 and R-10.

### S12 - Preserve the integrity parser and writer

Implement the subresource-integrity parser and writer as a matched pair, so a value written by the writer parses back through the parser and a value the original wrote parses identically.

- Established state: a round-tripping integrity representation over the supported algorithm set.
- Drift survived: base64 padding and algorithm-prefix spelling are easy to normalise incidentally, which keeps the pair self-consistent while breaking agreement with integrity strings the original emitted.
- Satisfies: `direnv_sri_test`, at least 4 native tests. Consistent with rubric R-06.

### S13 - Close the lifecycle end to end

Exercise the whole path through the executable: authorization is required before an environment applies and a change revokes it; entering and leaving a directory restores empty, unset and pre-existing values exactly; and a parent environment file applies to descendant directories while preserving quoted values. This step integrates S4 through S11 under the real command dispatch rather than at the library boundary.

- Established state: end-to-end agreement with the original across the three lifecycle cases, which is the only step that exercises parser, diff, authorization, traversal and shell rendering together.
- Drift survived: each component can be individually correct while the composition loses state, most commonly by restoring a previously unset variable as empty on leave. Treat this as the integration gate rather than an independent feature.
- Satisfies: `direnv_lifecycle`, at least 3 native tests. Consistent with rubrics R-03, R-08 and R-09.

## Red lines

- Invoking the original Go implementation as a subprocess from any code path. Rubric R-13 names this directly. Legitimate shell evaluation that direnv itself requires is permitted and is not the prohibited case.
- Leaving production Go source anywhere the legacy scan reaches. This fails every suite at the precondition.
- Taking a direct runtime dependency outside the allowed families and versions, or one that requires a download. The offline lockfile step fails before any suite runs.
- Editing or adding tests in the expectation that they will be graded. The verifier materialises its own frozen suite from `config.assets` and never reads candidate tests.
- Restoring an unset variable as empty, or an empty variable as unset, on any path.

## Rejected routes

Each route below is a plausible implementation that a reviewer might accept and the graded surface rejects. The named control is the check that catches it.

| rejected route | why it looks correct | control that rejects it |
| :-- | :-- | :-- |
| Shell out to the original Go binary | reproduces every behaviour exactly | legacy scan, rubric R-13 |
| Use `serde_json` defaults for encoding | emits valid, readable JSON | `direnv_deps_test` |
| Use `Path::canonicalize` for path cleaning | correct for every path that exists | `direnv_deps_test` |
| Return `Err` where the original panics | idiomatic Rust error handling | `direnv_dotenv_parse_test` |
| Represent unset as empty string | round-trips in every test without empty values | `direnv_env_diff_test`, `direnv_lifecycle` |
| Reject line-wrapped base64 payloads | strict and defensible | `direnv_env_test` |
| Default XDG to a conventional path when `HOME` is unset | avoids an awkward empty result | `direnv_packages_test` |
| Key authorization to path only | passes every unmodified-file test | `direnv_rc_test` |
| Drop a niche shell renderer | every retained renderer stays correct | `direnv_shells_test` minimum of 19 |
| Reuse bash escaping for systemd | evaluates correctly under bash | `direnv_shell_systemd_test` |
| Normalise SRI padding or prefix spelling | parser and writer stay self-consistent | `direnv_sri_test` |
| Assert a specific regex translation string | appears to pin behaviour precisely | rubric R-15 forbids requiring one; the `audited_config` cases check decisions, not strings |

## Reconciliation

The trajectory step set is `{S1..S13}`. The graded group set named by the steps is `{direnv_cmd_version_test, direnv_deps_test, direnv_dotenv_parse_test, direnv_env_diff_test, direnv_env_test, direnv_packages_test, direnv_rc_test, direnv_shell_systemd_test, direnv_shell_test, direnv_shells_test, direnv_sri_test, direnv_lifecycle}`, which is exactly the key set of `tests/test_weights.json` and exactly the suite `id` list of `tests/config.json`, in both directions and with no surplus on either side. S1 binds the preconditions rather than a group, which is why thirteen steps close over twelve groups.

Every manifest row D1 through D12 is named by at least one step, and every step names at least one manifest row. Rubric ids R-01 through R-15 are cited for consistency only and contribute nothing to the deterministic reward.

The `file_times` surface and the `audited_config` filter cases are named in the Scope boundary section. The former appears in no step because no graded suite exercises it, and no step prescribes a regex translation string.

Open gaps recorded against this bundle: `solution/grounding.yaml` and `solution/recompute.py` are absent, so this file is hand-derived and not regenerated; no feasibility bundle exists, so the rejected routes above are reasoned from committed bytes rather than measured against executed negative controls.
