# Multi-stage build pour optimiser la taille de l'image
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances système pour la compilation
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libcairo2-dev \
       libpango1.0-dev \
       libgdk-pixbuf-2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python dans un répertoire dédié
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage final - image minimale
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Installation uniquement des bibliothèques runtime (pas les -dev)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libcairo2 \
       libpango-1.0-0 \
       libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copie des dépendances Python compilées depuis le builder
COPY --from=builder /root/.local /root/.local

# Copie du code applicatif
COPY app /app/app
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8234
CMD ["/run.sh"]
