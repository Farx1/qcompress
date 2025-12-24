# Script de lancement pour QCompress
# Lance le backend FastAPI et le frontend Next.js
# Installe automatiquement les dépendances si nécessaire

Write-Host "🧠 QCompress - Démarrage..." -ForegroundColor Cyan
Write-Host ""

# Vérifier que Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "   Installez Python depuis https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Vérifier que Node.js est installé
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js trouvé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "   Installez Node.js depuis https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📦 Vérification et installation des dépendances..." -ForegroundColor Yellow
Write-Host ""

# Fonction pour vérifier si un module Python est installé
function Test-PythonModule {
    param([string]$ModuleName)
    $result = python -c "import $ModuleName" 2>&1
    return $LASTEXITCODE -eq 0
}

# Vérifier et installer les dépendances Python
Write-Host "🐍 Vérification des dépendances Python..." -ForegroundColor Cyan
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "⚠️  backend/requirements.txt non trouvé" -ForegroundColor Yellow
    Write-Host "   Le backend ne pourra pas démarrer" -ForegroundColor Red
} else {
    # Vérifier si les modules principaux sont installés
    $modulesToCheck = @("fastapi", "uvicorn", "torch", "transformers")
    $missingModules = @()
    
    foreach ($module in $modulesToCheck) {
        if (-not (Test-PythonModule -ModuleName $module)) {
            $missingModules += $module
        }
    }
    
    if ($missingModules.Count -gt 0) {
        Write-Host "⚠️  Modules Python manquants détectés" -ForegroundColor Yellow
        Write-Host "   Installation des dépendances Python..." -ForegroundColor Yellow
        
        # Vérifier si pip est disponible
        try {
            $pipVersion = pip --version 2>&1
            Write-Host "   Utilisation de: $pipVersion" -ForegroundColor Gray
        } catch {
            Write-Host "❌ pip n'est pas disponible" -ForegroundColor Red
            Write-Host "   Essayez: python -m ensurepip --upgrade" -ForegroundColor Yellow
            exit 1
        }
        
        # Installer les dépendances
        Write-Host "   Installation en cours (cela peut prendre plusieurs minutes)..." -ForegroundColor Gray
        $installProcess = Start-Process -FilePath "pip" -ArgumentList "install", "-r", "backend\requirements.txt" -WorkingDirectory $PSScriptRoot -Wait -NoNewWindow -PassThru
        
        if ($installProcess.ExitCode -ne 0) {
            Write-Host "❌ Échec de l'installation des dépendances Python" -ForegroundColor Red
            Write-Host "   Code de sortie: $($installProcess.ExitCode)" -ForegroundColor Yellow
            Write-Host "   Essayez d'installer manuellement: pip install -r backend/requirements.txt" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "✅ Dépendances Python installées avec succès" -ForegroundColor Green
    } else {
        Write-Host "✅ Dépendances Python déjà installées" -ForegroundColor Green
    }
}

Write-Host ""

# Vérifier et installer les dépendances Node.js
Write-Host "📦 Vérification des dépendances Node.js..." -ForegroundColor Cyan
if (-not (Test-Path "frontend\package.json")) {
    Write-Host "⚠️  frontend/package.json non trouvé" -ForegroundColor Yellow
    Write-Host "   Le frontend ne pourra pas démarrer" -ForegroundColor Red
} else {
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Host "⚠️  node_modules non trouvé dans frontend/" -ForegroundColor Yellow
        Write-Host "   Installation des dépendances Node.js..." -ForegroundColor Yellow
        
        # Vérifier si npm est disponible
        try {
            $npmVersion = npm --version 2>&1
            Write-Host "   Utilisation de npm: $npmVersion" -ForegroundColor Gray
        } catch {
            Write-Host "❌ npm n'est pas disponible" -ForegroundColor Red
            exit 1
        }
        
        # Installer les dépendances
        Write-Host "   Installation en cours (cela peut prendre plusieurs minutes)..." -ForegroundColor Gray
        $installProcess = Start-Process -FilePath "npm" -ArgumentList "install" -WorkingDirectory "frontend" -Wait -NoNewWindow -PassThru
        
        if ($installProcess.ExitCode -ne 0) {
            Write-Host "❌ Échec de l'installation des dépendances Node.js" -ForegroundColor Red
            Write-Host "   Code de sortie: $($installProcess.ExitCode)" -ForegroundColor Yellow
            Write-Host "   Essayez d'installer manuellement: cd frontend && npm install" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "✅ Dépendances Node.js installées avec succès" -ForegroundColor Green
    } else {
        Write-Host "✅ Dépendances Node.js déjà installées" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🚀 Démarrage des services..." -ForegroundColor Cyan
Write-Host ""

# Fonction pour vérifier si un port est utilisé
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Fonction pour libérer un port
function Free-Port {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.State -eq "Listen") {
            $processId = $conn.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "⚠️  Port $Port utilisé par le processus $($process.Name) (PID: $processId)" -ForegroundColor Yellow
                Write-Host "   Arrêt du processus..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 1
                Write-Host "✅ Port $Port libéré" -ForegroundColor Green
            }
        }
    }
}

