import os
import sys
import shutil
import shlex
from pathlib import Path
import subprocess

X11DOCKER_PATH = "./x11docker"

PWD = Path('.').absolute()
user = sys.argv[1]
IMAGE_NAME = f"localhost/x11dev-arch-{user}"
DEFAULT_DOCKERFILE_PATH = Path(f"basic-Dockerfile")
DOCKERFILE_PATH = Path(f"{user}-Dockerfile")

if not DOCKERFILE_PATH.is_file():
	DOCKERFILE_PATH = DEFAULT_DOCKERFILE_PATH

user_dir = Path("/home") / user
# TODO: change to home/user so docker works without symlink
x11docker_user_dir = Path("/x11docker") / user
CLIP_FILE = Path("/tmp/clip_sync")
DOCKER_GROUP_ID = subprocess.check_output(["bash", "-c", "getent group docker | cut -d: -f 3"]).decode().strip()
PODMAN_CONTAINER_DIR = Path(f"/var/lib/container-{user}")
PODMAN_CONTAINER_DIR.mkdir(exist_ok=True)
assert subprocess.check_output(["bash", "-c", "id -u"]).decode().strip() == '0', "Run as root, otherwise podman will eat you alive"



def build_dockerfile():
	assert os.system(
		f"podman build -t {IMAGE_NAME} --file {DOCKERFILE_PATH.name} --build-arg docker_group_id={DOCKER_GROUP_ID} --build-arg USER_NAME={user} . "
	) == 0


volumes = [
	f"{x11docker_user_dir}:{user_dir}", "/var/run/docker.sock:/var/run/docker.sock",
	"/lib/modules:/lib/modules", "/home/ankit:/host:ro",
        f"{PWD/'startups'}:/tmp/startups",
        f"{PODMAN_CONTAINER_DIR}:/var/lib/containers",
         f"{CLIP_FILE}:{CLIP_FILE}", *sys.argv[2:]
]

PODMAN_OPTIONS = shlex.split(f'--security-opt seccomp=unconfined  --privileged  --device /dev/fuse  --device /dev/dri --sysctl="net.ipv6.conf.all.disable_ipv6=0"  -v {" -v ".join(volumes)} --shm-size=1g')
cmd = [
	"x11docker",
	*shlex.split(
		f"--backend=podman --dbus --webcam --gpu --clipboard --network --xc=no  --init=none --sudouser --pulseaudio --desktop --user=RETAIN --xtest --workdir={user_dir} --cap-default --newprivileges=yes"
	),
        '--',
        *PODMAN_OPTIONS,
        '--',
	IMAGE_NAME,
]

if __name__ == "__main__":
	build_dockerfile()
	if not x11docker_user_dir.exists():
		os.system(f"sudo mkdir -p {x11docker_user_dir}; sudo chmod -R 777 {x11docker_user_dir}")
	if not CLIP_FILE.exists():
		os.system(f"sudo touch {CLIP_FILE}; sudo chmod 777 {CLIP_FILE}")

	os.execv(X11DOCKER_PATH, cmd)
