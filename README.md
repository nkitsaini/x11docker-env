This is a complete environment based on [X11Docker](https://github.com/mviereck/x11docker). This allows to spin a docker and get a new Desktop Environment (with completely different OS/software etc.) running inside docker. 

Requirements: Docker Buildkit, Weston, x11 environment


```sh
# start the environment
cd dev-base; ./build.sh; cd ..; python3 go.py lab
```

you might need to configure dotfiles from dotfiles repo:
```sh
git submodule update --init
```
Also update dotfiles to latest version timely
