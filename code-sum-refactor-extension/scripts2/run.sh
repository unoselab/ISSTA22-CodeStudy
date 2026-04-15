#!/usr/bin/env bash

# Compile main_summarizer.ts to main_summarizer.js
# Then run main_summarizer.js
#
# Install:
#   npm install -g typescript

set -e

INPUT_FILE="${1:-}"

tsc --ignoreConfig --target ES2020 --module commonjs main_summarizer.ts

if [ -n "$INPUT_FILE" ]; then
  node main_summarizer.js python ./summarizer.py "$INPUT_FILE"
else
  node main_summarizer.js python ./summarizer.py
fi