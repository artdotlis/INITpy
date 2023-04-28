FROM docker.io/rockylinux:9

ENV HOME="/root"
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:$PATH"

COPY . /tmp/app

WORKDIR /tmp/app

RUN bash ./bin/deploy/prep.sh && bash ./bin/deploy/req.sh

WORKDIR /

RUN rm -rf /tmp/app
