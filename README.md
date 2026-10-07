# Notices de montage

Notices de montage des figurines imprimées en 3D, publiées sur GitHub Pages :
https://drpsykoz.github.io/notices_impressions_3d/

## Structure

- `index.html` : page d'accueil qui liste les notices
- `assets/notice.css` : style commun à toutes les notices
- `<figurine>/index.html` : notice web (une par dossier), avec ses photos dans `img/` et le PDF
- `etiquettes/` : étiquettes QR code à imprimer (noir et blanc, 48 mm à 203 dpi)
- `outils/etiquette_qr.py` : génère une étiquette, ex. `python outils/etiquette_qr.py fantome-chien "Le Fantôme et son chien"`

⚠️ Ne jamais renommer le dépôt ni un dossier de figurine : les QR codes imprimés pointent dessus.
