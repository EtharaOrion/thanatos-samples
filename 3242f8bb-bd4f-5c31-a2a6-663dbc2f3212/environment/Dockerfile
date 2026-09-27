# Environment image for the direnv Go -> Rust migration task.
#
# This image is built from public, digest-pinned sources only. There is no
# private registry reference and no multi-stage copy out of a harness image:
# everything the task needs is installed here from an upstream URL with a
# recorded checksum, so anyone holding this bundle can rebuild it.
#
# What this replaced:
#   FROM <account>.dkr.ecr.<region>.amazonaws.com/... AS agent-files  (private ECR)
#   FROM argos-qc-starr@sha256:...                                   (bare repository
#          name, which Docker resolves to docker.io/library/argos-qc-starr and which
#          does not exist)
# Neither was pullable, so the previous file could not build for anyone.
#
# Solver runtime (the agent's own Python venv, vendored SDK and runner, and
# LITELLM_LOCAL_MODEL_COST_MAP) is deliberately NOT baked in. The harness
# injects that at run time. A task image that carries it cannot be rebuilt by
# anyone who does not also hold the harness image, which is the failure this
# file exists to avoid.
#
# Grading runs the frozen conformance suites offline. Every dependency the
# submission is allowed to use is fetched at build time and the image is then
# switched to offline mode, so a missing crate surfaces as a build failure here
# rather than as a plausible-looking low reward during grading.

# Crate download stage. It runs on the BUILD machine's own architecture: crates are
# architecture-independent source archives, and `cargo fetch` without --target
# downloads the packages of every platform, so the cache it produces is identical
# for amd64 and arm64. Running it natively avoids executing rustc under QEMU
# emulation, which crashes when the amd64 image is built on an arm64 host.
FROM --platform=$BUILDPLATFORM rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57 AS crates
COPY deps/ /tmp/cache-manifests/
RUN set -eux; \
    CARGO_NET_OFFLINE=false cargo fetch --locked --manifest-path /tmp/cache-manifests/ants_/Cargo.toml; \
    CARGO_NET_OFFLINE=false cargo fetch --locked --manifest-path /tmp/cache-manifests/direnv/Cargo.toml

FROM rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57

# Go is present so the agent can read and run the original implementation it is
# migrating. Same version and checksums as the sibling starr task image.
ARG GO_VERSION=1.27.1
ARG GO_SHA256_amd64=63d339f0da5ab53635a56f2490a7984dfe12dfcff22ad749f63edaf590168445
ARG GO_SHA256_arm64=3450b45a3f9ee8568792736a5c5e70a1f2e9b36c35a8f74958c03e51d7d92bec

ENV GOROOT=/usr/local/go \
    GOPATH=/go \
    GOMODCACHE=/go/pkg/mod \
    PATH=/usr/local/go/bin:/go/bin:/usr/local/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# ca-certificates/curl are needed for the pinned downloads below. git is
# required because solution/solve.sh applies fix.patch with `git apply`.
# python3 runs tests/test.sh and tests/score_tests.py; both are stdlib-only,
# so there is no pip install step.
# The shells are load-bearing: the conformance suites exercise direnv's export
# and escaping behaviour for bash, zsh, fish and tcsh. Shells the suites only
# assert about as generated text (elvish, murex, pwsh) are not installed,
# because nothing executes them.
# nodejs/npm and tmux are retained from the previous image definition.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fish \
        git \
        make \
        nodejs \
        npm \
        python3 \
        tcsh \
        tmux \
        zsh \
    && rm -rf /var/lib/apt/lists/*

# Go toolchain, checksum-verified. dpkg --print-architecture is used rather
# than BuildKit's TARGETARCH so this also builds under a plain docker build.
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) go_sha256="$GO_SHA256_amd64" ;; \
        arm64) go_sha256="$GO_SHA256_arm64" ;; \
        *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    curl -fsSL --retry 3 -o /tmp/go.tar.gz "https://dl.google.com/go/go${GO_VERSION}.linux-${arch}.tar.gz"; \
    printf '%s  /tmp/go.tar.gz\n' "$go_sha256" | sha256sum -c -; \
    rm -rf /usr/local/go; \
    tar -C /usr/local -xzf /tmp/go.tar.gz; \
    rm -f /tmp/go.tar.gz; \
    go version

# Module cache for the original Go implementation, so the agent can build and
# run it for reference after the image goes offline. Fetched from the
# workspace's own go.mod/go.sum, which pin every version.
COPY workspace/go.mod workspace/go.sum /tmp/gomod/
RUN set -eux; \
    cd /tmp/gomod; \
    GOFLAGS=-mod=mod go mod download all; \
    cd /; \
    rm -rf /tmp/gomod

# Crate cache for the dependencies the instruction allows the Rust port to use.
# deps/ ships a lockfile beside each manifest, so --locked pins exact versions.
# Fetched in the `crates` stage above and copied in unchanged.
COPY --from=crates /usr/local/cargo/registry /usr/local/cargo/registry
COPY --from=crates /usr/local/cargo/.global-cache /usr/local/cargo/.package-cache /usr/local/cargo/.package-cache-mutate /usr/local/cargo/

# The verifier drops test processes to an unprivileged uid. A cache only root
# can read is indistinguishable from a missing dependency once the image is
# offline, so widen the permissions here.
RUN chmod -R a+rwX /usr/local/cargo/registry /go/pkg/mod

# Grading creates the container without passing environment flags, so the
# offline contract has to live in the image. GOPROXY=off and
# CARGO_NET_OFFLINE=true turn any dependency that was not cached above into a
# hard error instead of a silent network fetch.
ENV CARGO_NET_OFFLINE=true \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=0 \
    GOTOOLCHAIN=local \
    GOPROXY=off \
    GOSUMDB=off \
    GOFLAGS=-buildvcs=false \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY workspace/ /workspace/

# direnv's own test fixture test/scenarios/symlink-bug is a symlink loop (foo/bar -> ..). It is created here
# instead of being shipped in the task folder: Harbor hashes the whole task folder before a run and refuses a
# cyclic symlink, while the image must still carry the fixture exactly as upstream has it.
RUN ln -s .. /workspace/test/scenarios/symlink-bug/foo/bar

# Playbook 15b: pin the executable bits in the image so a future repack that
# loses file modes cannot silently turn these into mode 644, make every probe
# exit 126, and leave the checker that exists to detect the interpreter
# passing vacuously. These are exactly the 15 files that are mode 755 in the
# shipped workspace.
#
# test/direnv-test.bash and test/direnv-test.ps1 are intentionally NOT in this
# list: GNUmakefile invokes them as `bash ./test/direnv-test.bash` and
# `pwsh ./test/direnv-test.ps1`, with an explicit interpreter, and both are
# mode 644 upstream at base_commit b00e451f.
RUN set -eux; \
    chmod 755 \
        /workspace/install.sh \
        /workspace/stdlib.sh \
        /workspace/script/dist-push \
        /workspace/script/prepare-release.sh \
        /workspace/script/update-gomod2nix \
        /workspace/test/direnv-test-common.sh \
        /workspace/test/direnv-test.elv \
        /workspace/test/direnv-test.fish \
        /workspace/test/direnv-test.mx \
        /workspace/test/direnv-test.tcsh \
        /workspace/test/direnv-test.zsh \
        /workspace/test/scenarios/in-envrc/test-in-envrc \
        /workspace/test/show-direnv-diff.sh \
        /workspace/test/stdlib.bash \
        /workspace/test/strict_env_test.bash; \
    test -x /workspace/test/direnv-test-common.sh

CMD ["/bin/bash"]
