"""Génère une étiquette QR code noir et blanc pur (1 bit) pour imprimante thermique.

Usage : python outils/etiquette_qr.py <dossier-notice> "<Nom de la figurine>"
Exemple : python outils/etiquette_qr.py fantome-chien "Le Fantôme et son chien"

Sortie : etiquettes/<dossier-notice>.png
Largeur 384 px = 48 mm à 203 dpi (rouleaux de 57/58 mm des mini-imprimantes thermiques).
"""
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "https://drpsykoz.github.io/notices_impressions_3d/"
WIDTH = 384
DPI = 203
MARGIN = 16
FONTS = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=f) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def main(slug, name):
    url = BASE_URL + slug + "/"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0, box_size=1)
    qr.add_data(url)
    qr.make(fit=True)
    modules = qr.modules_count
    box = (WIDTH - 2 * MARGIN - 40) // modules  # taille entière d'un module = netteté parfaite
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")
    qr_img = qr_img.resize((modules * box, modules * box), Image.NEAREST)

    f_top = font("consolab.ttf", 18)
    f_name = font("segoeuib.ttf", 28)
    f_sub = font("segoeui.ttf", 19)

    probe = ImageDraw.Draw(Image.new("1", (1, 1)))
    name_lines = wrap(probe, name, f_name, WIDTH - 2 * MARGIN)

    h = MARGIN + 22 + 14 + qr_img.height + 18 + len(name_lines) * 34 + 6 + 26 + MARGIN + 8
    img = Image.new("1", (WIDTH, h), 1)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # pas d'anticrénelage : que du noir et du blanc

    def center(text, y, f):
        d.text(((WIDTH - d.textlength(text, font=f)) / 2, y), text, font=f, fill=0)

    y = MARGIN
    center("NOTICE DE MONTAGE", y, f_top)
    y += 22 + 14
    img.paste(qr_img, ((WIDTH - qr_img.width) // 2, y))
    y += qr_img.height + 18
    for line in name_lines:
        center(line, y, f_name)
        y += 34
    y += 6
    center("Scanne-moi pour monter ta figurine", y, f_sub)

    out = Path(__file__).resolve().parent.parent / "etiquettes" / f"{slug}.png"
    out.parent.mkdir(exist_ok=True)
    img.save(out, dpi=(DPI, DPI))
    print(f"{out}  ({img.width}x{img.height}px, QR {modules} modules x {box}px)  ->  {url}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
