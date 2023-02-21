#!/bin/bash

gunicorn \
    --bind=0.0.0.0:9000 \
    --worker-class=uvicorn.workers.UvicornWorker \
    --workers=1 \
    --timeout=300 \
    --keep-alive=7200 \
    --forwarded-allow-ips='*' \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info \
    wsdemo:application
