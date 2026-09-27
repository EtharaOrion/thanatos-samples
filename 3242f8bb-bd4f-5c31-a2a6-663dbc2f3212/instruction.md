# Migrate direnv to Rust

Migrate the complete direnv library and executable while preserving shell export/escaping, dotenv parsing and error handling, reversible environment diffs including empty and unset values, XDG fallback rules, compressed environment serialization, integrity algorithms, version comparisons, authorization and directory traversal. Keep shell support files operational. Expose the Rust crate and executable as direnv. Allowed cached dependencies: base64 0.22, flate2 1, getrandom 0.2, libc 0.2, regex 1, serde_json 1, sha2 0.10, toml 0.8 and ureq 2; use versions in the cached registry.

The repository is at `/workspace`. `TARGET_API.md` gives the required Rust compatibility surface. Preserve observable source behavior, not only compilation. Remove production code in the old language; original tests, fixtures and documentation may remain. Do not use subprocess calls into the old implementation. The verifier uses independent frozen integration tests, not tests you add or edit.

Run cargo offline; package downloads are unavailable. Rust, Go, Node, Python and common shells are installed for local inspection. You may reorganize internals while preserving the documented API and executable behavior.
