FROM docker.io/rockylinux:9 AS appbuilder

ENV HOME="/root"
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:${PATH}"

COPY . /tmp/app

WORKDIR /tmp/app

RUN mkdir -p "${HOME}/.local/bin" && bash ./bin/deploy.sh

FROM docker.io/rockylinux:9 AS main

ARG USERNAME=devu
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG WORK_DIR=/workspace
ENV HOME="/home/${USERNAME}"

COPY . /tmp/app
WORKDIR /tmp/app

COPY --from=appbuilder /tmp/build /tmp/build
COPY --from=appbuilder /health.sh /health.sh
COPY --from=appbuilder /entrypoint.sh /entrypoint.sh

RUN bash ./bin/deploy/init_py.sh

WORKDIR /

RUN rm -rf /tmp/app

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -m -d $HOME \
    --uid $USER_UID --gid $USER_GID $USERNAME
RUN mkdir -p $WORK_DIR && \
    chown $USERNAME:$USERNAME -R $WORK_DIR && \
    mkdir -p "${HOME}/.local/bin" && \
    chown $USERNAME:$USERNAME -R $HOME


ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]

HEALTHCHECK --interval=5m --timeout=3s CMD /health.sh
