# Provenance — single-container live demo.
# Runtime-only Daml SDK (no damlc compiler — the DAR is prebuilt), Java 17,
# Python 3. Boot sequence: sandbox -> bootstrap parties+hold -> json-api -> UI.
# The ledger is in-memory: every boot recreates the demo state (documented).
FROM eclipse-temurin:17-jre-jammy

RUN apt-get update && apt-get install -y --no-install-recommends python3 curl \
    && rm -rf /var/lib/apt/lists/*

# Prebuilt DAR + runtime SDK pieces (canton, daml launcher, daml-sdk, helper, libs)
COPY sdk/ /root/.daml/sdk/2.10.6/
COPY damlbin/ /root/.daml/bin/
RUN chmod +x /root/.daml/bin/* || true
ENV PATH="/root/.daml/bin:${PATH}"

WORKDIR /app
COPY app/ /app/
RUN chmod +x /app/docker/boot.sh

EXPOSE 8090
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
  CMD curl -sf http://127.0.0.1:${PORT:-8090}/api/state -o /dev/null || exit 1

CMD ["/app/docker/boot.sh"]
