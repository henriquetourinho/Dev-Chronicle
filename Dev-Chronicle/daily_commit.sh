#!/bin/bash

# ==============================================================================
# DEV CHRONICLE - DAILY LOG SCRIPT (BILINGUAL & ROBUST)
# Cria o log diário, verifica erros comuns (como arquivo existente) e envia.
# ==============================================================================

# --- Variáveis de Data e Caminho ---
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
DATE_FULL=$(date +'%Y/%m/%d')
DATE_FORMATTED=$(date +'%d/%m/%Y')
DIRETORIO="logs/$YEAR/$MONTH"
ARQUIVO="$DIRETORIO/$DAY-log.md"

# --- Início e Verificações de Erro ---
echo "==================================================="
echo "✍️ Dev-Chronicle Daily Log / Registro Diário"
echo "==================================================="

# 🔴 CHECK 1: Verificação de Repositório Git / Git Repository Check
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ ERROR: This folder is NOT a Git repository."
    echo "❌ ERRO: Esta pasta NÃO é um repositório Git."
    echo "Please run this script from the 'Dev-Chronicle' folder."
    echo "Por favor, execute este script dentro da pasta 'Dev-Chronicle'."
    exit 1
fi

# 🔴 CHECK 2: Verificação de Arquivo Existente / Existing File Check
if [ -f "$ARQUIVO" ]; then
    echo "⚠️ WARNING: A log file for today ($DATE_FORMATTED) already exists."
    echo "⚠️ AVISO: Um arquivo de log para hoje ($DATE_FORMATTED) já existe."
    read -p "Do you want to (O)verwrite or (C)ancel? (O/C): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Oo]$ ]]; then
        echo "Canceled by user. / Cancelado pelo usuário."
        exit 0
    fi
fi

# --- 1. Entrada de Humor / Mood Input ---
echo " "
echo "1. What is your mood today? / Qual é o seu humor hoje?"
read -p "Mood/Humor: " HUMOR

if [ -z "$HUMOR" ]; then
    HUMOR="Not Specified / Não Especificado"
fi

# --- 2. Entrada do Log (Multilinha) / Log Input (Multiline) ---
echo " "
echo "2. Write your Daily Log. Press ENTER, write your text, and press CTRL+D when finished."
echo "   Escreva seu Log Diário. Tecle ENTER, escreva seu texto, e tecle CTRL+D ao terminar."
echo "---------------------------------------------------"
LOG_TEXT=$(cat)
echo "---------------------------------------------------"

# --- 3. Criação do Arquivo / File Creation ---
echo "-> Creating/Overwriting file / Criando/Sobrescrevendo arquivo: $ARQUIVO"

# Cria a estrutura de diretórios, se não existir
mkdir -p "$DIRETORIO"

# Escreve o conteúdo (usando HEREDOC para limpeza)
cat << EOF > "$ARQUIVO"
## 📅 Daily Log for $DATE_FORMATTED
## 📅 Log Diário de $DATE_FORMATTED

#mood: $HUMOR

$LOG_TEXT
EOF

echo "-> File created successfully. / Arquivo criado com sucesso."

# --- 4. Comandos Git / Git Commands ---
echo " "
echo "-> Committing and pushing to GitHub... / Comitando e enviando para o GitHub..."

# Adiciona o novo arquivo (ou o arquivo modificado)
git add "$ARQUIVO"
# Adiciona o README.md para o caso da automação futura
git add README.md > /dev/null 2>&1

# Executa o commit
git commit -m "CHRONICLE LOG: $DATE_FULL. Mood: $HUMOR"

# Envia as alterações
git push

# --- 5. Confirmação Final / Final Confirmation ---
if [ $? -eq 0 ]; then
    echo " "
    echo "✅ SUCCESS! Log saved and pushed to Dev-Chronicle on GitHub."
    echo "✅ SUCESSO! Log salvo e enviado para Dev-Chronicle no GitHub."
else
    echo " "
    echo "❌ ERROR: Failed to push changes. Check your internet connection or Git credentials."
    echo "❌ ERRO: Falha ao enviar as alterações. Verifique sua conexão com a internet ou credenciais Git."
    exit 1
fi

echo "==================================================="