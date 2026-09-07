# publi-password
Script de publipostage pour les identifiants des élèves du lycée Loritz

Les données sont récupérées depuis un fichier CSV extrait à partir d'ACL et intégrées dans des templates HTML. Les fiches sont ensuite converties en PDF puis fusionnées en un seul fichier.

## Prérequis

* Python **3.10 ou supérieur**
* `pip`
* Sous Linux : quelques dépendances système nécessaires à **WeasyPrint**

## Installation

### Windows

Cloner ou télécharger le projet, puis ouvrir un terminal dans son dossier :

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install pandas pypdf tqdm weasyprint
```

Si `weasyprint` rencontre des problèmes liés à ses dépendances natives, consulter la documentation officielle de WeasyPrint pour l'installation adaptée à votre version de Windows.

### Linux (Debian / Ubuntu)

Installer Python et les dépendances système de WeasyPrint :

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip \
    libpango-1.0-0 libpangoft2-1.0-0
```

Créer ensuite l'environnement virtuel et installer les dépendances Python :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pandas pypdf tqdm weasyprint
```

## Fichier CSV

Le fichier `Eleves.csv` doit être encodé en **UTF-16** et utiliser `;` comme séparateur.

Les colonnes attendues sont :

```text
nom
prénom
classe(s)
identifiant
mot de passe
```

Le script convertit automatiquement les trois colonnes suivantes :

* `prénom` → `prenom`
* `classe(s)` → `classe`
* `mot de passe` → `mot_de_passe`

Les autres colonnes présentes dans le CSV sont ignorées.

## Utilisation

### Versions <= 8

Une fois l'environnement virtuel activé :

```bash
python publi-html-v8.py
```

Sous Linux, si le fichier est exécutable :

```bash
./publi-html-v8.py
```
### Versions >= 9

Une fois l'environnement virtuel activé :

```bash
python publi-html-v9.py Eleves.csv eleves.pdf
```

Sous Linux, si le fichier est exécutable :

```bash
./publi-publi-html-v9.py Eleves.csv eleves.pdf
```

## Personnalisation

Les principaux paramètres se trouvent au début du script :

```python
CSV_FILE = "Eleves.csv"
OUTPUT_FILE = "eleve.pdf"

STUDENT_TEMPLATE_FILE = "template-date.html"
CLASS_TEMPLATE_FILE = "intercalaire.html"

QR_CODE_FILE = "lycee-4.0-IJYE2-qr-code.png"
TMP_DIR = "tmp"
```

Ils peuvent être modifiés pour adapter les noms de fichiers ou le dossier de sortie.


### Templates HTML

#### `template-date.html`

Template utilisé pour générer chaque fiche élève.

Les variables suivantes peuvent être utilisées :

```text
$nom
$prenom
$classe
$identifiant
$mot_de_passe
$image_path
$date
```

#### `intercalaire.html`

Template utilisé pour générer l'intercalaire d'une classe.

Variable disponible :

```text
$classe
```
