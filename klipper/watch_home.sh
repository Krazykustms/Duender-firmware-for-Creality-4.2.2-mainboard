#!/bin/bash
for i in $(seq 1 20); do
  curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead&webhooks' > /tmp/ks.json
  python3 - <<'PY'
import json
d=json.load(open('/tmp/ks.json'))['result']['status']
print('homed=%r state=%s msg=%s' % (
  d['toolhead'].get('homed_axes'),
  d['webhooks'].get('state'),
  (d['webhooks'].get('state_message') or '')[:100].replace('\n',' ')))
PY
  sleep 3
done
echo '--- last errors ---'
grep -aE 'BLTouch failed|No trigger|CommandError:|Must home' ~/printer_data/logs/klippy.log | tail -15
