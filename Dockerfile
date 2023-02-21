FROM --platform=linux/amd64 python:3.9.11 as build
ENV PIP_INDEX_URL="https://mirrors.cloud.tencent.com/pypi/simple/" PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN python -m venv .venv && \
    .venv/bin/pip install 'wheel==0.38.4' && \
    .venv/bin/pip install --no-deps -r /tmp/requirements.txt

FROM --platform=linux/amd64 python:3.9.11-slim as runtime
ENV PIP_INDEX_URL="https://mirrors.cloud.tencent.com/pypi/simple/" PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
ENV PATH=/app/.venv/bin:$PATH
COPY --from=build /app/.venv /app/.venv
COPY . /app
ARG EZFAAS_BUILD_ID=''
ARG EZFAAS_COMMIT_ID=''
ENV EZFAAS_BUILD_ID=${EZFAAS_BUILD_ID} EZFAAS_COMMIT_ID=${EZFAAS_COMMIT_ID}

FROM --platform=linux/amd64 runtime
CMD [ "/app/runserver.sh" ]
