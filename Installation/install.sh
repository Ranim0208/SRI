#!/bin/bash

# ============================================================================
# Script d'Installation et Exécution Phase 1
# Système de Recherche d'Information - ISAMM 2025-2026
# ============================================================================

set -e  # Arrêter si une erreur se produit

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FONCTIONS D'AFFICHAGE
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}===================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================================
# VÉRIFICATIONS PRÉALABLES
# ============================================================================

print_header "VÉRIFICATIONS PRÉALABLES"

# Vérifier Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $python_version trouvé"
else
    print_error "Python 3 n'est pas installé!"
    echo "Veuillez installer Python 3.8 ou supérieur"
    exit 1
fi

# Vérifier pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 trouvé"
else
    print_error "pip3 n'est pas installé!"
    exit 1
fi

# ============================================================================
# INSTALLATION DES DÉPENDANCES
# ============================================================================

print_header "INSTALLATION DES DÉPENDANCES"

if [ -f "requirements.txt" ]; then
    print_info "Installation des packages Python..."
    pip3 install -r requirements.txt --quiet
    print_success "Packages Python installés"
else
    print_error "Fichier requirements.txt non trouvé!"
    exit 1
fi

# ============================================================================
# INSTALLATION DE PLAYWRIGHT
# ============================================================================

print_header "INSTALLATION DE PLAYWRIGHT"

print_info "Installation des navigateurs Playwright..."
python3 -m playwright install chromium --with-deps
print_success "Navigateurs Playwright installés"

# ============================================================================
# VÉRIFICATION DE LA STRUCTURE
# ============================================================================

print_header "VÉRIFICATION DE LA STRUCTURE"

files=("phase1_collector.py" "phase1_validator.py" "phase1_converter.py" "config.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Fichier trouvé: $file"
    else
        print_warning "Fichier manquant: $file"
    fi
done

# ============================================================================
# MENU D'EXÉCUTION
# ============================================================================

print_header "MENU D'EXÉCUTION PHASE 1"

echo "Choisissez une action:"
echo "1. Lancer la collecte de tweets (recommandé)"
echo "2. Valider les données existantes"
echo "3. Convertir et exporter les formats"
echo "4. Afficher la configuration"
echo "5. Créer une exportation complète"
echo "6. Exécuter l'ensemble (collecte + validation + export)"
echo "0. Quitter"
echo ""

read -p "Entrez votre choix (0-6): " choice

case $choice in
    1)
        print_header "LANCEMENT DE LA COLLECTE"
        python3 phase1_collector.py
        ;;
    2)
        print_header "VALIDATION DES DONNÉES"
        if python3 phase1_validator.py; then
            print_success "Validation terminée avec succès"
        else
            print_error "Erreur lors de la validation"
        fi
        ;;
    3)
        print_header "CONVERSION DES FORMATS"
        if python3 phase1_converter.py; then
            print_success "Conversion terminée"
        else
            print_error "Erreur lors de la conversion"
        fi
        ;;
    4)
        print_header "CONFIGURATION"
        python3 -c "from config import print_config; print_config()"
        ;;
    5)
        print_header "CRÉATION D'UNE EXPORTATION COMPLÈTE"
        if python3 phase1_converter.py; then
            print_success "Exportation complète créée"
        else
            print_error "Erreur lors de l'exportation"
        fi
        ;;
    6)
        print_header "EXÉCUTION COMPLÈTE (COLLECTE + VALIDATION + EXPORT)"
        
        echo ""
        print_info "1/3: Collecte de tweets..."
        if python3 phase1_collector.py; then
            print_success "Collecte terminée"
        else
            print_error "Erreur lors de la collecte"
            exit 1
        fi
        
        echo ""
        print_info "2/3: Validation des données..."
        if python3 phase1_validator.py; then
            print_success "Validation réussie"
        else
            print_error "Erreur lors de la validation"
            exit 1
        fi
        
        echo ""
        print_info "3/3: Export des formats..."
        if python3 phase1_converter.py; then
            print_success "Export complété"
        else
            print_error "Erreur lors de l'export"
            exit 1
        fi
        
        echo ""
        print_header "EXÉCUTION COMPLÈTE RÉUSSIE ✅"
        echo "Les fichiers sont disponibles dans le dossier 'phase1_output/'"
        ;;
    0)
        echo "Au revoir!"
        exit 0
        ;;
    *)
        print_error "Choix invalide"
        exit 1
        ;;
esac

# ============================================================================
# AFFICHAGE DU RÉSUMÉ
# ============================================================================

print_header "RÉSUMÉ"

if [ -d "phase1_output" ]; then
    echo ""
    echo "📁 Fichiers générés:"
    for file in phase1_output/*; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            filename=$(basename "$file")
            echo "   $filename ($size)"
        fi
    done
else
    print_info "Le dossier phase1_output n'existe pas encore"
fi

echo ""
print_success "Installation et configuration terminées!"
echo ""
echo "📖 Consultez GUIDE_PHASE1.md pour plus de détails"
echo ""
