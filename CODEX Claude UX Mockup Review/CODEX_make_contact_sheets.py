from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src = Path(r'C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX rendered screenshots')
out = Path(r'C:\CODEX PG\CODEX Claude UX Mockup Review')
files = sorted([p for p in src.glob('*.png') if p.name[0:2].isdigit()])
font = ImageFont.load_default()

def make_sheet(paths, name, cols=4, thumb_w=340, thumb_h=235, label_h=34, pad=16):
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new('RGB', (cols*(thumb_w+pad)+pad, rows*(thumb_h+label_h+pad)+pad), '#101316')
    draw = ImageDraw.Draw(sheet)
    for i,p in enumerate(paths):
        r,c = divmod(i, cols)
        x = pad + c*(thumb_w+pad)
        y = pad + r*(thumb_h+label_h+pad)
        img = Image.open(p).convert('RGB')
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        bg = Image.new('RGB', (thumb_w, thumb_h), '#20252b')
        bx = (thumb_w-img.width)//2
        by = (thumb_h-img.height)//2
        bg.paste(img, (bx, by))
        sheet.paste(bg, (x, y))
        label = p.stem
        if len(label) > 48:
            label = label[:45] + '...'
        draw.text((x, y+thumb_h+8), label, fill='#dce3ea', font=font)
    out_path = out / name
    sheet.save(out_path, quality=92)
    print(out_path)

make_sheet(files[:16], 'CODEX_recent_mockups_contact_sheet.png')
make_sheet(files[16:], 'CODEX_v4_0_mockups_contact_sheet.png')
make_sheet(files, 'CODEX_all_claude_mockups_contact_sheet.png', cols=4, thumb_w=320, thumb_h=220)
