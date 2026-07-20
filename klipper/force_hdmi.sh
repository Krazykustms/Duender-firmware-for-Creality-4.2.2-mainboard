#!/bin/bash
set -e
echo "=== drm ==="
ls /sys/class/drm/
for d in /sys/class/drm/card*-HDMI*; do
  echo "DEVICE=$d"
  echo connected | sudo tee "$d/status" >/dev/null || true
  echo "status=$(cat $d/status 2>/dev/null)"
  echo "enabled=$(cat $d/enabled 2>/dev/null)"
  echo "modes:"
  cat "$d/modes" 2>/dev/null | head -20 || true
done
echo "=== restart KS ==="
sudo systemctl restart KlipperScreen
sleep 5
sudo -u biqu env DISPLAY=:0 xrandr --query | head -30
# try force mode if still disconnected
if sudo -u biqu env DISPLAY=:0 xrandr --query | grep -q 'HDMI-1 disconnected'; then
  echo "=== forcing HDMI-1 with xrandr ==="
  sudo -u biqu env DISPLAY=:0 bash -c '
    xrandr --newmode "1024x600_60.00" 49.00 1024 1072 1176 1328 600 603 613 624 -hsync +vsync 2>/dev/null || true
    xrandr --addmode HDMI-1 1024x600_60.00 2>/dev/null || true
    xrandr --addmode HDMI-1 1024x600 2>/dev/null || true
    xrandr --output HDMI-1 --mode 1024x600 2>&1 || xrandr --output HDMI-1 --mode 1024x600_60.00 2>&1 || true
    xrandr --query | head -30
  '
fi
