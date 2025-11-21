#!/bin/sh
set -e

# Auto-install integration into Home Assistant
INTEGRATION_SOURCE="/app/integration"
INTEGRATION_TARGET="/config/custom_components/wled_icons"

if [ -d "$INTEGRATION_SOURCE" ]; then
    echo "[SETUP] Checking integration installation..."
    
    # Check if integration needs update (compare versions or always update)
    if [ ! -d "$INTEGRATION_TARGET" ]; then
        echo "[SETUP] Installing WLED Icons integration..."
        mkdir -p /config/custom_components
        cp -r "$INTEGRATION_SOURCE" "$INTEGRATION_TARGET"
        echo "[SETUP] ✅ Integration installed successfully"
    else
        echo "[SETUP] Updating WLED Icons integration..."
        rm -rf "$INTEGRATION_TARGET"
        cp -r "$INTEGRATION_SOURCE" "$INTEGRATION_TARGET"
        echo "[SETUP] ✅ Integration updated successfully"
    fi
else
    echo "[SETUP] ⚠️  Integration source not found, skipping auto-install"
fi

echo "[STARTUP] Starting WLED Icons service..."
export PYTHONPATH=/app
exec uvicorn app.main:app --host 0.0.0.0 --port 8234
