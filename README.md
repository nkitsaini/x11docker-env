Requirements: Docker Buildkit, Weston, x11 environment


```sh
cd dev-base; ./build.sh; cd ..; python3 go.py lab
```

you might need to configure dotfiles from dotfiles repo:
```sh
git submodule update --init
```
Also update dotfiles to latest version timely
