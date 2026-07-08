#!/usr/bin/env python3
"""Pre-render a MineDojo-style zoom-out video-wall hero (hero_mosaic.mp4).

Reads a manifest of source videos, lays them out on a 4x4 wall rendered at
2x the output resolution, then runs a virtual camera that holds on the
center 2x2 for a few seconds, smoothly zooms out to reveal the full wall,
and holds on the final wall. Optionally bakes a title overlay into a second
output. Everything is done with ffmpeg; no realtime multi-<video> playback.

Usage:
  python3 scripts/make_hero_mosaic.py \
    --input-manifest assets/hero/selected_videos.json \
    --output assets/hero/hero_mosaic.mp4 \
    --duration 15 --fps 24 --resolution 1920x1080 --grid 4x4 \
    --title-output assets/hero/hero_mosaic_title.mp4
"""
import argparse, json, os, subprocess, sys, tempfile

BG = "#0d0d18"          # wall background (deep space blue-black)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def make_corner_mask(cell_w, cell_h, pad_x, pad_y, radius, path):
    """One grid cell, bg-colored everywhere except a transparent rounded-rect
    hole where the video shows through. Tiled over the wall it yields gaps +
    rounded corners with a single static overlay."""
    from PIL import Image, ImageDraw
    bg = tuple(int(BG[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    img = Image.new("RGBA", (cell_w, cell_h), bg)
    hole = Image.new("L", (cell_w, cell_h), 0)
    d = ImageDraw.Draw(hole)
    d.rounded_rectangle(
        [pad_x, pad_y, cell_w - pad_x - 1, cell_h - pad_y - 1],
        radius=radius, fill=255)
    img.putalpha(Image.eval(hole, lambda v: 255 - v))
    img.save(path)


def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-manifest", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title-output", default=None)
    ap.add_argument("--duration", type=float, default=15)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--resolution", default="1920x1080")
    ap.add_argument("--grid", default="4x4")
    ap.add_argument("--hold-in", type=float, default=3.0,
                    help="seconds to hold the opening 2x2 close-up")
    ap.add_argument("--zoom-end", type=float, default=10.0,
                    help="second at which the zoom-out completes")
    ap.add_argument("--crf", type=int, default=24)
    ap.add_argument("--speed", type=float, default=1.0,
                    help="tile playback speed factor (1.35 = 35% faster)")
    ap.add_argument("--title", default="PaperVidSkill")
    ap.add_argument("--slogan",
                    default="A Claude Code Skill for Scientific Paper-to-Video Generation")
    args = ap.parse_args()

    out_w, out_h = (int(v) for v in args.resolution.split("x"))
    cols, rows = (int(v) for v in args.grid.split("x"))
    with open(args.input_manifest) as f:
        manifest = json.load(f)
    vids = manifest["videos"]
    need = cols * rows
    if len(vids) < need:
        sys.exit(f"manifest has {len(vids)} videos, grid needs {need}")
    vids = vids[:need]

    base = os.path.dirname(os.path.abspath(args.input_manifest))
    root = os.getcwd()

    # Wall rendered at 2x output so the opening 2x2 close-up is pixel-true.
    wall_w, wall_h = out_w * 2, out_h * 2
    cell_w, cell_h = wall_w // cols, wall_h // rows          # 960x540
    pad_x, pad_y = 32, 18                                    # video 896x504 inside cell
    vid_w, vid_h = cell_w - 2 * pad_x, cell_h - 2 * pad_y

    tmp = tempfile.mkdtemp(prefix="hero_")
    mask_png = os.path.join(tmp, "corner_mask.png")
    make_corner_mask(cell_w, cell_h, pad_x, pad_y, 18, mask_png)

    # ---- one-pass filter graph: 16 tiles -> xstack wall -> mask -> zoompan
    inputs, filters, tags = [], [], []
    for i, v in enumerate(vids):
        src = v["source_video_path"]
        if not os.path.isabs(src):
            for cand in (os.path.join(base, src), os.path.join(root, src)):
                if os.path.exists(cand):
                    src = cand
                    break
        inputs += ["-ss", str(v.get("start_offset", 0)), "-t",
                   str(args.duration * args.speed + 1), "-i", src]
        filters.append(
            f"[{i}:v]setpts=PTS/{args.speed},fps={args.fps},"
            f"scale={vid_w}:{vid_h},setsar=1,"
            f"pad={cell_w}:{cell_h}:{pad_x}:{pad_y}:{BG},"
            f"trim=duration={args.duration},setpts=PTS-STARTPTS[t{i}]")
        tags.append(f"[t{i}]")
    layout = "|".join(f"{(i % cols) * cell_w}_{(i // cols) * cell_h}"
                      for i in range(need))
    inputs += ["-loop", "1", "-i", mask_png]
    filters.append("".join(tags) + f"xstack=inputs={need}:layout={layout}[wall]")
    filters.append(
        f"[{need}:v]tile={cols}x{rows}[maskwall];"
        f"[wall][maskwall]overlay=0:0:shortest=1[rounded]")

    # camera: hold z=2 (center 2x2), smoothstep out to z=1, hold full wall
    f_hold = int(args.hold_in * args.fps)
    f_zoom = int(args.zoom_end * args.fps)
    span = f_zoom - f_hold
    p = f"((on-{f_hold})/{span})"
    zexpr = (f"if(lte(on,{f_hold}),2,"
             f"if(gte(on,{f_zoom}),1,2-pow({p}\\,2)*(3-2*{p})))")
    # supersample the zoom (render at wall resolution, then lanczos-downscale)
    # so the virtual camera moves in sub-output-pixel steps without jitter
    filters.append(
        f"[rounded]zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        f":d=1:s={wall_w}x{wall_h}:fps={args.fps},"
        f"scale={out_w}:{out_h}:flags=lanczos,format=yuv420p[out]")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "warning", *inputs,
         "-filter_complex", ";".join(filters), "-map", "[out]",
         "-t", str(args.duration), "-r", str(args.fps),
         "-c:v", "libx264", "-crf", str(args.crf), "-preset", "medium",
         "-an", "-movflags", "+faststart", args.output])

    if args.title_output:
        # title fades in once the full wall is visible
        t0 = args.zoom_end + 0.5
        common = (f"fontfile={FONT}:fontcolor=white:x=(w-text_w)/2:"
                  f"alpha='if(lt(t,{t0}),0,min(1,(t-{t0})/0.8))':"
                  f"shadowcolor=black@0.7:shadowx=2:shadowy=2")
        vf = (f"drawbox=x=0:y=ih*0.30:w=iw:h=ih*0.34:color=black@0.35:t=fill:"
              f"enable='gte(t,{t0})',"
              f"drawtext=text='{args.title}':fontsize=110:y=h*0.36:{common},"
              f"drawtext=text='{args.slogan}':fontsize=38:y=h*0.36+150:{common}")
        run(["ffmpeg", "-y", "-loglevel", "warning", "-i", args.output,
             "-vf", vf, "-c:v", "libx264", "-crf", str(args.crf),
             "-preset", "medium", "-an", "-movflags", "+faststart",
             args.title_output])

    for f in (args.output, args.title_output):
        if f and os.path.exists(f):
            print(f"{f}: {os.path.getsize(f)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
