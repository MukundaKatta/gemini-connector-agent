"""Build the gemini-connector-agent demo video end-to-end."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
FG = "#0f172a"
FG_MUTED = "#475569"
ACCENT = "#0a3d8f"   # Fivetran-ish deep blue
ACCENT_2 = "#16a34a"
ACCENT_3 = "#dc2626"
BG = "#ffffff"
PANEL = "#f8fafc"
CODE_BG = "#0f172a"
CODE_FG = "#e2e8f0"

SF = "/System/Library/Fonts/SFNS.ttf"
SFI = "/System/Library/Fonts/SFNSItalic.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(MONO).exists():
    MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False, italic=False):
    path = MONO if mono else (SFI if italic else SF)
    return ImageFont.truetype(path, size)


@dataclass
class Slide:
    name: str
    narration: str
    draw: callable


def base(img, d, title=None, eyebrow=None):
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "gemini-connector-agent", font=font(22), fill=FG)
    d.text((W - 680, H - 44), "github.com/MukundaKatta/gemini-connector-agent", font=font(22), fill=FG_MUTED)
    if eyebrow:
        d.text((96, 80), eyebrow.upper(), font=font(26), fill=ACCENT)
    if title:
        d.text((96, 130), title, font=font(72), fill=FG)
        d.rectangle([(96, 230), (220, 236)], fill=ACCENT)


def draw_title(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "github.com/MukundaKatta/gemini-connector-agent", font=font(22), fill=FG_MUTED)
    d.text((W - 270, H - 44), "Apache 2.0", font=font(22), fill=FG_MUTED)
    d.text((96, 290), "gemini-connector-agent", font=font(96), fill=FG)
    d.rectangle([(96, 420), (340, 430)], fill=ACCENT)
    d.text((96, 470), "Fivetran connector-health triage", font=font(48), fill=FG_MUTED)
    d.text((96, 530), "via Gemini + the Fivetran MCP server.", font=font(48), fill=FG_MUTED)
    d.text((96, 720), "Google Cloud Rapid Agent Hackathon,", font=font(32), fill=FG)
    d.text((96, 765), "Fivetran partner track.", font=font(32), fill=FG)


def draw_problem(img, d):
    base(img, d, title="The setup", eyebrow="Why this agent")
    lines = [
        "Your data team has 47 Fivetran connectors.",
        "Three of them are broken right now.",
        "The Slack thread is full of guesses:",
        "  is it Salesforce throttling?",
        "  did someone rotate a token?",
        "  is the destination warehouse paused?",
        "",
        "The agent reads the actual error message in five seconds.",
    ]
    y = 290
    for line in lines:
        col = FG if line and not line.startswith("  ") else FG_MUTED
        d.text((96, y), line, font=font(38), fill=col)
        y += 64


def draw_architecture(img, d):
    base(img, d, title="How it works", eyebrow="Architecture")
    box_w = 380
    boxes = [
        ("User question",  "what's broken?",              ACCENT),
        ("ADK LlmAgent",   "Gemini 2.5 on Vertex AI",     FG),
        ("Fivetran MCP",   "list_connectors, history, ...", ACCENT_2),
    ]
    x = (W - 3 * box_w - 100) // 2
    for label, sub, color in boxes:
        d.rounded_rectangle([(x, 360), (x + box_w, 490)], radius=14, outline=color, width=4, fill=BG)
        d.text((x + 24, 380), label, font=font(32), fill=FG)
        d.text((x + 24, 430), sub, font=font(22), fill=FG_MUTED)
        x += box_w + 50
    a1 = ((W - 3 * box_w - 100) // 2) + box_w + 6
    a2 = a1 + box_w + 50
    d.text((a1, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((a2, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((96, 600), "Tool surface matches the official fivetran/fivetran-mcp server.", font=font(30), fill=FG)
    d.text((96, 650), "Stub for demos, real account via FIVETRAN_API_KEY + SECRET.", font=font(30), fill=FG)
    d.text((96, 770), "Five tools: list_connectors, get_connector, list_destinations,", font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 810), "get_destination, get_connector_sync_history.", font=font(28, italic=True), fill=FG_MUTED)


def draw_question(img, d):
    base(img, d, title="The triage", eyebrow="Live agent run")
    d.text((96, 320), "User asks:", font=font(36), fill=FG_MUTED)
    d.rounded_rectangle([(96, 380), (W - 96, 500)], radius=16, fill=PANEL)
    d.text((130, 410), '"Which Fivetran connectors are broken right now', font=font(36), fill=FG)
    d.text((130, 450), 'and why?"',                                          font=font(36), fill=FG)
    d.text((96, 580), "Agent walks two tools in order:", font=font(32), fill=FG_MUTED)
    steps = [
        "1.  list_connectors                 →  spots salesforce-main with status=broken",
        "2.  get_connector_sync_history      →  confirms recurring failures, not transient",
    ]
    y = 640
    for s in steps:
        d.text((130, y), s, font=font(24, mono=True), fill=FG)
        y += 50


def draw_answer(img, d):
    base(img, d, title="The triage answer", eyebrow="Real Vertex AI run")
    d.text((96, 320), "BROKEN CONNECTOR:", font=font(28, mono=True), fill=FG_MUTED)
    d.text((520, 320), "salesforce-main  salesforce  broken", font=font(28, mono=True), fill=ACCENT_3)
    d.text((96, 380), "ERROR:", font=font(28, mono=True), fill=FG_MUTED)
    d.text((520, 380), "API_DISABLED_FOR_ORG", font=font(28, mono=True), fill=ACCENT_3)
    d.text((96, 440), "HISTORY:", font=font(28, mono=True), fill=FG_MUTED)
    d.text((520, 440), "5 / 5 recent runs failed", font=font(28, mono=True), fill=FG)
    d.text((96, 530), "VERBATIM ERROR MESSAGE:", font=font(26, mono=True), fill=FG_MUTED)
    d.rounded_rectangle([(96, 570), (W - 96, 740)], radius=16, fill=PANEL)
    d.text((130, 600), 'REST API requests are disabled for this organization.', font=font(26), fill=FG)
    d.text((130, 640), 'Re-enable API access in Salesforce Setup > Profiles >',  font=font(26), fill=FG)
    d.text((130, 680), 'System Administrator > Administrative Permissions.',     font=font(26), fill=FG)
    d.text((96, 790), "ROOT CAUSE: org-level Salesforce config, not a flake or rate limit.",
           font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 835), "NEXT STEP: re-enable API access. Verbatim from the tool output.",
           font=font(28, italic=True), fill=FG_MUTED)


def draw_code(img, d):
    base(img, d, title="The implementation", eyebrow="Six lines of ADK")
    code = (
        "from google.adk.agents import LlmAgent\n"
        "from google.adk.tools.mcp_tool import McpToolset\n"
        "from gemini_connector_agent.agent import _fivetran_toolset\n"
        "\n"
        "agent = LlmAgent(\n"
        "    model='gemini-2.5-flash',\n"
        "    name='gemini_connector_agent',\n"
        "    instruction=SYSTEM_PROMPT,\n"
        "    tools=[_fivetran_toolset(stub=True)],\n"
        ")"
    )
    d.rounded_rectangle([(96, 320), (W - 96, H - 130)], radius=18, fill=CODE_BG)
    yy = 360
    for line in code.split("\n"):
        d.text((130, yy), line, font=font(30, mono=True), fill=CODE_FG)
        yy += 46


def draw_close(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.text((96, 180), "gemini-connector-agent", font=font(70), fill=FG)
    d.rectangle([(96, 270), (340, 280)], fill=ACCENT)
    d.text((96, 320), "github.com/MukundaKatta/gemini-connector-agent", font=font(32, mono=True), fill=ACCENT)
    d.text((96, 400), "gemini-connector-agent-1029931682737.us-central1.run.app", font=font(30, mono=True), fill=ACCENT_2)
    d.text((96, 530), "Google Cloud Agent Builder (ADK)", font=font(32), fill=FG_MUTED)
    d.text((96, 580), "+ Gemini 2.5 on Vertex AI", font=font(32), fill=FG_MUTED)
    d.text((96, 630), "+ Fivetran MCP server (stub for demos, real-account ready)", font=font(32), fill=FG_MUTED)
    d.text((96, 720), "Sixth and final entry in the GCRA partner-track sweep:", font=font(26, italic=True), fill=FG_MUTED)
    d.text((96, 760), "Dynatrace, Arize, MongoDB, Elastic, GitLab, Fivetran.", font=font(26, italic=True), fill=FG_MUTED)
    d.text((96, 830), "Apache 2.0. Mukunda Katta, independent.", font=font(28, italic=True), fill=FG_MUTED)


SLIDES = [
    Slide("01_title",
          "Gemini connector agent. Fivetran connector health triage via Gemini and the Fivetran M C P server, built on Google Cloud's Agent Development Kit.",
          draw_title),
    Slide("02_problem",
          "Your data team has forty seven Fivetran connectors. Three of them are broken right now. The Slack thread is full of guesses, is it Salesforce throttling, did someone rotate a token, is the destination warehouse paused. The agent reads the actual error message in five seconds.",
          draw_problem),
    Slide("03_architecture",
          "Three boxes. A user question goes into an A D K L L M agent powered by Gemini two point five on Vertex A I. The agent uses M C P toolset to call the Fivetran M C P server with five tools list connectors, get connector, list destinations, get destination, get connector sync history. Stub for demos, real account one A P I key away.",
          draw_architecture),
    Slide("04_question",
          "Here is a real triage. The user asks, which Fivetran connectors are broken right now and why. The agent walks two tools. List connectors spots salesforce main with status broken. Get connector sync history confirms the failures are recurring, not transient.",
          draw_question),
    Slide("05_answer",
          "The triage answer cites the broken connector by name. Salesforce main. Status broken. Five of five recent runs failed. Error code A P I disabled for org. The agent then quotes the full remediation message from the tool output verbatim. R E S T A P I requests are disabled for this organization. Re enable A P I access in Salesforce Setup, Profiles, System Administrator, Administrative Permissions. Root cause is an org level Salesforce config, not a flake or rate limit. Next step comes directly from the error.",
          draw_answer),
    Slide("06_code",
          "The agent fits in six lines of Google's A D K. One L L M agent, one M C P toolset bound to the stub or real Fivetran server, a Gemini model, and a system prompt that defines the triage workflow.",
          draw_code),
    Slide("07_close",
          "Gemini connector agent. Apache two point zero. Sixth and final entry in the G C R A partner track sweep. Dynatrace, Arize, Mongo D B, Elastic, Git Lab, Fivetran. Thank you.",
          draw_close),
]


def render_slides(outdir):
    paths = []
    for sl in SLIDES:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        sl.draw(img, d)
        p = outdir / f"{sl.name}.png"
        img.save(p, "PNG", optimize=True)
        paths.append(p)
        print(f"  rendered {p.name}")
    return paths


def render_audio(outdir):
    paths = []
    for sl in SLIDES:
        wav = outdir / f"{sl.name}.aiff"
        m4a = outdir / f"{sl.name}.m4a"
        subprocess.run(["say", "-v", "Samantha", "-r", "175", "-o", str(wav), sl.narration], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                        "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
        wav.unlink(missing_ok=True)
        paths.append(m4a)
        print(f"  spoke   {m4a.name}")
    return paths


def render_segments(outdir, slide_pngs, audio_m4as):
    segs = []
    for sl, png, m4a in zip(SLIDES, slide_pngs, audio_m4as):
        out = outdir / f"seg_{sl.name}.mp4"
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(m4a)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        seg_dur = float(dur) + 0.4
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-i", str(m4a),
            "-af", "apad=pad_dur=0.4",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-r", "30", "-t", f"{seg_dur:.2f}",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", str(out),
        ], check=True)
        segs.append(out)
        print(f"  segment {out.name}  ({seg_dur:.2f}s)")
    return segs


def concat(outdir, segs):
    list_file = outdir / "concat.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in segs) + "\n")
    out = outdir / "demo.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ], check=True)
    return out


def main():
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "gemini-connector-agent" / ".video-build"
    outdir.mkdir(parents=True, exist_ok=True)
    for needed in ("ffmpeg", "ffprobe", "say"):
        if shutil.which(needed) is None:
            sys.exit(f"missing tool: {needed}")
    print("[1/4] slides...")
    slides = render_slides(outdir)
    print("[2/4] audio...")
    audios = render_audio(outdir)
    print("[3/4] segments...")
    segs = render_segments(outdir, slides, audios)
    print("[4/4] concat...")
    final = concat(outdir, segs)
    size = final.stat().st_size / (1024 * 1024)
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
        capture_output=True, text=True,
    ).stdout.strip()
    print(f"\nDONE: {final}  ({size:.1f} MB, {float(dur):.1f}s)")


if __name__ == "__main__":
    main()
