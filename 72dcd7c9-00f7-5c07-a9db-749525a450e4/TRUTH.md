# TRUTH.md - evanepio__dotmanca-157

## Defect

The test suite is only partially compatible with idiomatic pytest usage:

- Model URL tests are organized as `django.test.TestCase` subclasses and use unittest assertion methods.
- Several function-style tests in the main application evaluate comparison or membership expressions without asserting them, so they pass even when the expected behavior is absent.
- Age tests use a custom context manager and mock the standard-library datetime class globally rather than using pytest’s built-in patching support.
- The application obtains the current date directly inside its age calculation, leaving no narrow, application-owned seam for deterministic date-based tests.

The migration must preserve the scenarios currently exercised and must not change application-visible URL, context, or age behavior.

## Root cause

The suite mixes unittest conventions with pytest-style test functions. Pytest can often collect unittest tests, which masks the fact that the migration has not actually happened. It also does not reinterpret bare boolean expressions as assertions; expressions such as checking that a key is present or that an age equals an expected number have no effect unless used in an assertion.

The age calculation is coupled directly to the system clock. Consequently, deterministic birthday-boundary tests must replace a standard-library datetime object rather than patching an application-level dependency. That approach is broader than necessary and is awkward to express with pytest fixtures.

## Solution shape

A correct result must have these properties:

- The affected suite is expressed as pytest tests rather than Django/unittest test cases.
- Tests use effective Python `assert` statements so failures in the expected behavior are observable.
- Test discovery remains straightforward under pytest, using discoverable test functions or pytest-compatible classes and methods.
- Every existing scenario remains represented:
  - Character URLs contain both the character slug and its team slug.
  - Issue URLs contain both the issue slug and its arc slug.
  - Gallery URLs contain the gallery slug.
  - Gallery-image URLs contain both the image slug and its gallery slug.
  - News-article URLs contain the publication date path and article slug.
  - Place URLs contain the place slug.
  - Both biography views expose an age.
  - Both biography age calculations handle the birthday and the preceding day correctly.
  - Home-page context contains the news collection under the expected key, including the existing multi-article setup.
- Date-sensitive tests use a pytest-supported isolation mechanism and do not depend on the actual day on which the suite runs.
- Production age calculations still use the real current local date by default.
- No database dependency is introduced for tests that only construct unsaved model objects.
- Existing application behavior and existing passing tests remain intact.

## Load-bearing work

- `characters/tests.py`
  - Remove dependence on Django’s unittest base class.
  - Keep separate pytest-discoverable checks for the character’s own slug and the related team slug in the generated absolute URL.
  - Use real assertions.

- `comics/tests.py`
  - Convert the issue URL scenarios to pytest-native tests.
  - Retain checks for both the issue slug and the related arc slug.
  - Continue using unsaved model instances because persistence is unnecessary for this behavior.

- `gallery/tests.py`
  - Convert gallery and gallery-image URL coverage to pytest-native tests.
  - Preserve the gallery URL check and both components of the gallery-image URL behavior.
  - Ensure all expectations are executable assertions.

- `main/tests.py`
  - Replace inert membership and equality expressions with actual assertions.
  - Preserve age-key coverage for both biography views.
  - Preserve the birthday-boundary cases for both people.
  - Use pytest’s fixture-based patching, or an equivalent pytest-compatible technique, to control the application’s notion of the current date.
  - Keep the existing home-page context scenarios and make their stated context-key expectation effective.
  - Remove custom unittest/mock infrastructure that is no longer needed.

- `main/views.py`
  - Introduce a narrow application-owned seam for obtaining the current date, and have the age calculation use that seam.
  - The default implementation must retain the prior production behavior of reading today’s local calendar date.
  - Do not alter the birthday comparison or the resulting age semantics.

- `news/tests.py`
  - Convert the publication-date and slug URL checks from unittest style to pytest-native tests.
  - Keep the fixed date formatting expectation and the slug-presence expectation.

- `places/tests.py`
  - Convert the place URL test from a Django/unittest case to a pytest-native test.
  - Retain the slug-presence behavior as a real assertion.

## Solution space

Several implementations can satisfy the migration:

1. **Top-level pytest functions**
   - Flatten the former unittest classes into discoverable module-level test functions.
   - Use plain assertions and pytest fixtures directly.

2. **Pytest-compatible grouping classes**
   - Keep logical class groupings, provided they do not inherit from `unittest.TestCase` or Django’s `TestCase`, require no unittest lifecycle, and contain pytest-discoverable methods using plain assertions.

3. **Clock isolation through an application seam**
   - Add a small module-level provider for today’s date and patch that provider with pytest’s monkeypatch fixture.
   - Inject a clock/date provider into the age-calculation path while retaining the same public view behavior.
   - Encapsulate current-date access in another application-owned object or callable that tests can replace cleanly.

