#!/bin/bash

set -e

RULE_PATH="/etc/udev/rules.d/99-esp32.rules"
PORT=$(ls /dev/ttyACM* 2>/dev/null | head -n1)

if [ -z "$PORT" ]; then
  echo "❌ No ESP32 device found on /dev/ttyACM*"
  exit 1
fi

echo "🔍 Scanning device at $PORT..."

VENDOR_ID=$(udevadm info -a -n "$PORT" | grep -m1 '{idVendor}' | awk -F'==' '{print $2}' | tr -d '" ')
PRODUCT_ID=$(udevadm info -a -n "$PORT" | grep -m1 '{idProduct}' | awk -F'==' '{print $2}' | tr -d '" ')

if [ -z "$VENDOR_ID" ] || [ -z "$PRODUCT_ID" ]; then
  echo "❌ Could not retrieve idVendor or idProduct."
  exit 1
fi

echo "📦 Detected Vendor ID: $VENDOR_ID"
echo "📦 Detected Product ID: $PRODUCT_ID"

if [ -f "$RULE_PATH" ]; then
  echo "⚠️  A rule already exists at $RULE_PATH."
  read -p "Do you want to overwrite it? [y/N]: " confirm
  if [[ ! "$confirm" =~ ^[yY]$ ]]; then
    echo "❌ Installation cancelled."
    exit 1
  fi
fi

echo "📝 Writing udev rule..."

sudo bash -c "cat > $RULE_PATH" <<EOF
SUBSYSTEM=="tty", ATTRS{idVendor}=="$VENDOR_ID", ATTRS{idProduct}=="$PRODUCT_ID", SYMLINK+="esp32", MODE="0666"
EOF

echo "🔄 Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "✅ Rule successfully installed."
echo "🔌 Unplug and reconnect your ESP32-S3."
echo "📎 You should now see it as: /dev/esp32"
