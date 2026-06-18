#!/usr/bin/env bash
# Prohibir archivos de GitHub Actions en .github/workflows/
if [[ -d ".github/workflows" ]] && ls .github/workflows/*.yml 1>/dev/null 2>&1; then
  echo "Error: GitHub Actions workflow files are prohibited (.github/workflows/*.yml)"
  exit 1
fi
exit 0
