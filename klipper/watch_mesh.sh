#!/bin/bash
python3 <<'PY'
import json, time, urllib.request, subprocess
url = "http://127.0.0.1:7125/printer/objects/query?print_stats&bed_mesh&webhooks&toolhead"
for i in range(48):
    d = json.load(urllib.request.urlopen(url, timeout=10))["result"]["status"]
    bm = d.get("bed_mesh") or {}
    msg = (d["webhooks"].get("state_message") or "").replace("\n", " ")[:100]
    print(
        "i=%d state=%s profile=%s has_mesh=%s homed=%r msg=%s"
        % (
            i,
            d["webhooks"]["state"],
            bm.get("profile_name"),
            bm.get("probed_matrix") is not None,
            d["toolhead"].get("homed_axes"),
            msg,
        )
    )
    time.sleep(5)
print("--- log ---")
print(
    subprocess.check_output(
        "grep -aE 'BED_MESH|bed_mesh|BLTouch failed|No trigger|CommandError|SAVE_CONFIG|z_offset|Mesh' ~/printer_data/logs/klippy.log | tail -30",
        shell=True,
        text=True,
    )
)
PY
