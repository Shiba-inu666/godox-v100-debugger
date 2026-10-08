#!/bin/zsh
cd -- "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  echo '请先按 README.md 安装调试依赖。'
  read
  exit 1
fi
if .venv/bin/python -c 'import urllib.request,json; s=json.load(urllib.request.urlopen("http://127.0.0.1:8765/api/state",timeout=1)); assert s["sha256"]=="fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787"' 2>/dev/null; then
  open http://127.0.0.1:8765
  exit 0
fi
.venv/bin/python debug/server.py --open
