FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS python-fetch

# S-002 (partial): pipefail makes the curl|tar pipeline fail loud on curl errors;
# SHA256 verification deferred per user constraint (curl|tar format required).
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

ARG TARGETARCH=amd64

RUN mkdir -p /opt/python && \
    case "${TARGETARCH}" in \
        amd64) ARCH="x86_64-unknown-linux-gnu" ;; \
        arm64) ARCH="aarch64-unknown-linux-gnu" ;; \
        *) echo "Unsupported: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/indygreg/python-build-standalone/releases/download/20240107/cpython-3.12.1+20240107-${ARCH}-install_only.tar.gz" \
    | tar -xzC /opt/python --strip-components=1

# ============================================
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos/dan-nor98__pypostboy@sha256:1ed9bae136ae004c5bda55743c5fbae6a124c84df7f9f45f1b20c3427c4b421b

USER root

COPY --from=python-fetch /opt/python /opt/python

# marker for language-specific fixes

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        patch \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* 
    
ARG MSB_REF=83e18683062efc1a3ba5693e5c6588c57ac5f095
RUN /opt/python/bin/python3 -m pip install --no-cache-dir \
    "multi-swe-bench @ git+https://github.com/Ethara-Ai/multi-swe-bench.git@${MSB_REF}"
    
# Provide a standardized workspace while keeping upstream layout intact
RUN mkdir -p /workspace && \
    ln -sfn /home/pypostboy /workspace/pypostboy && \
    git config --global --add safe.directory /home/pypostboy && \
    git config --global --add safe.directory /workspace/pypostboy

WORKDIR /workspace/pypostboy

ENV PYTHONUNBUFFERED=1

