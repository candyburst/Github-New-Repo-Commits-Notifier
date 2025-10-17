# ============================================================
# Base Image
# ============================================================
FROM ubuntu:22.04

# ============================================================
# Environment Variables
# ============================================================
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JUPYTER_DIR=/workspace \
    TZ=UTC

# ============================================================
# 1) Install OS dependencies + Dev tools + Node.js
# ============================================================
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        git curl wget ca-certificates \
        nano vim unzip zip \
        build-essential gcc g++ make \
        openssh-client sudo tini tzdata locales \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ============================================================
# 2) Locale setup (optional)
# ============================================================
RUN sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen

# ============================================================
# 3) Install JupyterLab + Jupyter Server
# ============================================================
RUN pip3 install --no-cache-dir \
    "jupyterlab==4.*" \
    "jupyter-server==2.*"

# ============================================================
# 4) Create non-root user "app" with sudo privileges
# ============================================================
RUN useradd -m -u 1000 -s /bin/bash app && \
    mkdir -p "${JUPYTER_DIR}" && \
    chown -R app:app "${JUPYTER_DIR}" && \
    usermod -aG sudo app && \
    echo "app ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/010-app-nopasswd && \
    chmod 440 /etc/sudoers.d/010-app-nopasswd

# ============================================================
# 5) Clone repository (optional: replace URL if private)
# ============================================================
USER app
WORKDIR ${JUPYTER_DIR}
RUN git clone --depth=1 https://github.com/nadjibunss/test.git "${JUPYTER_DIR}/test" || true

# ============================================================
# 6) Expose port for JupyterLab
# ============================================================
EXPOSE 8080

# ============================================================
# 7) Use tini as init
# ============================================================
USER root
ENTRYPOINT ["/usr/bin/tini", "--"]

# ============================================================
# 8) Run JupyterLab
# ============================================================
USER app
CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8080", \
     "--no-browser", \
     "--ServerApp.root_dir=/workspace", \
     "--ServerApp.token=", \
     "--ServerApp.password=", \
     "--ServerApp.port_retries=0"]
