# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

FROM docker.io/almalinux:10 AS appbuilder

ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG CONTAINER="container"
ARG NODE_VERSION

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
ARG HOME_MAIN="/home/runner"
ARG BIN_DEPLOY_ENTRY_PROD
ARG BIN_DEPLOY_HEALTH
ARG NODE_VERSION

RUN dnf clean all && dnf install -y bash

ARG BIN_DEPLOY_PREP
ARG BIN_DEPLOY_REQ
ARG BIN_DEPLOY_USER

COPY ./${BIN_DEPLOY_PREP} /prep.sh
COPY ./${BIN_DEPLOY_REQ} /req.sh
COPY ./${BIN_DEPLOY_USER} /user.sh

COPY --from=appbuilder /app/dist /build
COPY ./${BIN_DEPLOY_ENTRY_PROD} /entry.sh
COPY ./${BIN_DEPLOY_HEALTH} /health.sh

WORKDIR /build
RUN bash /prep.sh && rm /prep.sh
RUN bash /req.sh && rm /req.sh
RUN bash /user.sh && rm /user.sh

HEALTHCHECK --interval=5m --timeout=3s CMD /health.sh

RUN chown ${USERNAME}:${USERNAME} -R /build

USER ${USERNAME}

RUN pip install --no-cache-dir shared_utils*.whl
RUN pip install --no-cache-dir scaffolder*.whl

WORKDIR ${HOME_MAIN}

RUN rm -rf  /build

ENV PATH="${HOME_MAIN}/.local/bin:${PATH}"

ENTRYPOINT ["/bin/sh", "/entry.sh"]
