FROM mcr.microsoft.com/dotnet/sdk:10.0@sha256:35d40304542c8689331f8cab17c65926cdf48fe711e289321d71924b230a7d29 AS cache
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 NUGET_PACKAGES=/opt/nuget/packages
COPY cache-manifests/ /restore/
RUN cd /restore/target && dotnet restore src/Repl.McpTests/Repl.McpTests.csproj --disable-parallel
RUN cd /restore/base && dotnet restore src/Repl.McpTests/Repl.McpTests.csproj --disable-parallel
FROM mcr.microsoft.com/dotnet/sdk:10.0@sha256:35d40304542c8689331f8cab17c65926cdf48fe711e289321d71924b230a7d29
ENV DEBIAN_FRONTEND=noninteractive DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 NUGET_PACKAGES=/opt/nuget/packages PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 git curl ca-certificates bash procps tmux && rm -rf /var/lib/apt/lists/*
COPY --from=cache /opt/nuget/packages/ /opt/nuget/packages/
COPY workspace/ /workspace/
# Pin executable bits: packaging can drop the +x mode, which makes every script
# probe exit 126 and lets a checker pass vacuously (QA playbook 15b).
RUN find /workspace -type f \( -name '*.sh' -o -name 'entrypoint*' \) -exec chmod 755 {} +
WORKDIR /workspace
ENTRYPOINT []
CMD ["bash"]
