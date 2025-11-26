#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import getpass

# ==============================================================================
# ✍️  DEV CHRONICLE - ZERO TOUCH EDITION
#
# 🔗  Repository: https://github.com/henriquetourinho/Dev-Chronicle
# 👨‍💻  Developer:  Carlos Henrique Tourinho Santana
# 📧  Email:      henriquetourinho@riseup.net
#
# Description: Automated daily logging tool with auto-sync capabilities.
# ==============================================================================

# --- CONFIGURAÇÃO / SETTINGS ---
NOW = datetime.datetime.now()
DATE_FORMATTED = NOW.strftime('%d/%m/%Y')
DIR_PATH = os.path.join('logs', NOW.strftime('%Y'), NOW.strftime('%m'))
FILE_PATH = os.path.join(DIR_PATH, f"{NOW.strftime('%d')}-log.md")
BRANCH_NAME = 'main'

def run_cmd(command, check=True, silence=False):
    """Executa comandos do sistema operacional."""
    try:
        if silence:
            # Roda escondido (silencioso)
            result = subprocess.run(command, check=check, capture_output=True, text=True, shell=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            # Roda mostrando a saída no terminal (para erros críticos)
            result = subprocess.run(command, check=check, shell=True)
            return result.returncode == 0, ""
    except subprocess.CalledProcessError as e:
        return False, str(e)

def setup_environment():
    """Verifica e configura o ambiente Git automaticamente."""
    print("\n" + "="*60)
    print("⚙️  VERIFICANDO AMBIENTE / CHECKING ENVIRONMENT")
    print("="*60)
    
    # 1. Configurações Globais para evitar travamentos (Anti-Nano)
    run_cmd("git config --global core.mergeoptions --no-edit", silence=True)
    run_cmd("git config pull.rebase false", silence=True)

    # 2. Identidade do Autor
    if not subprocess.getoutput("git config user.name"):
        print("\n📝 Configuração Inicial de Autor (Apenas na 1ª vez):")
        name = input("   Nome Completo / Full Name: ").strip()
        email = input("   E-mail: ").strip()
        run_cmd(f'git config user.name "{name}"', silence=True)
        run_cmd(f'git config user.email "{email}"', silence=True)

    # 3. Inicializa Git se não existir
    if not os.path.exists('.git'):
        run_cmd('git init', silence=True)
        
    # 4. Verifica Conexão Remota e Token
    remotes = subprocess.getoutput("git remote -v")
    if "https" not in remotes or "@" not in remotes:
        print("\n🔑 Autenticação Necessária (Setup de Segurança).")
        print("   Insira seu Usuário e Token (PAT) para automação total.")
        
        gh_user = input("   👤 Usuário GitHub: ").strip()
        gh_repo = input("   📦 Repositório (ex: Dev-Chronicle): ").strip()
        gh_token = getpass.getpass("   🔑 Token (PAT): ").strip()

        # Monta URL com credenciais embutidas
        auth_url = f"https://{gh_user}:{gh_token}@github.com/{gh_user}/{gh_repo}.git"
        
        run_cmd('git remote remove origin', check=False, silence=True) 
        run_cmd(f'git remote add origin "{auth_url}"', check=False, silence=True)
        print("   ✅ Credenciais salvas com sucesso.")

    # Garante o nome da branch correta
    run_cmd(f'git branch -M {BRANCH_NAME}', silence=True)

def main():
    print("="*60)
    print("📘  DEV-CHRONICLE: Daily Log")
    print("="*60)

    setup_environment()

    # --- Verificação de Arquivo Existente ---
    if os.path.exists(FILE_PATH):
        print(f"\n⚠️  Log de hoje já existe.")
        if input("   Deseja sobrescrever? (s/n): ").lower() != 's':
            print("   Operação cancelada. Saindo...")
            sys.exit(0)

    # --- Entrada de Dados ---
    print("\n1. Humor (1-Produtivo, 2-Estressado, 3-Feliz, 4-Outro):")
    mood_map = {'1': 'Produtivo', '2': 'Estressado', '3': 'Feliz'}
    mood_input = input("   Opção: ").strip()
    mood = mood_map.get(mood_input, "Outro") # Padrão caso digite algo diferente
    
    print("\n2. Escreva seu log (Tecle ENTER duas vezes para finalizar e enviar):")
    print("-" * 60)
    lines = []
    while True:
        line = input()
        if not line: break
        lines.append(line)
    
    # --- Gravação do Arquivo ---
    os.makedirs(DIR_PATH, exist_ok=True)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(f"## {DATE_FORMATTED}\n#mood: {mood}\n\n" + "\n".join(lines))

    # --- Sincronização e Envio ---
    print("\n🚀 Enviando para o GitHub...")
    run_cmd('git add .', silence=True)
    run_cmd(f'git commit -m "Log: {DATE_FORMATTED} - {mood}"', check=False, silence=True)
    
    # Tentativa 1: Push Direto
    success, _ = run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=True)
    
    if success:
        print("✅ Log enviado com sucesso!")
    else:
        print("⚠️  Detectada atualização remota. Sincronizando...")
        # Estratégia Anti-Nano: --no-edit impede que o editor abra
        pull_cmd = f"git pull origin {BRANCH_NAME} --allow-unrelated-histories --no-rebase --no-edit"
        success_pull, _ = run_cmd(pull_cmd, check=False, silence=False)
        
        if success_pull:
            run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=False)
            print("✅ Sincronizado e Enviado com sucesso!")
        else:
            print("❌ Erro de conexão ou conflito crítico.")
            print("   Verifique sua internet ou as credenciais.")

if __name__ == '__main__':
    main()