# Vérifier et libérer le port 8000 (backend)
if (Test-Port -Port 8000) {
    Write-Host "🔍 Vérification du port 8000..." -ForegroundColor Yellow
    Free-Port -Port 8000
}

# Vérifier et libérer le port 3000 (frontend)
if (Test-Port -Port 3000) {
    Write-Host "🔍 Vérification du port 3000..." -ForegroundColor Yellow
    Free-Port -Port 3000
}

# Fonction pour nettoyer les processus à la sortie
function Cleanup {
    Write-Host ""
    Write-Host "🛑 Arrêt des services..." -ForegroundColor Yellow
    if ($backendProcess) {
        try {
            Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        } catch {
            # Ignorer les erreurs si le processus n'existe plus
        }
    }
    if ($frontendProcess) {
        try {
            Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
        } catch {
            # Ignorer les erreurs si le processus n'existe plus
        }
    }
    Write-Host "✅ Services arrêtés" -ForegroundColor Green
}

# Enregistrer le handler pour Ctrl+C
[Console]::TreatControlCAsInput = $false
Register-ObjectEvent -InputObject ([System.Console]) -EventName CancelKeyPress -Action {
    Cleanup
    exit 0
} | Out-Null

# Démarrer le backend
if (Test-Path "backend\main.py") {
    Write-Host "🔧 Démarrage du backend FastAPI..." -ForegroundColor Yellow
    $backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "backend" -PassThru -NoNewWindow
    Start-Sleep -Seconds 3
    
    # Vérifier si le backend a démarré correctement
    if ($backendProcess.HasExited) {
        Write-Host "❌ Le backend n'a pas pu démarrer (code de sortie: $($backendProcess.ExitCode))" -ForegroundColor Red
        Write-Host "   Vérifiez les logs ci-dessus pour plus de détails" -ForegroundColor Yellow
        Write-Host "   Assurez-vous que toutes les dépendances sont installées" -ForegroundColor Yellow
    } else {
        # Vérifier que le port 8000 est bien en écoute
        $maxRetries = 10
        $retryCount = 0
        $backendReady = $false
        while ($retryCount -lt $maxRetries -and -not $backendReady) {
            Start-Sleep -Seconds 1
            if (Test-Port -Port 8000) {
                $backendReady = $true
                Write-Host "✅ Backend démarré sur http://localhost:8000" -ForegroundColor Green
            }
            $retryCount++
        }
        
        if (-not $backendReady) {
            Write-Host "⚠️  Le backend n'écoute pas encore sur le port 8000 (tentative $retryCount/$maxRetries)" -ForegroundColor Yellow
            Write-Host "   Il devrait démarrer sous peu..." -ForegroundColor Gray
        }
    }
} else {
    Write-Host "⚠️  backend/main.py non trouvé, le backend ne sera pas démarré" -ForegroundColor Yellow
    $backendProcess = $null
}

# Démarrer le frontend
if (Test-Path "frontend\package.json") {
    Write-Host "🎨 Démarrage du frontend Next.js..." -ForegroundColor Yellow
    $frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend" -PassThru -NoNewWindow
    Start-Sleep -Seconds 5
    
    # Vérifier que le frontend démarre
    $maxRetries = 10
    $retryCount = 0
    $frontendReady = $false
    while ($retryCount -lt $maxRetries -and -not $frontendReady) {
        Start-Sleep -Seconds 1
        if (Test-Port -Port 3000) {
            $frontendReady = $true
            Write-Host "✅ Frontend démarré sur http://localhost:3000" -ForegroundColor Green
        }
        $retryCount++
    }
    
    if (-not $frontendReady) {
        Write-Host "⚠️  Le frontend n'écoute pas encore sur le port 3000 (tentative $retryCount/$maxRetries)" -ForegroundColor Yellow
        Write-Host "   Il devrait démarrer sous peu..." -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  frontend/package.json non trouvé, le frontend ne sera pas démarré" -ForegroundColor Yellow
    $frontendProcess = $null
}

Write-Host ""
Write-Host "✅ Services démarrés!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Accès aux services:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Appuyez sur Ctrl+C pour arrêter tous les services" -ForegroundColor Yellow
Write-Host ""

# Attendre indéfiniment
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Vérifier si les processus sont toujours en cours
        if ($backendProcess -and $backendProcess.HasExited) {
            Write-Host "⚠️  Le backend s'est arrêté" -ForegroundColor Red
        }
        if ($frontendProcess -and $frontendProcess.HasExited) {
            Write-Host "⚠️  Le frontend s'est arrêté" -ForegroundColor Red
        }
    }
} finally {
    Cleanup
}
