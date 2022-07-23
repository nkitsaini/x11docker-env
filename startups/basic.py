#!/bin/env python3
import os
import shlex
import os
import enum
import os
from typing import List, NoReturn, Optional
from dataclasses import dataclass, field
import shutil
import datetime as dt
import abc
import random
from string import ascii_lowercase
from pathlib import Path
import sys

user = sys.argv[1]

class ProcessType(enum.Enum):
	service = enum.auto()
	init = enum.auto()
	manual = enum.auto()

	def get_start_secs(self) -> int:
		if self == ProcessType.service:
			# ProcessType.init isn't used so lets start services at 0?
			return 1
		elif self == ProcessType.init:
			return 0
		elif self == ProcessType.manual:
			return 60*60*24*365
		else:
			raise



class BaseService(abc.ABC):
	@abc.abstractmethod
	def render(self) -> str:
		raise NotImplementedError

def rand_str(length: int = 6) -> str:
	return "".join(random.choices(ascii_lowercase, k=length))

@dataclass
class Service(BaseService):
	name: str
	command: str
	type: ProcessType = ProcessType.service
	user: str = user #TODO
	dir: str = ""
	exit_codes: List[int] = field(default_factory=list)

	def render(self) -> str:
		if self.user == "root":
			user_home = "/root"
		else:
			user_home = f"/home/{self.user}"

		if self.dir != "":
			dir_arg = f"directory={self.dir}"
		else:
			dir_arg = ""

		if self.exit_codes != []:
			exitcode_args = f"exitcodes={str(self.exit_codes)[1:-1]}"
		else:
			exitcode_args = ""

		return f"""
[program:{self.name}]
command={self.command}
#redirect_stderr=true
user={self.user}
environment=HOME={user_home},USER={self.user}
startsecs={self.type.get_start_secs()}

stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

{dir_arg}
{exitcode_args}

"""

CONF_BOILERPLATE = """
[unix_http_server]
file=/tmp/supervisor.sock   ; the path to the socket file

[supervisord]
logfile=/tmp/supervisord.log ; main log file; default $CWD/supervisord.log
logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB
logfile_backups=10           ; # of main logfile backups; 0 means none, default 10
loglevel=info                ; log level; default info; others: debug,warn,trace
pidfile=/tmp/supervisord.pid ; supervisord pidfile; default supervisord.pid
nodaemon=true                ; start in foreground if true; default false
silent=false                 ; no logs to stdout if true; default false
minfds=1024                  ; min. avail startup file descriptors; default 1024
minprocs=200                 ; min. avail process descriptors;default 200
user=root

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket

[inet_http_server]
port = 127.0.0.1:9001
"""

@dataclass
class Supervisord:
	entries: List[BaseService]
	def run(self) -> NoReturn:
		"""
		run never returns
		"""
		supervisord_config = CONF_BOILERPLATE
		for ent in self.entries:
			supervisord_config += ent.render()

		time_str = dt.datetime.now().isoformat(sep="_").replace(":", ".")
		file_path = "/tmp/supervisord_" + time_str + rand_str() + ".conf"

		open(file_path, "w").write(supervisord_config)
		supervisord_bin = shutil.which("supervisord")
		if supervisord_bin is None:
			print("supervisord is not installed")
			exit(1)
		os.execv(supervisord_bin, ["supervisord", "-n", "-c", file_path, "-u", "root"])


COPY_HOME = """
# COPY_HOME ----------------
SECONDS=0

#user=$(cut -d: -f1,3 /etc/passwd | egrep ':[0-9]{4}$' | cut -d: -f1)
export XDG_RUNTIME_DIR=/run/user/$(id -u)
user=$(id -un)
home="/home/$user"
mkdir -p $home
shopt -s extglob
shopt -s dotglob

echo starting 2>&1
if [ "$(ls -A $home)" ]; then
	echo home already has stuff 2>&1
	ls -la $home 2>&1
else
	echo home is empty 2>&1
	mv /home/future_user/* $home/
	echo "moved" 2>&1
	chown -R $user $home
	echo "owned" 2>&1
fi

echo "Total time to execute $SECONDS"

# Gnome keyring ----------------
cd $home


export NO_AT_BRIDGE=1; # Don't use dbus accessibility bridge
eval $(dbus-launch --sh-syntax);
eval $(echo -n "think" | /usr/bin/gnome-keyring-daemon --login);
eval $(/usr/bin/gnome-keyring-daemon --replace);

eval $(ssh-agent -s)
ssh-add

exec /usr/bin/i3
"""
HOME_COPY_AND_I3_STARTUP_SCRIPT = COPY_HOME + "exec /usr/bin/i3\n"

DATA_DIR = Path("/tmp/x11-data")

# Should run as root 
os.system("mkdir -p /run/user/1000")
os.system("chown -R 1000:1000 /run/user/1000")
os.system("chown -R 1000:1000 /run/user/1000")

if __name__ == "__main__":
	script_path = Path("/tmp/x11d-scripts")
	script_path.mkdir()
	home_and_i3_script = (script_path/'i3.sh')
	home_and_i3_script.write_text(HOME_COPY_AND_I3_STARTUP_SCRIPT)
	os.system(f"su {user} -c 'bash {home_and_i3_script}'")
