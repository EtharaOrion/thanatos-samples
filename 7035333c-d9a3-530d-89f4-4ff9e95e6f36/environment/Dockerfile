# The task environment is the prebuilt image task.toml pins as [environment].docker_image: the starting
# repository is already at /workspace, with the .NET SDK and the restored NuGet packages at /opt/nuget/packages.
# Keep this FROM identical to that pin. Building this file (harbor run --force-build) pulls the image
# from ECR, so it needs the same registry access as a normal run.
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/thanatos-envs@sha256:77e9488af944fe5cd7c7a64d0fab51916d9b61adae9460f3f4739aa8bde82529
