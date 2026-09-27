# Grader image for repl-mcp-sdk-2 (Harbor separate verifier; Harbor builds it from tests/ when
# [verifier.environment].docker_image is not set, and task.toml pins the prebuilt copy of exactly this file).
# The agent never runs here: Harbor uploads the agent's /workspace after the agent finishes ([[artifacts]]).
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos-envs@sha256:e1cfac1adf3c926021ca35b528c5df4d6e1f601bdf707c7c211fcc12b1edf3ce AS grader-kit

FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos-envs@sha256:77e9488af944fe5cd7c7a64d0fab51916d9b61adae9460f3f4739aa8bde82529
# The rubric grader, baked in from the grader kit.
COPY --from=grader-kit /opt/grader/ /opt/grader/
# The original (starting) code for the rubric's before/after comparison. /workspace is emptied: the delivery
# is uploaded there, and a missing upload must grade as an empty delivery, never as the original code.
RUN cp -a /workspace /opt/grader/original && rm -rf /workspace && mkdir /workspace
COPY . /tests/
RUN chmod 755 /tests/test.sh
