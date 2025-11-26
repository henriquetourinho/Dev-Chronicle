#!/bin/bash

# ==============================================================================
# DEV CHRONICLE - DAILY LOG SCRIPT (BILINGUAL)
# Executa a criação do log diário, formata o arquivo e envia para o GitHub.
# ==============================================================================

# --- Variáveis de Data e Caminho ---
# Define variables for Date and Path
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
DATE_FULL=$(date +'%Y/%m/%d')
DATE_FORMATTED=$(date +'%d/%m/%Y')
DIRETORIO="logs/$YEAR/$MONTH"
ARQUIVO="$DIRETORIO/$DAY-log.md"

# --- Início do Script e Instruções ---
echo "==================================================="
echo "✍️ Dev-Chronicle Daily Log / Registro Diário"
echo "==================================================="

# --- 1. Entrada de Humor / Mood Input ---
echo " "
echo "1. What is your mood today? / Qual é o seu humor hoje?"
echo "(e.g., Productive, Stressed, Happy, Frustrated / Produtivo, Estressado, Feliz, Frustrado)"
read -p "Mood/Humor: " HUMOR

if [ -z "$HUMOR" ]; then
    HUMOR="Not Specified / Não Especificado"
fi

# --- 2. Entrada do Log / Log Input ---
echo " "
echo "2. Write your Daily Log. Press CTRL+D when finished."
echo "   Escreva seu Log Diário. Tecle CTRL+D ao terminar."
echo "---------------------------------------------------"
LOG_TEXT=$(cat)
echo "---------------------------------------------------"

# --- 3. Criação do Arquivo / File Creation ---
echo "-> Creating file / Criando arquivo: $ARQUIVO"

# Cria a estrutura de diretórios, se não existir
# Create directory structure, if it doesn't exist
mkdir -p "$DIRETORIO"

# Escreve o conteúdo no arquivo Markdown
# Write content to the Markdown file
{
    echo "## 📅 Daily Log for $DATE_FORMATTED"
    echo "## 📅 Log Diário de $DATE_FORMATTED"
    echo ""
    echo "#mood: $HUMOR"
    echo ""
    echo "$LOG_TEXT"
    echo ""
} > "$ARQUIVO"

echo "-> File created successfully. / Arquivo criado com sucesso."

# --- 4. Comandos Git / Git Commands ---
echo " "
echo "-> Committing and pushing to GitHub... / Comitando e enviando para o GitHub..."

# Adiciona todos os arquivos modificados (incluindo o novo log)
git add .

# Executa o commit com uma mensagem descritiva
git commit -m "CHRONICLE LOG: $DATE_FULL. Mood: $HUMOR"

# Envia as alterações para o repositório remoto
git push

# --- 5. Confirmação Final / Final Confirmation ---
if [ $? -eq 0 ]; then
    echo " "
    echo "✅ Success! Log saved and pushed to Dev-Chronicle on GitHub."
    echo "✅ Sucesso! Log salvo e enviado para Dev-Chronicle no GitHub."
else
    echo " "
    echo "❌ Error: Failed to push changes. Please check your Git setup."
    echo "❌ Erro: Falha ao enviar as alterações. Por favor, verifique sua configuração Git."
fi

echo "==================================================="