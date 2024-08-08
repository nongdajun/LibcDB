#!/bin/bash
if [[ $# != 2 ]]; then
  echo >&2 "Usage: $0 libc_filename"
  exit 2
fi

. common/libc.sh

add_local $1 $2
