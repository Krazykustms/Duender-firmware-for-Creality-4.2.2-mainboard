#!/bin/bash
export DISPLAY=:0
echo "=== xrandr ==="
sudo -u biqu env DISPLAY=:0 xrandr --query 2>&1 | head -50
echo "=== processes ==="
ps aux | grep -E 'Xorg|KlipperScreen|screen.py' | grep -v grep
echo "=== KS journal ==="
journalctl -u KlipperScreen -n 30 --no-pager
echo "=== Xorg log tail ==="
tail -40 /home/biqu/.local/share/xorg/Xorg.0.log 2>/dev/null || tail -40 /var/log/Xorg.0.log 2>/dev/null || true
