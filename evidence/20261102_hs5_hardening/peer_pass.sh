#!/bin/bash
# Peer-style clean-environment pass: follow README §2-§4 and §6 literally, log everything.
# Arg 1: python launcher to use for "python3 -m venv" (README step), Arg 2: label
PYLAUNCH="$1"; LABEL="$2"
WORK=$HOME/pass_$LABEL; rm -rf "$WORK"; mkdir -p "$WORK"; cd "$WORK"
step() { echo; echo "### $(date -u +%H:%M:%S) \$ $*"; bash -o pipefail -c "$*" 2>&1; echo "### exit=$?"; }
echo "# Clean-environment pass '$LABEL' as user $(whoami) on $(uname -sr), start $(date -u +%FT%TZ)"
echo "# fresh HOME dir, no prior venv, no cached package; README followed literally (clone URL replaced by local mirror of the pushed repo)"
step "git clone /srv/metasense-remote.git Metasense" ; [ -d Metasense ] || { echo "ABORT: clone failed"; exit 1; }
cd Metasense || exit 1
echo "# which metasense before install: $(command -v metasense || echo none)"
step "git describe --tags"
step "$PYLAUNCH -m venv .venv"
source .venv/bin/activate
step "python --version"
step "pip install -e . -r requirements-dev.txt -q"
step "metasense doctor"
step "metasense analyze data/sample/paper_complete.txt | grep -E 'MetaSense|Completeness'"
step "metasense analyze data/sample/paper_weak.txt | grep -E 'Completeness|Weaknesses'"
step "metasense analyze data/sample/paper_no_method_heading.txt | grep -E 'Completeness|methodology-related'"
step "metasense analyze data/sample/empty.txt"
step "metasense analyze data/sample/paper_weak.txt --out reports/ && ls reports/"
step "metasense version"
step "python -m pytest -q | tail -2"
step "python scripts/check_packaging.py | tail -2"
step "python scripts/run_validation.py --label peer_$LABEL | tail -13"
echo "# end $(date -u +%FT%TZ)"
