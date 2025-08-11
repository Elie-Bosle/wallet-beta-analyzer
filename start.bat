@echo off
echo 🚀 Lancement de Beta Portfolio Analyzer...

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)

REM Créer l'environnement virtuel s'il n'existe pas
if not exist ".venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv .venv
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

REM Installer les dépendances
echo 📦 Installation des dépendances...
pip install -r requirements.txt

REM Vérifier et libérer le port si nécessaire
echo 🔍 Vérification des ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    echo ⚠️  Port 8080 occupé, libération en cours...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 2 >nul
)

REM Lancer l'application
echo 🌐 Démarrage du serveur web...
echo 📍 L'application sera disponible sur: http://localhost:8080 (ou port suivant)
echo 🔄 Appuyez sur Ctrl+C pour arrêter le serveur
echo ----------------------------------------

python app.py
pause
