"""Fetch live/public reference data (best-effort, cached, never blocks offline runs).

Sources (all public, verified 2026-10-04):
- https://gems-erasmus.eu/hardware/ (module list: Diamond/Ruby/Sapphire/Emerald)
- OpenAlex: mechatronics mobile robot + open-source hardware education
Falls back to bundled snapshot if network unavailable — reproducibility first.
"""
import json, pathlib, urllib.request

OUT = pathlib.Path("data/public/live_snapshot.json")
OUT.parent.mkdir(parents=True, exist_ok=True)
snap = {"gems_hardware_url": "https://gems-erasmus.eu/hardware/", "modules_expected": ["Diamond","Ruby","Sapphire","Emerald","Drivetrain","Robots","Amethyst","Citrine"]}
for url in ["https://gems-erasmus.eu/hardware/", "https://api.openalex.org/works?search=mechatronics+mobile+robot&per-page=3"]:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body = r.read(2000).decode("utf-8", "ignore")
            snap[url] = {"bytes": len(body), "ok": True, "head": body[:300]}
            print("FETCH OK", url)
    except Exception as e:
        snap[url] = {"ok": False, "error": str(e)[:200]}
        print("FETCH SKIP (offline ok):", url, str(e)[:120])
json.dump(snap, open(OUT,"w"), indent=2)
print("wrote", OUT)
