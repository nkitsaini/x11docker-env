# syntax = docker/dockerfile:1.3
FROM ubuntu:21.10

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,id=21.04,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt sh -c "echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections" && \
	echo "resolvconf resolvconf/linkify-resolvconf boolean false" | debconf-set-selections && \
	apt-get update && yes | unminimize

RUN mkdir -p /tmp/heavy/
WORKDIR /tmp/

COPY ./heavy/apt.sh /tmp/heavy/
RUN  --mount=type=cache,id=21.10,sharing=locked,target=/var/cache/apt --mount=type=cache,sharing=locked,target=/var/lib/apt bash /tmp/heavy/apt.sh

COPY ./heavy/apt-3rd.sh /tmp/heavy/
RUN mkdir -p /tmp/apt3-cache
RUN --mount=type=cache,id=21.10,sharing=locked,target=/var/cache/apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt --mount=type=cache,id=v1,sharing=locked,target=/tmp/apt3-cache \
	sudo bash /tmp/heavy/apt-3rd.sh

COPY ./heavy/requirements.txt /tmp/heavy
RUN --mount=type=cache,target=/root/.cache,rw sudo pip3 install -r /tmp/heavy/requirements.txt


RUN useradd -ms /bin/bash future_user && echo "future_user:future_user" | chpasswd && adduser future_user sudo

USER future_user
RUN wget --https-only --secure-protocol=TLSv1_2 -O- https://sh.rustup.rs | sh /dev/stdin -y

COPY ./heavy/cargo_installs.sh /tmp/heavy
RUN bash /tmp/heavy/cargo_installs.sh