4. **Alternative deterministic-time tooling**
   - A pytest-compatible time-freezing fixture or library is acceptable if it is already an appropriate project dependency and reliably restores global state.
   - Direct patching of the date source can also be valid if scoped narrowly to the application module and compatible with immutable built-in date types.

5. **Equivalent assertion forms**
   - Membership may be asserted against the mapping directly or its keys.
   - Equality may place either expected or actual value first.
   - URL checks may use substring membership or another equivalent assertion that proves the same URL component is present.

The exact arrangement and naming of tests need not match any single implementation. What matters is pytest-native collection, meaningful assertions, deterministic date testing, and preserved coverage.

## Ordered plan

1. Inventory the existing test scenarios in each affected application so none are lost during structural conversion.
2. Identify which tests require Django database support and which only instantiate unsaved objects. Keep the latter as lightweight unit tests without database markers or Django test-case inheritance.
3. Convert each unittest-based URL test group into pytest-discoverable functions or pytest-compatible grouping classes.
4. Replace unittest assertion methods with plain assertions while preserving the original inputs and expected URL components.
5. Audit the already function-style main tests for expressions that do not assert anything, and turn each intended expectation into an effective assertion.
6. Create a narrow date-source boundary in the main view logic. Route age calculation through it while preserving the real current-date default.
7. Rewrite birthday-boundary tests to override only that application-owned date source through pytest fixture support, ensuring automatic cleanup after each test.
8. Remove obsolete unittest imports, Django test-case imports, custom patching helpers, and other dead test infrastructure.
9. Run pytest over the complete repository, not only the edited modules, to verify collection and compatibility.
10. Confirm that the date override does not leak between tests and that production execution still uses the real current date.

## Pitfalls

- Merely running the old `TestCase` classes under pytest does not constitute a unittest-to-pytest migration.
- Removing class inheritance without renaming or restructuring tests can make pytest stop collecting them.
- Bare expressions are not assertions; they silently pass regardless of value.
- Replacing assertions with tautologies, such as checking a locally assigned value against itself, loses behavioral coverage.
- Patching the wrong import location may leave the production call untouched.
- Replacing `datetime.date.today` directly can fail because built-in date and datetime types are not always safely mutable.
- Broadly replacing the global datetime class can affect unrelated modules or leak state when cleanup is incorrect.
- A test double may return either a date-like or datetime-like value, but the production calculation must continue to operate consistently from its year, month, and day fields.
- Accidentally changing birthday comparison boundaries can make age decrement on the birthday itself or fail to decrement on the day before it.
- Adding database markers or retaining Django `TestCase` solely for unsaved model URL tests adds unnecessary setup and obscures the migration.
- Combining the two components of a nested URL into one weak test can reduce diagnostic clarity or inadvertently drop coverage of one slug.
- A test whose name mentions limiting news items must not be “strengthened” in a way that changes the task’s expected behavior unless the application contract independently requires that new assertion.
- Hard-coding a fake current date in production logic would make tests deterministic at the cost of breaking application behavior.

## Cheat surface

A superficially passing change is insufficient if it does any of the following:

- Leaves unittest or Django `TestCase` subclasses in place and relies on pytest’s unittest compatibility.
- Deletes or skips the existing scenarios.
- Keeps no-op comparisons or membership expressions.
- Replaces meaningful checks with unconditional assertions.
- Mocks model URL methods rather than exercising their real implementations.
- Hard-codes expected slugs, dates, ages, or URLs in production code specifically for the test inputs.
- Alters the age calculation to return the expected examples without preserving general birthday behavior.
- Makes the production clock permanently return a fixed test date.
- Patches global time without restoring it, allowing order-dependent passes.
- Runs only selected migrated tests while leaving the complete suite broken.
- Adds configuration that excludes failing or unmigrated tests from collection.

## Success criteria

- Running the repository’s pytest suite collects and passes all existing and migrated tests.
- The affected test modules no longer depend on unittest-style test-case inheritance or unittest assertion APIs.
- Every expected membership and equality condition is enforced by a real assertion.
- All original URL-component scenarios remain collected and pass against the real model methods.
- Both biography views expose an age in their context.
- For each covered birthday, the age is ten on the tenth birthday and nine on the preceding day.
- Date-sensitive tests are deterministic and independent of the machine’s current date.
- The application’s default age calculation still uses the actual current local date.
- Home-page context tests still exercise and verify the expected news context entry.
- No test-state leakage, new database requirement, collection regression, or unrelated application behavior change is introduced.

## Verification

Run the existing test suite on the migrated tree and confirm it passes; this bundle does not enumerate it.

## Provenance

```yaml
uuid: 72dcd7c9-00f7-5c07-a9db-749525a450e4
instance_id: evanepio__dotmanca-157
fix_patch_sha256: 6970394405ba35ac01fd07a13901a24e67e76faa819a53eab3d012abba2d4c6e
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
