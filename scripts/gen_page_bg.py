#!/usr/bin/env python3
"""Generate the demo-page background with the image model configured in
spark-to-paper-skills/.env (TS_FIG_* settings, OpenAI-style API)."""
import base64, os, sys

ENV = "/mnt/data0/LX_Bench/CS/hyperframes/spark-to-paper-skills/.env"
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))

from openai import OpenAI

model = os.environ.get("TS_FIG_MODEL") or "gpt-image-1"
base = os.environ.get("TS_FIG_BASE_URL") or os.environ.get("VISION_BASE_URL") or None
key = os.environ.get("TS_FIG_API_KEY") or os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=key, base_url=base)

PROMPT = (
    "A wide cinematic website hero background for an AI research project that turns "
    "scientific papers into explainer videos. Deep space blue-black base (#0a0a16) with a "
    "subtle nebula gradient in indigo and violet, faint constellation-like network lines, "
    "a soft abstract suggestion of a glowing paper page dissolving into film-strip light "
    "trails and playback timelines drifting to the right, tiny star particles, gentle "
    "purple-magenta glow accents near the horizon. Elegant, dark, futuristic, minimal. "
    "Strictly decorative: NO text, NO letters, NO logos, NO charts, NO UI, NO people. "
    "Very low contrast in the center so overlaid white text stays readable."
)

out = sys.argv[1] if len(sys.argv) > 1 else "page_bg.png"
print(f"model={model} base={base or 'default'}")
kwargs = dict(model=model, prompt=PROMPT, size="1536x1024", n=1)
q = os.environ.get("TS_FIG_QUALITY")
if q:
    kwargs["quality"] = q
r = client.images.generate(**kwargs)
d = r.data[0]
if getattr(d, "b64_json", None):
    open(out, "wb").write(base64.b64decode(d.b64_json))
else:
    import urllib.request
    urllib.request.urlretrieve(d.url, out)
print("saved", out, os.path.getsize(out))
