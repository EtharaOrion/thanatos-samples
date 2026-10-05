# The task environment is the prebuilt image task.toml pins as [environment].docker_image: the starting
# repository is already at /workspace, the yarn dependency cache at /opt/twenty-cache (restored into a tree
# by /usr/local/bin/prepare-twenty), with PostgreSQL, Redis and the Node toolchain installed.
# Keep this FROM identical to that pin. Building this file (harbor run --force-build) pulls the image
# from ECR, so it needs the same registry access as a normal run.
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos-envs@sha256:803cb98fdadd11071b4e17129f2f9109a9da7d6192c499633bd8ff2ab6310b03
