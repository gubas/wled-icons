# Multi-stage build pour optimiser la taille de l'image
FROM python:3.11-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances de build (gcc pour compiler Pillow)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libjpeg

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage final - image minimale Alpine
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Installation uniquement des bibliothèques runtime nécessaires
RUN apk add --no-cache \
    libjpeg \
    libstdc++

WORKDIR /app

# Copie des dépendances Python compilées depuis le builder
COPY --from=builder /root/.local /root/.local

# Copie du code applicatif
COPY app /app/app
COPY integration /app/integration
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8234
CMD ["/run.sh"]
