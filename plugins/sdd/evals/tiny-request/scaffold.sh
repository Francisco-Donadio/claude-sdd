#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
printf '# Demo\n\nYou will recieve an email when your export is ready.\n' > README.md
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm "init"
