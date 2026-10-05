# The task environment is the prebuilt image task.toml pins as [environment].docker_image: the starting
# repository is already at /workspace (including the test/scenarios/symlink-bug/foo/bar -> .. fixture),
# with the Rust, Go, Node, Python and shell toolchains and the offline cargo and Go module caches.
# Keep this FROM identical to that pin. Building this file (harbor run --force-build) pulls the image
# from ECR, so it needs the same registry access as a normal run.
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos-envs@sha256:68fbc9ed277dc73fafb58bf7e908f620d677dd41783d4947a8e11dc910c2ddfd
