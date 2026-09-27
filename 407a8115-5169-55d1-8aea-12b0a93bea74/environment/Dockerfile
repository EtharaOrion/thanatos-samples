FROM node:24.5.0-bookworm-slim@sha256:ac365b72b69807f4b0f73bcddccffbed7307cc6e296fddf778f3c6ffd6be2381 AS cache
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates curl build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY workspace/ /workspace/
ENV NODE_OPTIONS=--max-old-space-size=16384 YARN_ENABLE_HARDENED_MODE=0 YARN_ENABLE_CONSTRAINTS_CHECKS=0 YARN_ENABLE_TELEMETRY=0 NX_DAEMON=false
RUN node .yarn/releases/yarn-4.13.0.cjs workspaces focus twenty-server twenty-front
RUN python3 -c 'import os, pathlib, shutil; source=pathlib.Path("/workspace"); target=pathlib.Path("/opt/twenty-cache"); roots=[]; [(roots.append(pathlib.Path(root)/"node_modules"), dirs.remove("node_modules")) for root,dirs,files in os.walk(source) if "node_modules" in dirs]; [(p.parent.mkdir(parents=True,exist_ok=True), shutil.move(str(r),str(p))) for r in roots for p in [target/r.relative_to(source)]]; (target/".yarn").mkdir(exist_ok=True); shutil.copy2(source/".yarn/install-state.gz", target/".yarn/install-state.gz")'
# Solver runtime (agent venv, vendored SDK, agent_runner.py, LITELLM_LOCAL_MODEL_COST_MAP)
# is deliberately NOT baked into this image. The harness injects it at run time; a task
# image carrying it could not be rebuilt by anyone who does not also hold the harness
# image, which is the exact reproducibility failure this Dockerfile exists to avoid.
FROM node:24.5.0-bookworm-slim@sha256:ac365b72b69807f4b0f73bcddccffbed7307cc6e296fddf778f3c6ffd6be2381
ENV DEBIAN_FRONTEND=noninteractive NODE_OPTIONS=--max-old-space-size=16384 YARN_ENABLE_NETWORK=0 NX_DAEMON=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends postgresql postgresql-client redis-server python3 git ca-certificates curl build-essential bash procps tmux && rm -rf /var/lib/apt/lists/*
COPY --from=cache /opt/twenty-cache/ /opt/twenty-cache/
COPY workspace/ /workspace/
# Executable bits are re-asserted here so a future repack cannot silently ship these 644.
RUN chmod 755 /workspace/packages/twenty-docker/scripts/1-click.sh \
              /workspace/packages/twenty-docker/twenty-app-dev/rootfs/etc/s6-overlay/scripts/register-crons.sh
RUN printf '#!/bin/sh\nset -eu\ncp -a /opt/twenty-cache/. "${1:-/workspace}/"\n' > /usr/local/bin/prepare-twenty && chmod 755 /usr/local/bin/prepare-twenty
WORKDIR /workspace
ENTRYPOINT []
CMD ["bash"]
