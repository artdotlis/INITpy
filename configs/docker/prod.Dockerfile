FROM docker.io/almalinux:10 AS appbuilder

ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG CONTAINER="container"

COPY . /app

WORKDIR /app

RUN dnf clean all && dnf install -y bash
RUN bash "./${BIN_DEPLOY_PREP}" && bash "./${BIN_DEPLOY_REQ}"
RUN make build && make run-build

RUN --mount=type=secret,id=env_file,target=/run/secrets/env_file \
    bash -c "\
        while IFS='=' read -r key value; do \
            if [[ ! \${key} =~ ^# && -n \${key} ]]; then \
                export \${key}=\${value}; \
            fi; \
        done < /run/secrets/env_file && make run-build \
    "

FROM docker.io/almalinux:10 AS main

ARG USERNAME=runner
ARG USER_UID=1001
ARG USER_GID=1001
ENV HOME_MAIN="/home/${USERNAME}"
ENV HOME="${HOME_MAIN}"
ENV PATH="${HOME_MAIN}/.local/bin:${PATH}"
ENV CONTAINER="container"

RUN dnf clean all && dnf install -y bash

ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG BIN_DEPLOY_USER

COPY ./${BIN_DEPLOY_PREP} /prep.sh
COPY ./${BIN_DEPLOY_REQ} /req.sh
COPY ./${BIN_DEPLOY_USER} /user.sh

COPY --from=appbuilder /app/dist /build

WORKDIR /build
RUN bash /prep.sh && rm /prep.sh
RUN bash /req.sh && rm /req.sh
RUN bash /user.sh && rm /user.sh

# stage wheels into the user's home, then drop to the user exactly once
RUN mkdir -p "${HOME_MAIN}/wheels" && \
    cp /build/*.whl "${HOME_MAIN}/wheels/" && \
    chown -R "${USERNAME}:${USERNAME}" "${HOME_MAIN}" && \
    rm -rf /build

USER ${USERNAME}

RUN pip install --no-cache-dir "${HOME_MAIN}"/wheels/*.whl && rm -rf "${HOME_MAIN}/wheels"

WORKDIR ${HOME_MAIN}

ENTRYPOINT ["sleep", "infinity"]
