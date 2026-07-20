#!/usr/bin/env python3
import json, time, urllib.parse, urllib.request

def get(path):
    return json.load(urllib.request.urlopen("http://127.0.0.1:7125" + path, timeout=15))

def gcode(script):
    q = urllib.parse.urlencode({"script": script})
    urllib.request.urlopen("http://127.0.0.1:7125/printer/gcode/script?" + q, timeout=30)

print("state", get("/printer/objects/query?webhooks")["result"]["status"]["webhooks"])
gcode("SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET=0")
gcode("SET_HEATER_TEMPERATURE HEATER=extruder TARGET=50")
for i in range(8):
    time.sleep(4)
    d = get("/printer/objects/query?extruder&heater_bed")["result"]["status"]
    e, b = d["extruder"], d["heater_bed"]
    print(
        "i=%d E temp=%.1f tgt=%.0f pwr=%.2f  Bed temp=%.1f tgt=%.0f pwr=%.2f"
        % (i, e["temperature"], e["target"], e["power"], b["temperature"], b["target"], b["power"])
    )
gcode("SET_HEATER_TEMPERATURE HEATER=extruder TARGET=0")
print("extruder target cleared")
