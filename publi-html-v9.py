#!/usr/bin/env python3

import os
import shutil
import datetime
import argparse
from string import Template

import pandas as pd
from pypdf import PdfWriter
from tqdm import tqdm
from weasyprint import HTML


# ============================================================
# CONFIGURATION
# ============================================================

STUDENT_TEMPLATE_FILE = "template-date.html"
CLASS_TEMPLATE_FILE = "intercalaire.html"
QR_CODE_FILE = "lycee-4.0-IJYE2-qr-code.png"
TMP_DIR = "tmp"


# ============================================================
# ARGUMENTS DE LIGNE DE COMMANDE
# ============================================================

parser = argparse.ArgumentParser(
    description="Génère un PDF à partir d'un fichier CSV."
)

parser.add_argument(
    "csv",
    help="Fichier CSV source"
)

parser.add_argument(
    "pdf",
    help="Fichier PDF de sortie"
)

args = parser.parse_args()

CSV_FILE = args.csv
OUTPUT_FILE = args.pdf


# ============================================================
# PRÉPARATION DU DOSSIER TEMPORAIRE
# ============================================================

os.makedirs(TMP_DIR, exist_ok=True)


# ============================================================
# CHEMINS ABSOLUS
# ============================================================

student_template_path = os.path.abspath(STUDENT_TEMPLATE_FILE)
class_template_path = os.path.abspath(CLASS_TEMPLATE_FILE)
qr_code_path = os.path.abspath(QR_CODE_FILE)


# ============================================================
# CHARGEMENT DU CSV
# ============================================================

df = pd.read_csv(
    CSV_FILE,
    sep=";",
    encoding="utf-16"
)


# ============================================================
# RENOMMAGE DES COLONNES
# ============================================================

df = df.rename(columns={
    "prénom": "prenom",
    "mot de passe": "mot_de_passe",
    "classe(s)": "classe"
})


# ============================================================
# VÉRIFICATION DES COLONNES
# ============================================================

required_columns = [
    "nom",
    "prenom",
    "classe",
    "identifiant",
    "mot_de_passe"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Colonnes manquantes dans le CSV : "
        + ", ".join(missing_columns)
    )


df = df[required_columns]


# ============================================================
# TRI PAR CLASSE
# ============================================================

df = df.sort_values(
    by="classe",
    kind="stable"
).reset_index(drop=True)


# ============================================================
# CHARGEMENT DES TEMPLATES
# ============================================================

with open(
    STUDENT_TEMPLATE_FILE,
    "r",
    encoding="utf-8"
) as file:
    student_template = Template(file.read())


with open(
    CLASS_TEMPLATE_FILE,
    "r",
    encoding="utf-8"
) as file:
    class_template = Template(file.read())


# ============================================================
# DATE DE GÉNÉRATION
# ============================================================

generation_date = datetime.datetime.now().strftime(
    "%d/%m/%Y"
)


# ============================================================
# FONCTION : GÉNÉRER UNE FICHE UTILISATEUR
# ============================================================

def generate_student_pdf(row, output_path):

    if (
        pd.notna(row["mot_de_passe"])
        and str(row["mot_de_passe"]).strip() != ""
    ):
        password = str(row["mot_de_passe"])
    else:
        password = "Mot de passe personnalisé par l'utilisateur"

    html = student_template.substitute(
        nom=row["nom"],
        prenom=row["prenom"],
        classe=row["classe"],
        identifiant=row["identifiant"],
        mot_de_passe=password,
        image_path=qr_code_path,
        date=generation_date
    )

    HTML(
        string=html,
        base_url=os.path.dirname(student_template_path)
    ).write_pdf(output_path)


# ============================================================
# FONCTION : GÉNÉRER UN INTERCALAIRE
# ============================================================

def generate_class_separator(classe, output_path):

    html = class_template.substitute(
        classe=classe
    )

    HTML(
        string=html,
        base_url=os.path.dirname(class_template_path)
    ).write_pdf(output_path)


# ============================================================
# LISTE DES FICHIERS À FUSIONNER
# ============================================================

temporary_files = []


# ============================================================
# CLASSE PRÉCÉDENTE
# ============================================================

last_class = None


# ============================================================
# GÉNÉRATION
# ============================================================

for index, row in tqdm(
    df.iterrows(),
    total=len(df),
    desc="Génération des PDF",
    unit="utilisateurs"
):

    # --------------------------------------------------------
    # Récupération de la classe
    # --------------------------------------------------------

    if pd.notna(row["classe"]):
        classe = str(row["classe"]).strip()
    else:
        classe = ""


    # ========================================================
    # INTERCALAIRE
    # ========================================================

    if classe != last_class:

        separator_path = os.path.join(
            TMP_DIR,
            f"{index:05d}_intercalaire.pdf"
        )

        generate_class_separator(
            classe,
            separator_path
        )

        temporary_files.append(
            separator_path
        )

        last_class = classe


    # ========================================================
    # FICHE ÉLÈVE
    # ========================================================

    student_path = os.path.join(
        TMP_DIR,
        f"{index:05d}_fiche.pdf"
    )

    generate_student_pdf(
        row,
        student_path
    )

    temporary_files.append(
        student_path
    )


# ============================================================
# FUSION DES PDF
# ============================================================

print()
print("Fusion des PDF...")

writer = PdfWriter()

for pdf_path in temporary_files:
    writer.append(pdf_path)


# ============================================================
# ÉCRITURE DU PDF FINAL
# ============================================================

with open(
    OUTPUT_FILE,
    "wb"
) as file:
    writer.write(file)


# ============================================================
# NETTOYAGE DU DOSSIER TMP
# ============================================================

print("Nettoyage des fichiers temporaires...")

for pdf_path in temporary_files:

    if os.path.exists(pdf_path):
        os.remove(pdf_path)


# ============================================================
# RÉSULTAT
# ============================================================

print()
print("========================================")
print("Génération terminée")
print("========================================")
print(f"Élèves traités : {len(df)}")
print(f"PDF final      : {OUTPUT_FILE}")
print(f"Dossier tmp    : {TMP_DIR}/")