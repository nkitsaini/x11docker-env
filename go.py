import os
import sys
import shutil
import shlex
from pathlib import Path
import subprocess

X11DOCKER_PATH = "./x11docker"

user = sys.argv[1]
IMAGE_NAME = f"x11dev-sd-{user}"
DEFAULT_DOCKERFILE_PATH = Path(f"basic-Dockerfile")
DOCKERFILE_PATH = Path(f"{user}-Dockerfile")

if not DOCKERFILE_PATH.is_file():
	DOCKERFILE_PATH = DEFAULT_DOCKERFILE_PATH

user_dir = Path("/home") / user
# TODO: change to home/user so docker works without symlink
x11docker_user_dir = Path("/x11docker") / user
CLIP_FILE = Path("/tmp/clip_sync")
DOCKER_GROUP_ID = subprocess.check_output(["bash", "-c", "getent group docker | cut -d: -f 3"]).decode().strip()


def build_dockerfile():
	assert os.system(
		f"docker build -t {IMAGE_NAME} --file {DOCKERFILE_PATH.name} --build-arg docker_group_id={DOCKER_GROUP_ID} --build-arg USER_NAME={user} . "
	) == 0


volumes = [
	f"{x11docker_user_dir}:{user_dir}", f"/var/log/s6-{user}:/var/log/s6", "/var/run/docker.sock:/var/run/docker.sock",
	"/lib/modules:/lib/modules", "/home/backup/lab:/old/lab:ro", "/home/backup/work:/old/work:ro", "/home/ankit:/host:ro",
	"/etc/wireguard:/etc/wireguard:ro", f"{CLIP_FILE}:{CLIP_FILE}", *sys.argv[2:]
]

cmd = [
	"x11docker",
	*shlex.split(
		f"--dbus --webcam --hostipc --gpu --init=none --sudouser --pulseaudio --desktop --user=RETAIN --xtest -f --workdir={user_dir} --cap-default --newprivileges=yes"
	),
	*shlex.split(
		f'-- --dns 1.1.1.1 --cap-add ALL --security-opt seccomp=unconfined --privileged --cap-add=NET_ADMIN --device /dev/fuse --cap-add=SYS_MODULE --sysctl="net.ipv6.conf.all.disable_ipv6=0"  -v {" -v ".join(volumes)} --shm-size=1g --'
	),
	IMAGE_NAME,
]

if __name__ == "__main__":
	build_dockerfile()
	if not x11docker_user_dir.exists():
		os.system(f"sudo mkdir -p {x11docker_user_dir}; sudo chmod -R 777 {x11docker_user_dir}")
	if not CLIP_FILE.exists():
		os.system(f"sudo touch {CLIP_FILE}; sudo chmod 778 {CLIP_FILE}")

	os.execv(X11DOCKER_PATH, cmd)