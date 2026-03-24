import pandas as pd
from weasyprint import HTML
from pypdf import PdfWriter
import os
from string import Template
from tqdm import tqdm  # <-- Barre de progression
import datetime

# Fichiers
csv_file = "Eleves.csv"
template_file = "template-date.html"
pdf_file = "eleves.pdf"

# Charger le CSV
df = pd.read_csv(csv_file, sep=";", encoding="utf-16")

df = df.rename(columns={
    'prénom': 'prenom',
    'mot de passe': 'mot_de_passe',
    'classe(s)': 'classe'
})

df = df[['nom', 'prenom', 'classe', 'identifiant', 'mot_de_passe']]



# Charger le template HTML
with open(template_file, "r", encoding="utf-8") as f:
    html_template = Template(f.read())

# Image absolue (QR code par ex.)
image_path = os.path.abspath("lycee-4.0-IJYE2-qr-code.png")

# Writer final
writer = PdfWriter()

# Taille des blocs
chunk_size = 200

# Boucle avec barre de progression
for i in tqdm(range(0, len(df), chunk_size), desc="Génération PDF", unit="chunk"):
    html_content = ""
    for row in df.iloc[i:i+chunk_size].itertuples(index=False):
        # Vérifier si le mot de passe est vide ou NaN
        mot_de_passe = row.mot_de_passe if pd.notna(row.mot_de_passe) and str(row.mot_de_passe).strip() != "" else "Mot de passe personnalisé"

        html_content += html_template.substitute(
            nom=row.nom,
            prenom=row.prenom,
            classe=row.classe,
            identifiant=row.identifiant,
            mot_de_passe=mot_de_passe,
            image_path=image_path,
            date=datetime.datetime.now().strftime("%d/%m/%Y")
        )

    # PDF temporaire
    tmp_file = f"tmp_{i}.pdf"
    HTML(string=html_content).write_pdf(tmp_file)

    # Fusionner dans le PDF final
    writer.append(tmp_file)

    # Supprimer le fichier temporaire
    os.remove(tmp_file)

# Sauvegarder le PDF complet
with open(pdf_file, "wb") as f:
    writer.write(f)

print(f"✅ PDF fusionné : {pdf_file}")
