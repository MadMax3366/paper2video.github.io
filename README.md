# Paper2Video — demo site

A demo gallery for **Paper2Video**: an automated pipeline that turns a research paper (PDF)
into a 60-second animated explainer video, built on [HyperFrames](https://github.com).

It extracts the paper's main figure + result tables/plots, writes a content-rich **8-beat**
narration, lays out an animated composition with captions and figure call-outs, generates a
voiceover, renders the video, and optionally composites a realistic **talking-head avatar**
narrator in the corner.

## Contents
- `index.html` — the demo page (page style: Stellar by HTML5 UP).
- `videos/` — generated explainer videos (hero, 3 avatar-narrator variants, 10 ICML 2026 papers).
- `assets/`, `images/` — page template assets.

## Deploy (GitHub Pages)
Settings → Pages → Source: **Deploy from a branch** → `main` / root. The site serves at
`https://<user>.github.io/paper2video.github.io/`. (`.nojekyll` disables Jekyll so all static
files are served as-is.) GitHub Pages on a free account requires a **public** repo; for a
private repo use GitHub Pro, or host on Cloudflare Pages / Netlify / Vercel.
