#!/bin/bash
# Script de lancement pour QCompress
# Lance le backend FastAPI et le frontend Next.js
# Installe automatiquement les dépendances si nécessaire

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}🧠 QCompress - Démarrage...${NC}"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    echo -e "${YELLOW}   Installez Python depuis https://www.python.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python trouvé: $(python3 --version)${NC}"

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    echo -e "${YELLOW}   Installez Node.js depuis https://nodejs.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js trouvé: $(node --version)${NC}"

echo ""
echo -e "${YELLOW}📦 Vérification et installation des dépendances...${NC}"
echo ""

# Fonction pour vérifier si un module Python est installé
check_python_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Vérifier et installer les dépendances Python
echo -e "${CYAN}🐍 Vérification des dépendances Python...${NC}"
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  backend/requirements.txt non trouvé${NC}"
    echo -e "${RED}   Le backend ne pourra pas démarrer${NC}"
else
    # Vérifier si les modules principaux sont installés
    modules_to_check=("fastapi" "uvicorn" "torch" "transformers")
    missing_modules=()
    
    for module in "${modules_to_check[@]}"; do
        if ! check_python_module "$module"; then
            missing_modules+=("$module")
        fi
    done
    
    if [ ${#missing_modules[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Modules Python manquants détectés${NC}"
        echo -e "${YELLOW}   Installation des dépendances Python...${NC}"
        
        # Vérifier si pip est disponible
        if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
            echo -e "${RED}❌ pip n'est pas disponible${NC}"
            echo -e "${YELLOW}   Essayez: python3 -m ensurepip --upgrade${NC}"
            exit 1
        fi
        
        # Utiliser pip3 ou pip selon ce qui est disponible
        PIP_CMD="pip3"
        if ! command -v pip3 &> /dev/null; then
            PIP_CMD="pip"
        fi
        
        echo -e "${GRAY}   Utilisation de: $($PIP_CMD --version)${NC}"
        
        # Installer les dépendances
        echo -e "${GRAY}   Installation en cours (cela peut prendre plusieurs minutes)...${NC}"
        if $PIP_CMD install -r backend/requirements.txt; then
            echo -e "${GREEN}✅ Dépendances Python installées avec succès${NC}"
        else
            echo -e "${RED}❌ Échec de l'installation des dépendances Python${NC}"
            echo -e "${YELLOW}   Essayez d'installer manuellement: pip install -r backend/requirements.txt${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Dépendances Python déjà installées${NC}"
    fi
fi

echo ""

# Vérifier et installer les dépendances Node.js
echo -e "${CYAN}📦 Vérification des dépendances Node.js...${NC}"
if [ ! -f "frontend/package.json" ]; then
    echo -e "${YELLOW}⚠️  frontend/package.json non trouvé${NC}"
    echo -e "${RED}   Le frontend ne pourra pas démarrer${NC}"
else
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules non trouvé dans frontend/${NC}"
        echo -e "${YELLOW}   Installation des dépendances Node.js...${NC}"
        
        # Vérifier si npm est disponible
        if ! command -v npm &> /dev/null; then
            echo -e "${RED}❌ npm n'est pas disponible${NC}"
            exit 1
        fi
        
        echo -e "${GRAY}   Utilisation de npm: $(npm --version)${NC}"
        
        # Installer les dépendances
        echo -e "${GRAY}   Installation en cours (cela peut prendre plusieurs minutes)...${NC}"
        cd frontend
        if npm install; then
            echo -e "${GREEN}✅ Dépendances Node.js installées avec succès${NC}"
        else
            echo -e "${RED}❌ Échec de l'installation des dépendances Node.js${NC}"
            echo -e "${YELLOW}   Essayez d'installer manuellement: cd frontend && npm install${NC}"
            cd ..
            exit 1
        fi
        cd ..
    else
        echo -e "${GREEN}✅ Dépendances Node.js déjà installées${NC}"
    fi
fi

echo ""
echo -e "${CYAN}🚀 Démarrage des services...${NC}"
echo ""

# Fonction pour vérifier si un port est utilisé
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port > /dev/null 2>&1
    elif command -v netstat &> /dev/null; then
        netstat -an | grep -q ":$port.*LISTEN"
    elif command -v ss &> /dev/null; then
        ss -lnt | grep -q ":$port"
    else
        # Si aucun outil n'est disponible, on suppose que le port est libre
        return 1
    fi
}

# Fonction pour libérer un port
free_port() {
    local port=$1
    local pid
    
    if command -v lsof &> /dev/null; then
        pid=$(lsof -ti :$port)
    elif command -v netstat &> /dev/null; then
        pid=$(netstat -tlnp 2>/dev/null | grep ":$port" | awk '{print $7}' | cut -d'/' -f1 | head -n1)
    elif command -v ss &> /dev/null; then
        pid=$(ss -lntp 2>/dev/null | grep ":$port" | grep -oP 'pid=\K[0-9]+' | head -n1)
    fi
    
    if [ ! -z "$pid" ] && [ "$pid" != "-" ]; then
        echo -e "${YELLOW}⚠️  Port $port utilisé par le processus PID: $pid${NC}"
        echo -e "${YELLOW}   Arrêt du processus...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}✅ Port $port libéré${NC}"
    fi
}

# Vérifier et libérer le port 8000 (backend)
if check_port 8000; then
    echo -e "${YELLOW}🔍 Vérification du port 8000...${NC}"
    free_port 8000
fi

# Vérifier et libérer le port 3000 (frontend)
if check_port 3000; then
    echo -e "${YELLOW}🔍 Vérification du port 3000...${NC}"
    free_port 3000
fi

# Variables pour stocker les PIDs
BACKEND_PID=""
FRONTEND_PID=""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
    fi
    # Nettoyer les processus enfants
    pkill -f "uvicorn main:app" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    echo -e "${GREEN}✅ Services arrêtés${NC}"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Démarrer le backend
if [ -f "backend/main.py" ]; then
    echo -e "${YELLOW}🔧 Démarrage du backend FastAPI...${NC}"
cd backend
    python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 3
    
    # Vérifier si le backend a démarré
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Le backend n'a pas pu démarrer${NC}"
        echo -e "${YELLOW}   Vérifiez les logs dans backend.log${NC}"
        echo -e "${YELLOW}   Assurez-vous que toutes les dépendances sont installées${NC}"
    else
        # Vérifier que le port 8000 est bien en écoute
        max_retries=10
        retry_count=0
        backend_ready=false
        
        while [ $retry_count -lt $max_retries ] && [ "$backend_ready" = false ]; do
            sleep 1
            if check_port 8000; then
                backend_ready=true
                echo -e "${GREEN}✅ Backend démarré sur http://localhost:8000${NC}"
            fi
            retry_count=$((retry_count + 1))
        done
        
        if [ "$backend_ready" = false ]; then
            echo -e "${YELLOW}⚠️  Le backend n'écoute pas encore sur le port 8000 (tentative $retry_count/$max_retries)${NC}"
            echo -e "${GRAY}   Il devrait démarrer sous peu...${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  backend/main.py non trouvé, le backend ne sera pas démarré${NC}"
fi

# Démarrer le frontend
if [ -f "frontend/package.json" ]; then
    echo -e "${YELLOW}🎨 Démarrage du frontend Next.js...${NC}"
cd frontend
    npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 5
    
    # Vérifier que le frontend démarre
    max_retries=10
    retry_count=0
    frontend_ready=false
    
    while [ $retry_count -lt $max_retries ] && [ "$frontend_ready" = false ]; do
        sleep 1
        if check_port 3000; then
            frontend_ready=true
            echo -e "${GREEN}✅ Frontend démarré sur http://localhost:3000${NC}"
        fi
        retry_count=$((retry_count + 1))
    done
    
    if [ "$frontend_ready" = false ]; then
        echo -e "${YELLOW}⚠️  Le frontend n'écoute pas encore sur le port 3000 (tentative $retry_count/$max_retries)${NC}"
        echo -e "${GRAY}   Il devrait démarrer sous peu...${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  frontend/package.json non trouvé, le frontend ne sera pas démarré${NC}"
fi

echo ""
echo -e "${GREEN}✅ Services démarrés!${NC}"
echo ""
echo -e "${CYAN}📊 Accès aux services:${NC}"
echo -e "   Frontend:  http://localhost:3000"
echo -e "   Backend:   http://localhost:8000"
echo -e "   API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 Appuyez sur Ctrl+C pour arrêter tous les services${NC}"
echo -e "${GRAY}   Logs backend: tail -f backend.log${NC}"
echo -e "${GRAY}   Logs frontend: tail -f frontend.log${NC}"
echo ""

# Attendre que les processus se terminent
wait
