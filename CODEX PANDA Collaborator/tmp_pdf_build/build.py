"""Build the PANDA Collaborator Setup & Daily Use Guide PDF.

Pipeline:
  1. Pillow-annotate captured screenshots (S2 hub, S4 handoff form)
  2. Pillow-draw registration form + confirmation illustrations
  3. Assemble 6-page PDF with ReportLab Platypus
  4. Save to PANDA_Collaborator_Setup_Guide.pdf
"""
from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

# === paths ===
PC_ROOT = Path(r"C:\CODEX PG\CODEX PANDA Collaborator")
TMP = PC_ROOT / "tmp_pdf_build"
SHOT_HUB = TMP / "shot_hub.png"
SHOT_DARRIN = TMP / "shot_darrin_active.png"
SHOT_PAM = TMP / "shot_pam_active.png"
SHOT_HANDOFF = TMP / "shot_handoff_form.png"
OUT_PDF = PC_ROOT / "PANDA_Collaborator_Setup_Guide.pdf"

# Annotated image targets
ANN_DARRIN_HUB = TMP / "ann_darrin_hub.png"
ANN_HANDOFF = TMP / "ann_handoff_form.png"
ILL_DARRIN_FORM = TMP / "ill_darrin_form.png"
ILL_PAM_FORM = TMP / "ill_pam_form.png"
ILL_CONFIRMATION = TMP / "ill_confirmation.png"

# === palette (per spec §4 + active-state values per Issue D resolution) ===
# Cover/chip values use spec table; in-app illustrations use active-state.
SPEC_AMBER = "#e8a87c"   # Darrin chip on cover
SPEC_CYAN = "#5fa0a8"    # Pam chip on cover
APP_AMBER = "#f2b36d"    # active Darrin in real app
APP_CYAN = "#68d8e8"     # active Pam in real app
DARK = "#14141f"
SURFACE = "#1a1a2e"
SURFACE_2 = "#22223a"
LINE = "#2a2a3e"
TEXT = "#e0ddd5"
MUTED = "#888888"
OK_COLOR = "#7fb069"
BAD_COLOR = "#e74c3c"
WARN_COLOR = "#f39c12"

PDF_BG = colors.white
PDF_BODY = colors.HexColor("#111827")

# Step number colors
STEP_DARK = colors.HexColor("#1a1a2e")
STEP_AMBER = colors.HexColor("#d97706")
STEP_CYAN = colors.HexColor("#0891b2")
STEP_GREEN = colors.HexColor("#16a34a")
STEP_TEXT = colors.white

# === font helpers ===
def _font(size: int):
    """Return a TrueType font if available, else default."""
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _font_bold(size: int):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return _font(size)


def _font_mono(size: int):
    candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return _font(size)


