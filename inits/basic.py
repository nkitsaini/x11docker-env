#!/bin/env python3

import os

os.chdir("/tmp/dotfiles")
os.execvp("python3", ["python3", "install.py", "/home/future_user"])
