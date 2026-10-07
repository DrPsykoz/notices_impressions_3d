"""Génère une planche de 2 étiquettes QR code, noir et blanc pur (1 bit), pour imprimante thermique.

Usage :
  python outils/etiquette_qr.py <dossier-notice> "<Titre ligne 1>" "<Titre ligne 2>" [pièces] [durée]
Exemple :
  python outils/etiquette_qr.py fantome-chien "Le Fantôme" "et son chien" 04 "~5 min"

Sortie : etiquettes/<dossier-notice>.png
Format : bordereau 100 x 150 mm à 203 dpi (800 x 1200 px), 2 étiquettes de 100 x 75 mm.
La mise en page est faite en HTML (rendue par Edge) puis seuillée en 1 bit ; le QR code est
dessiné à part, aligné au pixel près, pour rester parfaitement net.
"""
import html
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw

BASE_URL = "https://drpsykoz.github.io/notices_impressions_3d/"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
W, H = 800, 1200          # 100 x 150 mm à 203 dpi
HALF = H // 2
DPI = 203
SS = 3                    # sur-échantillonnage du rendu HTML
QR_X, QR_Y, QR_BOX = 40, 112, 296   # zone du QR dans chaque étiquette (px)

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@500;700&display=block" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: {W}px; height: {H}px; background: #fff; color: #000; overflow: hidden; }}
  body {{ font-family: Inter, "Segoe UI", sans-serif; }}
  .mono {{ font-family: "JetBrains Mono", Consolas, monospace; text-transform: uppercase; letter-spacing: .06em; }}
  .lab {{ position: absolute; left: 0; width: {W}px; height: {HALF}px; }}
  .bar {{ position: absolute; left: 40px; right: 40px; top: 34px; display: flex; justify-content: space-between; font-size: 17px; font-weight: 500; }}
  .bar .dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #000; margin-right: 10px; vertical-align: 1px; }}
  .rule {{ position: absolute; left: 40px; right: 40px; top: 76px; border-top: 3px solid #000; }}
  .right {{ position: absolute; left: 372px; right: 40px; top: 104px; }}
  h1 {{ font-size: 50px; line-height: 1.02; letter-spacing: -.035em; font-weight: 700; }}
  h1 span {{ font-weight: 400; }}
  .specs {{ margin-top: 22px; font-size: 17px; font-weight: 500; }}
  .specs div {{ display: flex; justify-content: space-between; padding: 9px 0; border-top: 2px solid #000; }}
  .specs div:last-child {{ border-bottom: 2px solid #000; }}
  .specs b {{ font-weight: 700; }}
  .cta {{ position: absolute; left: 40px; right: 40px; top: 440px; height: 104px; background: #000; color: #fff; border-radius: 14px; padding: 0 30px; display: flex; align-items: center; justify-content: space-between; }}
  .cta strong {{ display: block; font-size: 30px; letter-spacing: -.02em; }}
  .cta small {{ display: block; font-size: 16px; margin-top: 4px; }}
  .cta .arrow {{ font-size: 46px; font-weight: 400; }}
  .cut {{ position: absolute; left: 0; right: 0; top: {HALF}px; border-top: 2px dashed #000; }}
  .cut span {{ position: absolute; left: 24px; top: -14px; background: #fff; padding: 0 8px; font-size: 18px; }}
</style></head><body>
{labels}
<div class="cut"><span class="mono">✂</span></div>
</body></html>"""

LABEL = """<div class="lab" style="top:{top}px">
  <div class="bar mono"><span><span class="dot"></span>Notice de montage</span><span>Imprimé en 3D</span></div>
  <div class="rule"></div>
  <div class="right">
    <h1>{t1}<br><span>{t2}</span></h1>
    <div class="specs mono">{specs}</div>
  </div>
  <div class="cta">
    <div><strong>Scanne le QR code</strong><small class="mono">Montage étape par étape</small></div>
    <span class="arrow">↖</span>
  </div>
</div>"""


def render_layout(t1, t2, specs):
    rows = "".join(f"<div><span>{html.escape(k)}</span><b>{html.escape(v)}</b></div>" for k, v in specs)
    label = lambda top: LABEL.format(top=top, t1=html.escape(t1), t2=html.escape(t2), specs=rows)
    page = TEMPLATE.format(W=W, H=H, HALF=HALF, labels=label(0) + label(HALF))
    tmp = Path(tempfile.mkdtemp())
    (tmp / "l.html").write_text(page, encoding="utf-8")
    shot = tmp / "l.png"
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={SS}", f"--window-size={W},{H}",
                    "--virtual-time-budget=8000", f"--user-data-dir={tmp / 'prof'}",
                    f"--screenshot={shot}", (tmp / "l.html").as_uri()],
                   check=True, capture_output=True)
    for _ in range(120):  # msedge.exe peut rendre la main avant d'avoir écrit la capture
        if shot.exists() and shot.stat().st_size > 0:
            time.sleep(0.5)
            break
        time.sleep(0.5)
    im = Image.open(shot).convert("L").crop((0, 0, W * SS, H * SS))
    im = im.resize((W, H), Image.LANCZOS)
    return im.point(lambda p: 255 if p > 140 else 0).convert("1")


def render_qr(url):
    """QR à modules arrondis, dessiné en grand puis réduit et seuillé (bords nets, 1 bit)."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    m = qr.modules
    n = len(m)
    px = QR_BOX // n                      # taille entière d'un module à 203 dpi
    S = 8                                 # sur-échantillonnage du dessin
    u = px * S
    big = Image.new("L", (n * u, n * u), 255)
    d = ImageDraw.Draw(big)
    finders = [(0, 0), (0, n - 7), (n - 7, 0)]
    in_finder = lambda r, c: any(fr <= r < fr + 7 and fc <= c < fc + 7 for fr, fc in finders)
    for r in range(n):
        for c in range(n):
            if m[r][c] and not in_finder(r, c):
                g = u * 0.06
                d.rounded_rectangle((c * u + g, r * u + g, (c + 1) * u - g, (r + 1) * u - g), radius=u * 0.32, fill=0)
    for fr, fc in finders:
        x, y = fc * u, fr * u
        d.rounded_rectangle((x, y, x + 7 * u - 1, y + 7 * u - 1), radius=u * 0.6, fill=0)
        d.rounded_rectangle((x + u, y + u, x + 6 * u - 1, y + 6 * u - 1), radius=u * 0.4, fill=255)
        d.rounded_rectangle((x + 2 * u, y + 2 * u, x + 5 * u - 1, y + 5 * u - 1), radius=u * 0.26, fill=0)
    small = big.resize((n * px, n * px), Image.LANCZOS)
    return small.point(lambda p: 255 if p > 128 else 0).convert("1")


def main(slug, t1, t2, pieces="", duree=""):
    url = BASE_URL + slug + "/"
    specs = [(k, v) for k, v in (("Pièces", pieces), ("Durée", duree)) if v]
    img = render_layout(t1, t2, specs)
    qr = render_qr(url)
    off = (QR_BOX - qr.width) // 2
    for top in (0, HALF):
        img.paste(qr, (QR_X + off, top + QR_Y + off))
    out = Path(__file__).resolve().parent.parent / "etiquettes" / f"{slug}.png"
    out.parent.mkdir(exist_ok=True)
    img.save(out, dpi=(DPI, DPI))
    print(f"{out}  ({W}x{H}px = 100x150 mm)  ->  {url}")


if __name__ == "__main__":
    main(*sys.argv[1:])
