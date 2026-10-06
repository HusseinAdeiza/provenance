#!/usr/bin/env bash
# build_image.sh — assemble a minimal Docker context and build the demo image.
# Runtime-only: no damlc (the 823MB compiler). The DAR ships prebuilt, so the
# container only needs sandbox + script + json-api + UI.
set -euo pipefail
cd "$(dirname "$0")/.."        # /root/provenance
SDK="$HOME/.daml/sdk/2.10.6"
CTX=/tmp/prov-docker-ctx
IMAGE=provenance-demo:latest

echo "── stage context ──"
rm -rf "$CTX"; mkdir -p "$CTX/sdk" "$CTX/damlbin" "$CTX/app"

# runtime SDK pieces only (skip damlc/daml2js/studio — huge, unused at runtime)
for part in canton daml daml-sdk daml-helper daml-libs; do
  [ -d "$SDK/$part" ] && cp -a "$SDK/$part" "$CTX/sdk/" && echo "  + sdk/$part"
done
cp -a "$SDK/daml_version.txt" "$CTX/sdk/" 2>/dev/null || true
cp -a "$SDK/sdk-config.yaml" "$CTX/sdk/" 2>/dev/null || true
# the daml launcher + its lib
cp -a "$HOME/.daml/bin/." "$CTX/damlbin/" && echo "  + damlbin/"

# the app: source + prebuilt DAR + docker dir
mkdir -p "$CTX/app/.daml/dist"
cp -a .daml/dist/*.dar "$CTX/app/.daml/dist/"
cp -a daml-src ui demo docker ai.py mcp_server.py eval_mcp.py "$CTX/app/" 2>/dev/null || true
cp docker/Dockerfile "$CTX/Dockerfile"
echo "  + app/ (DAR + ui + demo + docker)"

echo "── context size ──"
du -sh "$CTX" | sed 's/^/  /'

echo "── build ──"
cd "$CTX"
docker build -t "$IMAGE" . 2>&1 | tail -15
echo "── image ──"
docker images "$IMAGE" | tail -1