# === Pillow helpers ===
def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _draw_arrowhead(draw, from_pt, to_pt, color, size: int = 12) -> None:
    dx = to_pt[0] - from_pt[0]
    dy = to_pt[1] - from_pt[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    p1 = (to_pt[0] - ux * size + px * size / 2, to_pt[1] - uy * size + py * size / 2)
    p2 = (to_pt[0] - ux * size - px * size / 2, to_pt[1] - uy * size - py * size / 2)
    draw.polygon([to_pt, p1, p2], fill=color)


def annotate(src: Path, dst: Path, callouts: list[dict]) -> None:
    """Draw labelled callout arrows over an existing image and save."""
    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    label_font = _font_bold(20)
    for c in callouts:
        col = c.get("color", hex_to_rgb(APP_AMBER))
        tip = tuple(c["tip"])
        anc = tuple(c["anchor"])
        # leader line
        draw.line([anc, tip], fill=col, width=3)
        _draw_arrowhead(draw, anc, tip, col, size=14)
        # text box
        text = c["label"]
        bbox = draw.textbbox((0, 0), text, font=label_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 10, 6
        # box anchored at anc, extending in the natural direction (right or left of anc)
        ax, ay = anc
        if ax > tip[0]:
            box = (ax - 4, ay - th // 2 - pad_y, ax + tw + pad_x * 2 + 4, ay + th // 2 + pad_y)
            text_xy = (ax + pad_x, ay - th // 2 - 2)
        else:
            box = (ax - tw - pad_x * 2 - 4, ay - th // 2 - pad_y, ax + 4, ay + th // 2 + pad_y)
            text_xy = (ax - tw - pad_x, ay - th // 2 - 2)
        draw.rectangle(box, fill=hex_to_rgb(DARK) + (240,), outline=col, width=2)
        draw.text(text_xy, text, fill=hex_to_rgb(TEXT), font=label_font)
    img.save(dst, "PNG")


# === illustration: registration form ===
def draw_registration_form(
    name: str,
    accent_hex: str,
    button_hex: str,
    button_text: str,
    fields: list[tuple[str, str, str]],
    out_path: Path,
    callouts: list[dict] | None = None,
) -> Path:
    """Render a faux registration panel that matches the app's dark style.

    fields: list of (label, value, hint) — hint values:
        'empty'   — empty cursor field (highlighted)
        'filled'  — pre-filled, dim text
        'mono'    — pre-filled, monospaced (for paths)
    """
    W, H = 1100, 720
    img = Image.new("RGB", (W, H), color=hex_to_rgb(DARK))
    draw = ImageDraw.Draw(img)

    # Title bar
    title_h = 40
    draw.rectangle((0, 0, W, title_h), fill=hex_to_rgb(DARK))
    draw.line((0, title_h, W, title_h), fill=hex_to_rgb(LINE), width=1)
    draw.text((20, 12), "PANDA Collaborator", fill=hex_to_rgb(TEXT), font=_font_bold(16))
    draw.text((W - 280, 14), "Setup — Register Users", fill=hex_to_rgb(MUTED), font=_font(13))

    # Section header
    sec_y = title_h + 18
    draw.text((30, sec_y), f"Register {name}", fill=hex_to_rgb(accent_hex), font=_font_bold(22))

    # Field rows — compact
    y = sec_y + 40
    row_h = 44
    label_w = 280
    field_w = W - 60 - label_w - 30
    for i, (label, value, kind) in enumerate(fields):
        bg = hex_to_rgb(SURFACE if i % 2 == 0 else SURFACE_2)
        draw.rectangle((30, y, W - 30, y + row_h - 3), fill=bg, outline=hex_to_rgb(LINE), width=1)
        draw.text((50, y + 14), label, fill=hex_to_rgb(MUTED), font=_font(13))
        # field box
        fx0 = 50 + label_w
        fy0 = y + 8
        fx1 = W - 50
        fy1 = y + row_h - 11
        draw.rectangle((fx0, fy0, fx1, fy1), fill=hex_to_rgb(DARK), outline=hex_to_rgb(LINE), width=1)
        if kind == "empty":
            draw.rectangle((fx0, fy0, fx1, fy1), fill=hex_to_rgb(DARK), outline=hex_to_rgb(accent_hex), width=2)
            draw.line((fx0 + 12, fy0 + 5, fx0 + 12, fy1 - 5), fill=hex_to_rgb(accent_hex), width=2)
            draw.text((fx0 + 22, y + 12), "(type here)", fill=hex_to_rgb(MUTED), font=_font(13))
        else:
            font = _font_mono(13) if kind == "mono" else _font(13)
            color_txt = hex_to_rgb(MUTED) if kind == "filled" else hex_to_rgb(TEXT)
            max_w = fx1 - fx0 - 24
            txt = value
            while txt and draw.textlength(txt, font=font) > max_w:
                txt = txt[:-1]
            if txt != value:
                txt = txt[:-1] + "..."
            draw.text((fx0 + 12, y + 12), txt, fill=color_txt, font=font)
        y += row_h

    # Register button
    btn_y = y + 16
    btn_h = 48
    btn_w = 540
    btn_x = (W - btn_w) // 2
    draw.rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), fill=hex_to_rgb(button_hex))
    bf = _font_bold(18)
    btxt_w = draw.textlength(button_text, font=bf)
    draw.text((btn_x + (btn_w - btxt_w) / 2, btn_y + 13), button_text, fill=(255, 255, 255), font=bf)

    img.save(out_path, "PNG")

    if callouts:
        annotate(out_path, out_path, callouts)
    return out_path


# === illustration: confirmation screen ===
def draw_confirmation(name: str, out_path: Path) -> Path:
    W, H = 1100, 480
    img = Image.new("RGB", (W, H), color=hex_to_rgb(DARK))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle((0, 0, W, 50), fill=hex_to_rgb(DARK))
    draw.line((0, 50, W, 50), fill=hex_to_rgb(LINE), width=1)
    draw.text((20, 14), "PANDA Collaborator", fill=hex_to_rgb(TEXT), font=_font_bold(18))
    draw.text((W - 240, 16), "Confirmation", fill=hex_to_rgb(MUTED), font=_font(15))

    # Big check
    cx, cy = 70, 130
    draw.ellipse((cx, cy, cx + 80, cy + 80), fill=hex_to_rgb(OK_COLOR))
    draw.line((cx + 22, cy + 42, cx + 38, cy + 58), fill=(20, 20, 31), width=8)
    draw.line((cx + 38, cy + 58, cx + 64, cy + 28), fill=(20, 20, 31), width=8)

    # Heading
    draw.text((cx + 110, cy + 8), f"User 1 registered: {name}",
              fill=hex_to_rgb(OK_COLOR), font=_font_bold(28))
    draw.text((cx + 110, cy + 50), "Check the values below, then continue to User 2.",
              fill=hex_to_rgb(MUTED), font=_font(15))

    # Info rows
    rows = [
        ("Name", name),
        ("Repo path", r"C:\CODEX PG"),
        ("Git author", "Codex Backup"),
    ]
    ry = 250
    for k, v in rows:
        draw.rectangle((60, ry, W - 60, ry + 50), fill=hex_to_rgb(SURFACE), outline=hex_to_rgb(LINE), width=1)
        draw.text((80, ry + 16), k, fill=hex_to_rgb(MUTED), font=_font(15))
        draw.text((280, ry + 16), v, fill=hex_to_rgb(TEXT), font=_font_mono(15))
        ry += 60

    # Continue button
    btn_h = 56
    btn_w = 360
    btn_x = (W - btn_w) // 2
    btn_y = H - btn_h - 30
    draw.rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), fill=hex_to_rgb(STEP_AMBER.hexval()[2:]))
    bf = _font_bold(20)
    bt = "Continue to User 2 →"
    btxt_w = draw.textlength(bt, font=bf)
    draw.text((btn_x + (btn_w - btxt_w) / 2, btn_y + 16), bt, fill=(255, 255, 255), font=bf)

    img.save(out_path, "PNG")
    return out_path


# === build all illustrations ===
def build_illustrations() -> None:
    # S2 (Darrin hub) — annotate
    # Coords are for the live 1366×768 capture, not the old smoke png.
    darrin_callouts = [
        {"label": "Active user — Darrin",  "tip": (380, 32),  "anchor": (700, 32),
         "color": hex_to_rgb(APP_AMBER)},
        {"label": "Switch users here",     "tip": (470, 215), "anchor": (200, 380),
         "color": hex_to_rgb(APP_AMBER)},
        {"label": "Start your session",    "tip": (615, 180), "anchor": (220, 480),
         "color": hex_to_rgb(OK_COLOR)},
        {"label": "End session / Handoff", "tip": (965, 505), "anchor": (1100, 600),
         "color": hex_to_rgb(OK_COLOR)},
    ]
    annotate(SHOT_DARRIN, ANN_DARRIN_HUB, darrin_callouts)

    # S4 (handoff form) — annotate
    # Image is ~549×475 (the cropped region)
    handoff_img = Image.open(SHOT_HANDOFF)
    hw, hh = handoff_img.size
    # TITLE field is roughly mid-left in the form. CREATE SAFE HANDOFF button is top.
    handoff_callouts = [
        {"label": "Title here",
         "tip": (130, 135), "anchor": (300, 175),
         "color": hex_to_rgb(APP_AMBER)},
        {"label": "Click to save",
         "tip": (275, 75), "anchor": (395, 35),
         "color": hex_to_rgb(OK_COLOR)},
    ]
    annotate(SHOT_HANDOFF, ANN_HANDOFF, handoff_callouts)

    # Darrin registration form
    darrin_fields = [
        ("Name", "", "empty"),
        ("Repo path", r"C:\CODEX PG", "mono"),
        ("Handoff agent", "Codex", "filled"),
        ("Handoff title", "Darrin handoff", "filled"),
        ("Codex account", "Codex (Darrin)", "filled"),
        ("Claude account", "Claude (Darrin)", "filled"),
        ("Claude Desktop", r"C:\Users\drrap\AppData\Local\AnthropicClaude\claude.exe", "mono"),
        ("Claude Code", r"C:\Users\drrap\AppData\Roaming\npm\claude.CMD", "mono"),
        ("Git name", "Codex Backup", "filled"),
        ("Git email", "codex-backup@local", "filled"),
    ]
    darrin_form_callouts = [
        {"label": "Type your name here",
         "tip": (380, 119), "anchor": (740, 119),
         "color": hex_to_rgb(APP_AMBER)},
        {"label": "Pre-filled",
         "tip": (520, 162), "anchor": (820, 195),
         "color": hex_to_rgb(MUTED)},
        {"label": "Click to register",
         "tip": (550, 578), "anchor": (820, 650),
         "color": hex_to_rgb(OK_COLOR)},
    ]
    draw_registration_form(
        name="Darrin",
        accent_hex=APP_AMBER,
        button_hex="#d97706",
        button_text="Register User 1 and continue →",
        fields=darrin_fields,
        out_path=ILL_DARRIN_FORM,
        callouts=darrin_form_callouts,
    )

    # Pam registration form
    pam_fields = [
        ("Name", "", "empty"),
        ("Repo path", r"C:\CODEX PG", "mono"),
        ("Handoff agent", "Claude", "filled"),
        ("Handoff title", "CD handoff", "filled"),
        ("Codex account", "Codex (Pam)", "filled"),
        ("Claude account", "Claude (Pam)", "filled"),
        ("Claude Desktop", r"C:\Users\drrap\AppData\Local\AnthropicClaude\claude.exe", "mono"),
        ("Claude Code", r"C:\Users\drrap\AppData\Roaming\npm\claude.CMD", "mono"),
        ("Git name", "Pam Rapoport", "filled"),
        ("Git email", "darrinpam@comcast.net", "filled"),
    ]
    pam_form_callouts = [
        {"label": "Type your name here",
         "tip": (380, 119), "anchor": (740, 119),
         "color": hex_to_rgb(APP_CYAN)},
        {"label": "Pre-filled",
         "tip": (520, 162), "anchor": (820, 195),
         "color": hex_to_rgb(MUTED)},
        {"label": "Click to register",
         "tip": (550, 578), "anchor": (820, 650),
         "color": hex_to_rgb(OK_COLOR)},
    ]
    draw_registration_form(
        name="Pam",
        accent_hex=APP_CYAN,
        button_hex="#5fa0a8",
        button_text="Register User 2 and open Hub →",
        fields=pam_fields,
        out_path=ILL_PAM_FORM,
        callouts=pam_form_callouts,
    )

    # Confirmation screen
    draw_confirmation("Darrin", ILL_CONFIRMATION)

    print("[build] illustrations done")


# === ReportLab helpers ===
class CoverBand(Flowable):
    """Full-width dark band with cover branding + amber rule below."""
    def __init__(self, width: float, band_h: float = 100):
        super().__init__()
        self.width = width
        self.band_h = band_h
        self.height = band_h + 6  # band + rule + small gap

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(colors.HexColor(DARK))
        c.rect(0, 6, self.width, self.band_h, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(20, 6 + self.band_h / 2 + 2, "PANDA Collaborator")
        c.setFillColor(colors.HexColor("#888888"))
        c.setFont("Helvetica", 12)
        c.drawRightString(self.width - 20, 6 + self.band_h / 2 + 2, "Setup & Daily Use Guide")
        # Amber rule below
        c.setStrokeColor(colors.HexColor(SPEC_AMBER))
        c.setLineWidth(2)
        c.line(0, 0, self.width, 0)
        c.restoreState()


class SectionRule(Flowable):
    """Colored horizontal rule for section openers."""
    def __init__(self, width: float, color_hex: str, weight: float = 3):
        super().__init__()
        self.width = width
        self.color = colors.HexColor(color_hex)
        self.weight = weight
        self.height = weight + 4

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.weight)
        c.line(0, self.height / 2, self.width, self.height / 2)


def style(name: str = "body", **kw):
    base = ParagraphStyle("base", fontName="Helvetica", fontSize=10, leading=14,
                          textColor=PDF_BODY)
    base.__dict__.update(kw)
    base.name = name
    return base


def user_chip(label: str, color_hex: str, fill_alpha_hex: str, total_w: float) -> Table:
    """Small pill-style user chip for the cover."""
    body = Paragraph(
        f'<font color="{color_hex}" size="14">●</font>&nbsp;&nbsp;'
        f'<font size="10">{label}</font>',
        style("chip", fontSize=10, textColor=PDF_BODY, leading=14),
    )
    t = Table([[body]], colWidths=[total_w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fill_alpha_hex)),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor(color_hex)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def step_card(num: str, color: colors.Color, title: str, body: str, total_w: float) -> Table:
    """Step card: numbered colored box on the left, title + body on the right."""
    num_para = Paragraph(
        f'<para align="center"><font name="Helvetica-Bold" size="14" color="white">{num}</font></para>',
        style("num"),
    )
    body_para = Paragraph(
        f'<font name="Helvetica-Bold" size="11">{title}</font><br/><br/>'
        f'<font size="9.5">{body}</font>',
        style("step", fontSize=10, leading=13),
    )
    left_w = 36
    t = Table([[num_para, body_para]], colWidths=[left_w, total_w - left_w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#f9fafb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
        ("TOPPADDING", (1, 0), (1, 0), 8),
        ("BOTTOMPADDING", (1, 0), (1, 0), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    return t


def info_box(text: str, kind: str = "info", total_w: float | None = None) -> Table:
    """Coloured-tint info / warning / safety box."""
    if kind == "warn":
        bg, border = colors.HexColor("#fff7ed"), colors.HexColor(WARN_COLOR)
    elif kind == "ok":
        bg, border = colors.HexColor("#ecfdf5"), colors.HexColor(OK_COLOR)
    elif kind == "blue":
        bg, border = colors.HexColor("#eff6ff"), colors.HexColor("#3b82f6")
    elif kind == "red":
        bg, border = colors.HexColor("#fef2f2"), colors.HexColor(BAD_COLOR)
    else:
        bg, border = colors.HexColor("#f3f4f6"), colors.HexColor("#9ca3af")
    p = Paragraph(text, style("infobox", fontSize=9.5, leading=13))
    cw = [total_w] if total_w else None
    t = Table([[p]], colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def trouble_card(badge: str, badge_color: str, title: str, detail: str, total_w: float) -> Table:
    """Issue card for troubleshooting: short ASCII badge + title + body."""
    badge_p = Paragraph(
        f'<para align="center"><font name="Helvetica-Bold" size="14" color="white">{badge}</font></para>',
        style("badge"),
    )
    body = Paragraph(
        f'<font name="Helvetica-Bold" size="10">{title}</font><br/><br/>'
        f'<font size="9">{detail}</font>',
        style("trouble", fontSize=9.5, leading=12),
    )
    left_w = 34
    t = Table([[badge_p, body]], colWidths=[left_w, total_w - left_w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(badge_color)),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#f9fafb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
        ("TOPPADDING", (1, 0), (1, 0), 6),
        ("BOTTOMPADDING", (1, 0), (1, 0), 6),
    ]))
    return t


# === build the PDF ===
def build_pdf() -> int:
    USABLE_W = 7 * inch  # 504pt
    PAGE_W, PAGE_H = letter

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="PANDA Collaborator — Setup & Daily Use Guide",
        author="Panda Gallery / PandaPerio",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                        fontSize=18, leading=22, textColor=PDF_BODY, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=13, leading=17, textColor=PDF_BODY, spaceAfter=6)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14,
                          textColor=PDF_BODY, spaceAfter=4)
    cap = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10,
                         textColor=colors.HexColor("#6b7280"), alignment=1)
    foot = ParagraphStyle("foot", fontName="Helvetica", fontSize=7,
                          textColor=colors.HexColor("#6b7280"), alignment=1)

    story: list = []

    # ============== PAGE 1 — Cover + Intro + Part 1 ==============
    story.append(CoverBand(USABLE_W, band_h=70))
    story.append(Spacer(1, 12))

    # Two user chips
    chip_t = Table(
        [[user_chip("Darrin · User 1 · Amber theme", SPEC_AMBER, "#fef3e7", USABLE_W / 2 - 4),
          user_chip("Pam · User 2 · Cyan theme", SPEC_CYAN, "#e8f4f6", USABLE_W / 2 - 4)]],
        colWidths=[USABLE_W / 2 - 4, USABLE_W / 2 - 4],
    )
    chip_t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(chip_t)
    story.append(Spacer(1, 14))

    # Intro
    story.append(Paragraph(
        "PANDA Collaborator helps Darrin and Pam share an AI coding workspace "
        "safely. When one person finishes and the other takes over, PANDA "
        "creates a safe handoff record so nothing is lost. First-time setup "
        "takes about 3 minutes and is done once. Daily use takes about 30 "
        "seconds.", body))
    story.append(Spacer(1, 12))

    # TOC
    toc_data = [
        ["Part", "Title", "When to use"],
        ["1", "First-Time Setup", "Once only — registers Darrin and Pam"],
        ["2", "Daily Use", "Every session — 30 seconds"],
        ["3", "Creating a Handoff", "When you finish working"],
        ["4", "Troubleshooting", "If something goes wrong"],
    ]
    toc = Table(toc_data, colWidths=[40, 150, USABLE_W - 190])
    toc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(toc)
    story.append(Spacer(1, 16))

    # Part 1 header
    story.append(SectionRule(USABLE_W, SPEC_AMBER))
    story.append(Paragraph("Part 1 — First-Time Setup", h1))
    story.append(Paragraph(
        "Do this once on each computer that runs PANDA Collaborator. "
        "After you finish, the Hub will open automatically every time.", body))
    story.append(Spacer(1, 6))

    # STEP 1
    story.append(step_card(
        "1", STEP_DARK, "Open PANDA Collaborator",
        "Double-click the PANDA Collaborator icon on your Desktop. Your "
        "browser opens automatically within a few seconds. The address is "
        "<font name=\"Courier\">http://127.0.0.1:8788/</font>.", USABLE_W))
    story.append(Spacer(1, 6))
    story.append(info_box(
        "The app runs entirely on your computer — nothing is sent to the "
        "internet just because you open it.", kind="blue", total_w=USABLE_W))
    story.append(PageBreak())

    # ============== PAGE 2 — Part 1 continued ==============
    # STEP 2
    story.append(step_card(
        "2", STEP_AMBER, "Register Darrin (User 1)",
        "The registration form opens automatically on first launch. Fill in "
        "Darrin's details below. Most fields are pre-filled — you only need "
        "to type the name.", USABLE_W))
    story.append(Spacer(1, 6))

    # Darrin form illustration
    img = RLImage(str(ILL_DARRIN_FORM), width=USABLE_W * 0.85, height=USABLE_W * 0.85 * 720 / 1100)
    story.append(img)
    story.append(Spacer(1, 4))
    story.append(info_box(
        "<b>If the Register button is grey,</b> scroll down — a required "
        "field may be below the visible area. The footer shows which fields "
        "are missing.", kind="warn", total_w=USABLE_W))
    story.append(PageBreak())

    # ============== PAGE 3 — Part 1 finish + Part 2 start ==============
    # STEP 3
    story.append(step_card(
        "3", STEP_GREEN, "See the Confirmation",
        "PANDA shows a confirmation screen with Darrin's saved details. "
        "Check that everything looks right, then click <b>Continue to "
        "User 2</b>.", USABLE_W))
    story.append(Spacer(1, 6))
    img_c = RLImage(str(ILL_CONFIRMATION), width=USABLE_W * 0.9,
                    height=USABLE_W * 0.9 * 480 / 1100)
    story.append(img_c)
    story.append(Spacer(1, 8))

    # STEP 4
    story.append(step_card(
        "4", STEP_CYAN, "Register Pam (User 2)",
        "The same form appears for Pam. Fill in Pam's details. Pam's row "
        "uses cyan accents instead of amber — that's how the app shows "
        "which user is being set up.", USABLE_W))
    story.append(Spacer(1, 6))
    img_p = RLImage(str(ILL_PAM_FORM), width=USABLE_W * 0.78,
                    height=USABLE_W * 0.78 * 720 / 1100)
    story.append(img_p)
    story.append(Spacer(1, 4))
    story.append(info_box(
        "Once both users are registered, the Hub opens automatically. "
        "You won't need to register again.", kind="ok", total_w=USABLE_W))
    story.append(PageBreak())

    # ============== PAGE 4 — Part 2: Daily Use ==============
    story.append(SectionRule(USABLE_W, SPEC_CYAN))
    story.append(Paragraph("Part 2 — Daily Use", h1))
    story.append(Paragraph(
        "Every time you open PANDA Collaborator, follow these steps. The "
        "whole thing takes about 30 seconds.", body))
    story.append(Spacer(1, 6))

    daily_steps = [
        ("1", STEP_DARK, "Open PANDA Collaborator",
         "Double-click the desktop icon. Your browser opens the Hub."),
        ("2", STEP_AMBER, "Click the Handover button for the active user",
         "Inside the User 1 (Darrin) or User 2 (Pam) card, click "
         "<b>Handover</b>. PANDA switches the colour theme and loads that "
         "person's settings."),
        ("3", STEP_DARK, "Confirm the name at the top of the screen",
         "The large name at the top shows who is active. Amber = Darrin. "
         "Cyan = Pam. Always check this before starting work."),
        ("4", STEP_GREEN, "Click Start Session / Start Work",
         "PANDA scans the project and shows a plain-English summary of what "
         "happened last time — concerns, achievements, and what to do next. "
         "Read it before starting."),
        ("5", STEP_DARK, "Do your work, then return to PANDA when done",
         "Work in Claude, Codex, or any other tool. Come back to PANDA "
         "when you finish."),
    ]
    for n, c, t, b in daily_steps:
        story.append(step_card(n, c, t, b, USABLE_W))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 4))
    hub_w = USABLE_W * 0.78
    img_hub = RLImage(str(ANN_DARRIN_HUB), width=hub_w, height=hub_w * 768 / 1366)
    story.append(img_hub)
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "The Collaborator Hub with Darrin active (amber theme). The other "
        "user's Handover button is always visible — one click switches the "
        "active user.", cap))
    story.append(PageBreak())

    # ============== PAGE 5 — Part 3: Creating a Handoff ==============
    story.append(SectionRule(USABLE_W, OK_COLOR))
    story.append(Paragraph("Part 3 — Creating a Handoff", h1))
    story.append(Paragraph(
        "When you finish working, create a handoff so the next person has "
        "full context.", body))
    story.append(Spacer(1, 6))

    handoff_steps = [
        ("1", STEP_DARK, "Click End Session / Handoff",
         "Find this button in the Collaborator Hub. Click it."),
        ("2", STEP_DARK, "Enter a short title (optional)",
         "Describe what you did — for example: <i>Tracker filter fix, "
         "combo UX done</i>. Leave blank to use the default."),
        ("3", STEP_DARK, "Add notes (optional)",
         "Briefly note what you finished, any open issues, and what to "
         "do next."),
        ("4", STEP_GREEN, "Click Create safe handoff",
         "PANDA saves a protection branch, patch files for unsaved "
         "changes, file copies, and a plain-English HANDOFF summary."),
    ]
    for n, c, t, b in handoff_steps:
        story.append(step_card(n, c, t, b, USABLE_W))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 4))
    # Handoff form illustration
    hf_img = Image.open(SHOT_HANDOFF)
    hw, hh = hf_img.size
    target_w = USABLE_W * 0.62
    target_h = target_w * hh / hw
    img_handoff = RLImage(str(ANN_HANDOFF), width=target_w, height=target_h)
    img_handoff.hAlign = 'CENTER'
    story.append(img_handoff)
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "The Create Handoff form. Fill in the title and any notes, then "
        "click the button. PANDA handles the rest.", cap))
    story.append(Spacer(1, 8))
    story.append(info_box(
        "PANDA never deletes files, force-pushes, or discards unsaved "
        "work. It is always safe to click Create safe handoff.",
        kind="ok", total_w=USABLE_W))
    story.append(PageBreak())

    # ============== PAGE 6 — Part 4: Troubleshooting ==============
    story.append(SectionRule(USABLE_W, BAD_COLOR))
    story.append(Paragraph("Part 4 — Troubleshooting", h1))
    story.append(Spacer(1, 4))

    issues = [
        ("[!]", BAD_COLOR, "Something looks wrong — click Emergency Pause",
         "Click the red Emergency Pause button. This stops all work and "
         "flags the issue. Nothing is deleted."),
        ("[?]", "#3b82f6", "The browser didn't open",
         "Double-click the desktop icon again. If it still won't open, "
         "type <font name=\"Courier\">http://127.0.0.1:8788/</font> "
         "into your browser."),
        ("[>]", "#6b7280", "The app says it is already running",
         "That's fine. Open your browser and go to "
         "<font name=\"Courier\">http://127.0.0.1:8788/</font>"),
        ("[o]", "#6b7280", "A button is grey and won't click",
         "A required field is missing. For registration buttons, scroll "
         "down inside the form — some fields may be below the visible "
         "area. The footer names missing fields."),
        ("[P]", "#3b82f6", "Reading an old handoff",
         "Click <b>Packages</b> in the left panel, pick a package, then "
         "click <b>Inspect package</b>. Read-only — no files are changed."),
        ("[W]", WARN_COLOR, "Never enter passwords into PANDA",
         "PANDA stores names and email addresses only. Never type "
         "passwords, API keys, or tokens."),
    ]
    for badge, color, title, detail in issues:
        story.append(trouble_card(badge, color, title, detail, USABLE_W))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ============== PAGE 7 — Quick Reference ==============
    story.append(Paragraph("Quick Reference", h1))
    story.append(Spacer(1, 4))

    qref_data = [
        ["Task", "What to do", "Where"],
        ["Open the app", "Double-click PANDA Collaborator on the Desktop", "Desktop"],
        ["App won't open", "Go to http://127.0.0.1:8788/ in your browser", "Browser"],
        ["Switch to Darrin", "Click Handover in User 1 card, then check name at top", "Hub"],
        ["Switch to Pam", "Click Handover in User 2 card, then check name at top", "Hub"],
        ["Start working", "Click Start Session / Start Work", "Hub"],
        ["Finish working", "Click End Session / Handoff, then Create safe handoff", "Hub"],
        ["Something is wrong", "Click Emergency Pause (red button)", "Hub"],
        ["Read old handoffs", "Click Packages, pick one, click Inspect package", "Hub left panel"],
        ["App already running", "Open browser, go to http://127.0.0.1:8788/", "Browser"],
    ]
    qref = Table(qref_data, colWidths=[100, USABLE_W - 100 - 90, 90])
    qref.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(qref)
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "PANDA Collaborator · Setup & Daily Use Guide · Darrin and Pam · May 2026",
        foot))

    doc.build(story)
    return 0


if __name__ == "__main__":
    build_illustrations()
    rc = build_pdf()
    print(f"[build] PDF written: {OUT_PDF} (rc={rc})")
