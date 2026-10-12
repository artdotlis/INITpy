FROM docker.io/almalinux:10

ARG UV
ARG PNPM
ARG USERNAME=devu
# USER_UID and USER_GID will be mapped by devcontainer
ARG USER_UID=1000
ARG USER_GID=1000
ARG WORK_DIR=/workspace
ENV HOME_MAIN="/home/${USERNAME}"
ENV PATH="${HOME_MAIN}/.local/bin:${WORK_DIR}/${UV}:${WORK_DIR}/${PNPM}:${PATH}"
ENV CONTAINER="container"
ENV HISTFILE=/dev/null
ENV HISTSIZE=0
ENV HISTFILESIZE=0

ARG NODE_VERSION
ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG BIN_DEPLOY_USER
ARG BIN_DEPLOY_ENTRY_DEV

COPY . /tmp/app

WORKDIR /tmp/app

COPY ./${BIN_DEPLOY_ENTRY_DEV} /entry_dev.sh

RUN dnf clean all && dnf install -y bash
RUN bash "./${BIN_DEPLOY_PREP}" && bash "./${BIN_DEPLOY_REQ}" && bash "./${BIN_DEPLOY_USER}"

WORKDIR /

RUN rm -rf /tmp/app

RUN mkdir -p ${WORK_DIR} && \
    chown ${USERNAME}:${USERNAME} -R ${WORK_DIR} 

RUN git config --global --add safe.directory ${WORK_DIR}
RUN dnf install -y openssh openssh-clients

HEALTHCHECK --interval=60s --timeout=6s --retries=1 CMD exit 0

USER ${USERNAME}

ENTRYPOINT ["/bin/bash", "/entry_dev.sh"]
