#!/usr/bin/env python3
"""Ask the GPT model configured in spark-to-paper-skills/.env for a design
review of the demo page. Prints structured suggestions (JSON)."""
import os, sys

ENV = "/mnt/data0/LX_Bench/CS/hyperframes/spark-to-paper-skills/.env"
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))

from openai import OpenAI

model = os.environ.get("VISION_MODEL") or "gpt-5.5"
base = os.environ.get("TS_FIG_BASE_URL") or None
client = OpenAI(api_key=os.environ.get("TS_FIG_API_KEY") or os.environ["OPENAI_API_KEY"], base_url=base)

html = open(sys.argv[1]).read()

PROMPT = f"""You are a senior web designer reviewing an academic project demo page
(for an EMNLP system-demonstration paper). It uses the HTML5UP Stellar template,
MineDojo-site-style layout: full-page dark sci-fi generated background, compact
transparent title header, white pill nav, white content card with sections
(demo montage video, method explanation, 8-beat schema grid, gallery of 20
2-minute explainer videos), footer.

Give concrete, high-impact aesthetic improvements. Respond as JSON:
{{"suggestions": [{{"area": "typography|color|spacing|layout|copy|hero|gallery",
  "issue": "...", "fix": "specific CSS or copy change, ready to apply"}}]}}
Max 12 suggestions, each independently applicable, no framework changes, keep
the Stellar template and current structure. Focus on: title header impact,
readability over the dark background, section rhythm/spacing, gallery card
polish, pipeline step row, any awkward copy (keep technical claims unchanged).

CURRENT PAGE HTML (truncated to first 12000 chars):
{html[:12000]}
"""

r = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": PROMPT}],
    response_format={"type": "json_object"},
)
print(r.choices[0].message.content)
