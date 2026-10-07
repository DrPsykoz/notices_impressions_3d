# Notices de montage

Notices de montage des figurines imprimées en 3D, publiées sur GitHub Pages :
https://drpsykoz.github.io/notices_impressions_3d/

## Structure

- `index.html` : page d'accueil qui liste les notices
- `assets/notice.css` : style commun à toutes les notices
- `<figurine>/index.html` : notice web (une par dossier), avec ses photos dans `img/` et le PDF
- `etiquettes/` : planches de 2 étiquettes QR code à imprimer (bordereau thermique 100 x 150 mm, noir et blanc pur, 203 dpi)
- `outils/etiquette_qr.py` : génère une planche, ex. `python outils/etiquette_qr.py fantome-chien "Le Fantôme" "et son chien" 04 "~5 min"`

⚠️ Ne jamais renommer le dépôt ni un dossier de figurine : les QR codes imprimés pointent dessus.
