# Installation sur Windows

## Étape 0 : Configuration Google Cloud Console (Gmail API)

Avant de commencer, vous devez créer un projet Google Cloud et obtenir les identifiants pour accéder à Gmail.

### 1. Créer un projet Google Cloud

1. Aller sur https://console.cloud.google.com/
2. Cliquer sur **Sélectionner un projet** → **Nouveau projet**
3. Donner un nom au projet (ex: "Vinted Printer")
4. Cliquer sur **Créer**

### 2. Activer Gmail API

1. Dans le menu de gauche : **API et services** → **Bibliothèque**
2. Rechercher **"Gmail API"**
3. Cliquer sur **Gmail API**
4. Cliquer sur **Activer**

### 3. Créer les identifiants OAuth 2.0

1. Dans le menu de gauche : **API et services** → **Identifiants**
2. Cliquer sur **+ Créer des identifiants** → **ID client OAuth**
3. Si demandé, configurer l'écran de consentement OAuth :
   - Type d'application : **Externe**
   - Nom de l'application : "Vinted Printer"
   - E-mail d'assistance utilisateur : votre email
   - Cliquer sur **Enregistrer et continuer**
   - Utilisateurs test : ajouter votre adresse Gmail
   - Cliquer sur **Enregistrer et continuer**
4. Retourner dans **Identifiants** → **+ Créer des identifiants** → **ID client OAuth**
5. Type d'application : **Application de bureau**
6. Nom : "Vinted Printer key"
7. Cliquer sur **Créer**
8. **Télécharger le JSON** et le renommer en `credentials.json`
9. **URI de redirection autorisés** - Cliquer sur **+ Ajouter un URI**
   * Entrer : `http://localhost:8080/`
10. Placer le fichier `credentials.json` dans le dossier du projet

### 4. Ajouter votre compte Gmail en utilisateur test

1. Dans **API et services** → **Écran de consentement OAuth**
2. Onglet **Audience**
3. Section **Utilisateurs test** → **+ Ajouter des utilisateurs**
4. Ajouter votre adresse Gmail
5. Cliquer sur **Enregistrer**

**Note :** Votre application restera en mode "Test" ce qui est suffisant pour un usage personnel. Vous pourrez l'utiliser avec votre compte Gmail sans limitation.

## Étape 1 : Installer Python

1. Télécharger **Python 3.12** (pas 3.13) depuis https://www.python.org/downloads/
   - Ou utilisez ce lien direct : https://www.python.org/downloads/release/python-3120/
2. **⚠️ Important : Cocher "Add Python to PATH"** pendant l'installation
3. Installer Python

**Note :** Python 3.13 n'est pas encore supporté par toutes les bibliothèques. Utilisez Python 3.12.

## Étape 2 : Installer les dépendances

1. Ouvrir un terminal (PowerShell ou CMD) dans le dossier du projet
2. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

## Étape 3 : Installer SumatraPDF (pour l'impression automatique)

1. Télécharger **SumatraPDF** : https://www.sumatrapdfreader.org/download-free-pdf-viewer
2. Installer SumatraPDF (gratuit et léger)

**Note :** SumatraPDF est le meilleur outil pour l'impression automatique de PDFs. Si vous ne l'installez pas, le programme essaiera d'utiliser Adobe Reader ou la méthode par défaut de Windows (moins fiable).

## Étape 4 : Configuration

1. Créer un label dans gmail en allant dans paramètres, voir tous les paramètres, Libellés, Nouveau Libellé, puis en remplissant de cette façon par exemple

   ![1759350881950](image/README/1759350881950.png)
   (UPADTE (09/01/2026) : Vinted a changé son adresse d'expédition pour noreply@vinted.fr retirez bien le - entre no et reply)
3. Créer/éditer le fichier `.env` dans le dossier du projet :

   ```
   GMAIL_LABEL=Votre_Label        # nom du label bordereaux vinted
   CHECK_INTERVAL=90              # intervalles de scan
   PRINTER_NAME=Votre_Imprimante  # nom de l'imprimante
   WORK_START_HOUR=8              # heure de début de scan
   WORK_END_HOUR=22               # heure de fin de scan
   LOG_LEVEL=INFO                 # niveau de logs
   ```
4. S'assurer que le fichier `credentials.json` est présent (fichier Google API)

## Étape 5 : Lancer le programme

Démarrez Powershell en tant qu'administrateur naviguez vers le dossier du projet et lancez :

```
python main.py
```

**Note :** La première fois, il vous demandera de vous connecter à Google via le navigateur pour autoriser l'accès Gmail.

Vous pouvez laisser la fenêtre ouverte et le programme tourner. Vous pouvez configurer votre pc portable pour fonctionner meme si fermé en lançant Powershell en mode administrateur et en collant ces commandes :

```powershell
# 1. Ne rien faire quand le couvercle est fermé (sur secteur)
powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0

# 2. Ne rien faire quand le couvercle est fermé (sur batterie)
powercfg /setdcvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0

# 3. Désactiver la mise en veille automatique (sur secteur)
powercfg /change standby-timeout-ac 0

# 4. Désactiver la mise en veille automatique (sur batterie)
powercfg /change standby-timeout-dc 0

# 5. Désactiver la mise en veille de l'écran (sur secteur)
powercfg /change monitor-timeout-ac 0

# 6. Désactiver la mise en veille de l'écran (sur batterie)
powercfg /change monitor-timeout-dc 0

# 7. Désactiver l'hibernation
powercfg /hibernate off

# 8. Appliquer les modifications
powercfg /setactive SCHEME_CURRENT
```

Une fois ces commandes validées, vous pourrez fermer votre ordinateur portable branché à l'imprimante et sur secteur et le programme imprimera vos bordereaux automatiquement dans la journée !
