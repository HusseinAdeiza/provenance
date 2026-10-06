# Provenance demo — one container running the whole stack.
#
# Boots: canton sandbox → bootstrap (parties + first hold) → json-api → roles UI.
# The UI is the served surface on $PORT; everything else is internal.
#
# The Daml SDK is installed in the image (not at runtime) so the build is
# reproducible and the boot has no network dependency. SDK 2.10.6 is the
# version the contracts and the demo harness are verified against.

FROM eclipse-temurin:17-jre-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    DAML_VERSION=2.10.6 \
    PATH="/opt/daml/bin:${PATH}" \
    PYTHONUNBUFFERED=1

# JRE + python3 + curl (the entrypoint health-checks via curl) + unzip for the SDK
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 ca-certificates curl unzip git \
 && rm -rf /var/lib/apt/lists/*

# Daml SDK — pinned to 2.10.6, the version the contracts and demo harness are
# verified against. NOTE: get.daml.com takes the version POSITIONALLY
# (usage: get-daml.sh VERSION) — there is no --version flag. Verified against
# the installer's own usage header, not assumed.
RUN curl -fsSL https://get.daml.com/ -o /tmp/get-daml.sh \
 && chmod +x /tmp/get-daml.sh && /tmp/get-daml.sh ${DAML_VERSION} \
 && rm -f /tmp/get-daml.sh

WORKDIR /app

# Build the Daml package in the image so the container does not compile on boot.
# Dependencies resolve first for layer caching.
COPY daml.yaml ./
COPY daml-src/ ./daml-src/
RUN daml build

# Runtime code: UI server, AI layer, MCP server, demo harness (used by /api/ask
# and by judges running the checks themselves).
COPY ui/ ./ui/
COPY ai.py eval_mcp.py ./
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 8090
ENV PORT=8090

HEALTHCHECK --interval=30s --timeout=10s --start-period=150s --retries=3 \
  CMD curl -fsS --max-time 5 "http://127.0.0.1:${PORT}/api/state" \
      | grep -q '"strangerVisibleHolds": *0' || exit 1

ENTRYPOINT ["./entrypoint.sh"]