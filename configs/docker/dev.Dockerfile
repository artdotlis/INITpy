FROM docker.io/almalinux:10

ARG USERNAME=devu
# USER_UID and USER_GID will be mapped by devcontainer
ARG USER_UID=1000
ARG USER_GID=1000
ARG WORK_DIR=/workspace
ENV HOME_MAIN="/home/${USERNAME}"
ENV PATH="${HOME_MAIN}/.local/bin:${PATH}"
ENV CONTAINER="container"
ENV HISTFILE=/dev/null
ENV HISTSIZE=0
ENV HISTFILESIZE=0

ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG BIN_DEPLOY_USER

COPY . /app

WORKDIR /app

RUN dnf clean all && dnf install -y bash
RUN bash "./${BIN_DEPLOY_PREP}" && bash "./${BIN_DEPLOY_REQ}" && bash "./${BIN_DEPLOY_USER}"

WORKDIR /

RUN rm -rf /app

RUN mkdir -p ${WORK_DIR} && \
    chown ${USERNAME}:${USERNAME} -R ${WORK_DIR}

RUN git config --global --add safe.directory ${WORK_DIR}
RUN dnf install -y openssh openssh-clients

USER ${USERNAME}

ENTRYPOINT ["sleep", "infinity"]
