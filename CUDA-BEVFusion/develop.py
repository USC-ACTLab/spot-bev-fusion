import os
import subprocess
import argparse

import docker
import docker.errors
import docker.types

def lookForDevContainer(docker_client, image_label=None):
    """
    look for the dev image locally; build if it doesn't exist
    """
    if image_label is None:
        print("Using default nvidia cuda 12.4.1-cudnn-devel-ubuntu22.04")
        dev_image_label = "nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04"
    else:
        dev_image_label = image_label

    try:
        dev_container = docker_client.images.get(dev_image_label)
    except docker.errors.ImageNotFound:
        print("Image not found")
        if (image_label is None):
            print("Pulling image from remote")
            dev_container = docker_client.images.pull("nvidia/cuda", tag="12.4.1-cudnn-devel-ubuntu22.04")
        else:
            print("Building custom image")
            dev_container = docker_client.images.build(path=".", tag=dev_image_label, rm=True)
    finally:
        return dev_container


def startDevContainer(docker_client, image):
    """
    mount current repo and sub folders containing code into the container
    """
    current_dir = os.path.join(os.path.abspath(os.getcwd()),'..')
    mount_path = "/opt/bev_fusion"

    # Create volume mounts for each subdirectory
    volumes = {current_dir: {"bind": mount_path, "mode": "rw"}}

    device_request = [
        docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
    ]

    enviornment = [
        "NVIDIA_VISIBLE_DEVICES=all",
        "NVIDIA_DRIVER_CAPABILITIES=all"
    ]

    # Create the container
    container = docker_client.containers.create(image, 
                                                volumes=volumes, 
                                                command="bash", 
                                                tty=True, 
                                                stdin_open=True,
                                                auto_remove=True,
                                                runtime='nvidia',
                                                device_requests=device_request,
                                                environment=enviornment)
    container.start()
    return container


def buildSourceFiles(running_container):
    worker_cnt = os.cpu_count() - 2;
    build_cmd = "source /opt/ros/humble/setup.bash && cd /ros_ws && colcon build --symlink-install --parallel-workers "\
        + str(worker_cnt)
    print("Building with " + str(worker_cnt) + " workers")
    try:
        _, stream = running_container.exec_run(f"bash -c '{build_cmd}'", stream=True, tty=True, workdir="/ros_ws")
        for data in stream:
            print(data.decode("utf-8"), end='')
    except KeyboardInterrupt:
        print("Aborting build, stopping container...")
        running_container.stop()
        raise KeyboardInterrupt
    else:
        print("Build complete")

def main():
    parser = argparse.ArgumentParser(
        prog="develop.py",
        description="Launch spot ros dev contanier"
    )
    parser.add_argument("-b", "--build", help="Build the container", action="store_true")
    parser.add_argument("-r", "--run", help="Run the container after build", action="store_true")
    parser.add_argument("-i", "--image", help="Image label to use")
    args = parser.parse_args()
    client = docker.from_env()
    image = lookForDevContainer(client, image_label=args.image if args.image else None)
    container = startDevContainer(client, image)
    if (args.build):
        try:
            buildSourceFiles(container)
        except KeyboardInterrupt:
            container.stop()
            exit(1)

    if (not args.build or args.run):
        print("Starting shell")
        subprocess.run(["docker", "exec", "-it", "-w", "/opt/bev_fusion/CUDA-BEVFusion", container.id, "bash"])
        container.stop()

if __name__ == "__main__":
    main()
