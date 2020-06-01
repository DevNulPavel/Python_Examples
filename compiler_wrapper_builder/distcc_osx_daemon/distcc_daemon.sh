#! /usr/bin/env bash

# launchctl setenv PATH $PATH
# --log-file=/var/log/distcc_logs

/usr/local/bin/distccd \
    --jobs 64 \
    --allow 0.0.0.0/32 \
    --allow 127.0.0.1 \
    --no-detach \
    --daemon \
    --log-stderr \
    --verbose \
    --enable-tcp-insecure