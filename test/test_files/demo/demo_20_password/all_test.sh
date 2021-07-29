#!/usr/bin/env bash

set -eu -o pipefail

PRG="password_pgr.py"
for FILE in password*.py; do
    echo "==> ${FILE} <==" 
    cp "$FILE" "$PRG"
    make test
done

echo "Done."
