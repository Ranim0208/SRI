@echo off
REM ============================================================================
REM Script d'Installation et Exécution Phase 1 - Windows
REM Système de Recherche d'Information - ISAMM 2025-2026
REM ============================================================================

setlocal enabledelayedexpansion

REM Couleurs (simples pour Windows)
cls

echo.
echo ==================================================================
echo         INSTALLATION PHASE 1 - WINDOWS
echo ==================================================================
echo.

REM ============================================================================
REM VERIFICATIONS PREALABLES
REM ============================================================================

echo [ETAPE 1/4] Verification des prerequis...
echo.

REM Verifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python 3 n'est pas installe!
    echo Veuillez telecharger Python 3.8+ depuis https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo [OK] Python %python_version% trouve

REM Verifier pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] pip n'est pas installe!
    exit /b 1
)

echo [OK] pip trouve
echo.

REM ============================================================================
REM INSTALLATION DES DEPENDANCES
REM ============================================================================

echo [ETAPE 2/4] Installation des dependances Python...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [ERREUR] Erreur lors de l'installation des packages
        pause
        exit /b 1
    )
    echo [OK] Packages installes
) else (
    echo [ERREUR] Fichier requirements.txt non trouve!
    pause
    exit /b 1
)

echo.

REM ============================================================================
REM INSTALLATION DE PLAYWRIGHT
REM ============================================================================

echo [ETAPE 3/4] Installation des navigateurs Playwright...
echo.

python -m playwright install chromium --with-deps
if %errorlevel% neq 0 (
    echo [AVERTISSEMENT] Erreur lors de l'installation de Playwright
    echo Poursuivez manuellement si necessaire
)

echo [OK] Playwright configure
echo.

REM ============================================================================
REM VERIFICATION DE LA STRUCTURE
REM ============================================================================

echo [ETAPE 4/4] Verification de la structure des fichiers...
echo.

set files=phase1_collector.py phase1_validator.py phase1_converter.py config.py

for %%F in (%files%) do (
    if exist "%%F" (
        echo [OK] %%F trouve
    ) else (
        echo [AVERTISSEMENT] %%F manquant
    )
)

echo.

REM ============================================================================
REM MENU D'EXECUTION
REM ============================================================================

:menu
cls
echo ==================================================================
echo         MENU D'EXECUTION - PHASE 1
echo ==================================================================
echo.
echo Choisissez une action:
echo.
echo 1. Lancer la collecte de tweets (recommande)
echo 2. Valider les donnees existantes
echo 3. Convertir et exporter les formats
echo 4. Afficher la configuration
echo 5. Creer une exportation complete
echo 6. Executer l'ensemble (collecte + validation + export)
echo 0. Quitter
echo.

set /p choice="Entrez votre choix (0-6): "

if "%choice%"=="1" goto collect
if "%choice%"=="2" goto validate
if "%choice%"=="3" goto convert
if "%choice%"=="4" goto config
if "%choice%"=="5" goto export
if "%choice%"=="6" goto full
if "%choice%"=="0" goto end
echo Choix invalide
timeout /t 2
goto menu

REM ============================================================================
REM ACTIONS
REM ============================================================================

:collect
cls
echo ==================================================================
echo         LANCEMENT DE LA COLLECTE
echo ==================================================================
echo.
python phase1_collector.py
pause
goto menu

:validate
cls
echo ==================================================================
echo         VALIDATION DES DONNEES
echo ==================================================================
echo.
python phase1_validator.py
pause
goto menu

:convert
cls
echo ==================================================================
echo         CONVERSION DES FORMATS
echo ==================================================================
echo.
python phase1_converter.py
pause
goto menu

:config
cls
echo ==================================================================
echo         CONFIGURATION ACTUELLE
echo ==================================================================
echo.
python -c "from config import print_config; print_config()"
pause
goto menu

:export
cls
echo ==================================================================
echo         CREATION D'UNE EXPORTATION COMPLETE
echo ==================================================================
echo.
python phase1_converter.py
pause
goto menu

:full
cls
echo ==================================================================
echo         EXECUTION COMPLETE
echo ==================================================================
echo.

echo [1/3] Collecte de tweets...
python phase1_collector.py
if %errorlevel% neq 0 (
    echo [ERREUR] Erreur lors de la collecte
    pause
    goto menu
)

echo.
echo [2/3] Validation des donnees...
python phase1_validator.py
if %errorlevel% neq 0 (
    echo [ERREUR] Erreur lors de la validation
    pause
    goto menu
)

echo.
echo [3/3] Export des formats...
python phase1_converter.py
if %errorlevel% neq 0 (
    echo [ERREUR] Erreur lors de l'export
    pause
    goto menu
)

echo.
echo ==================================================================
echo         EXECUTION COMPLETE REUSSIE!
echo ==================================================================
echo.
echo Les fichiers sont disponibles dans le dossier 'phase1_output\'
echo.
pause
goto menu

:end
echo.
echo Au revoir!
echo.
exit /b 0
