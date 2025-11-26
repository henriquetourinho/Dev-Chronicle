#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import getpass
import glob

# ==============================================================================
# ✍️  DEV CHRONICLE - ULTIMATE EDITION (With Auto-Dashboard)
#
# 🔗  Repository: https://github.com/henriquetourinho/Dev-Chronicle
# 👨‍💻  Developer:  Carlos Henrique Tourinho Santana
# ==============================================================================

# --- CONFIGURAÇÕES ---
NOW = datetime.datetime.now()
DATE_FORMATTED = NOW.strftime('%d/%m/%Y')
DIR_PATH = os.path.join('logs', NOW.strftime('%Y'), NOW.strftime('%m'))
FILE_PATH = os.path.join(DIR_PATH, f"{NOW.strftime('%d')}-log.md")
README_PATH = "README.md"
BRANCH_NAME = 'main'

def run_cmd(command, check=True, silence=False):
    """Executa comandos do sistema operacional."""
    try:
        if silence:
            result = subprocess.run(command, check=check, capture_output=True, text=True, shell=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, check=check, shell=True)
            return result.returncode == 0, ""
    except subprocess.CalledProcessError as e:
        return False, str(e)

def update_readme_stats():
    """Lê logs, calcula estatísticas e atualiza o README automaticamente."""
    print("📊 Calculando estatísticas para o Dashboard...")
    
    # 1. Busca todos os logs na pasta logs/
    log_files = glob.glob("logs/**/*.md", recursive=True)
    total_logs = len(log_files)
    
    # Contadores iniciais
    mood_counts = {
        "Produtivo": 0, 
        "Estressado": 0, 
        "Feliz": 0, 
        "Outro": 0
    }
    last_log_content = "Nenhum log encontrado ainda."

    # 2. Processa cada arquivo
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Conta os humores baseando-se na tag #mood:
                for key in mood_counts:
                    if f"#mood: {key}" in content:
                        mood_counts[key] += 1
                        break
                
                # Pega o texto do log atual para o snippet
                if log_file == FILE_PATH:
                    parts = content.split("#mood:")
                    if len(parts) > 1:
                        # Pega o texto após o mood e limpa espaços
                        raw_text = parts[1].split("\n", 1)[1].strip()
                        # Corta se for muito longo (150 caracteres)
                        last_log_content = (raw_text[:150] + '...') if len(raw_text) > 150 else raw_text
        except Exception as e:
            print(f"   ⚠️ Erro ao ler {log_file}: {e}")

    # 3. Gera a Tabela Markdown Atualizada
    table_rows = []
    
    # Configuração visual (Ícones e Traduções)
    mood_config = {
        "Produtivo":  {"icon": "🚀", "label": "**Productive / Produtivo**"},
        "Estressado": {"icon": "🤯", "label": "**Stressed / Estressado**"},
        "Feliz":      {"icon": "😄", "label": "**Happy / Feliz**"},
        "Outro":      {"icon": "🔹", "label": "**Other / Outro**"}
    }

    for mood, data in mood_config.items():
        count = mood_counts.get(mood, 0)
        percent = (count / total_logs * 100) if total_logs > 0 else 0.0
        row = f"| {data['icon']} {data['label']} | {count} | {percent:.1f}% |"
        table_rows.append(row)

    new_table = f"""| Mood / Sentimento | Frequency / Frequência | Percentage / Percentual |
| :--- | :--- | :--- |
{chr(10).join(table_rows)}"""

    new_log_snippet = f"""**Date / Data:** {DATE_FORMATTED}
> {last_log_content}"""

    # 4. Grava no README.md entre os marcadores ocultos
    if os.path.exists(README_PATH):
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Substitui a Tabela de Stats
        if "" in readme_content and "" in readme_content:
            start = readme_content.find("") + len("")
            end = readme_content.find("")
            readme_content = readme_content[:start] + "\n" + new_table + "\n" + readme_content[end:]
        
        # Substitui o Snippet do Último Log
        if "" in readme_content and "" in readme_content:
            start = readme_content.find("") + len("")
            end = readme_content.find("")
            readme_content = readme_content[:start] + "\n" + new_log_snippet + "\n" + readme_content[end:]
            
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Dashboard atualizado no README com sucesso!")
    else:
        print("⚠️  AVISO: README.md não encontrado. O dashboard não foi atualizado.")

def setup_environment():
    """Configura Git (Anti-Nano) e Autenticação."""
    print("\n" + "="*60)
    print("⚙️  VERIFICANDO AMBIENTE / CHECKING ENVIRONMENT")
    print("="*60)
    
    # Anti-travamento
    run_cmd("git config --global core.mergeoptions --no-edit", silence=True)
    run_cmd("git config pull.rebase false", silence=True)

    # Identidade
    if not subprocess.getoutput("git config user.name"):
        print("\n📝 Configuração de Autor:")
        name = input("   Nome Completo: ").strip()
        email = input("   E-mail: ").strip()
        run_cmd(f'git config user.name "{name}"', silence=True)
        run_cmd(f'git config user.email "{email}"', silence=True)

    # Inicialização
    if not os.path.exists('.git'):
        run_cmd('git init', silence=True)
        
    # Token Check
    remotes = subprocess.getoutput("git remote -v")
    if "https" not in remotes or "@" not in remotes:
        print("\n🔑 Autenticação Necessária (Setup Único).")
        gh_user = input("   👤 Usuário GitHub: ").strip()
        gh_repo = input("   📦 Repositório: ").strip()
        gh_token = getpass.getpass("   🔑 Token (PAT): ").strip()
        
        auth_url = f"https://{gh_user}:{gh_token}@github.com/{gh_user}/{gh_repo}.git"
        run_cmd('git remote remove origin', check=False, silence=True) 
        run_cmd(f'git remote add origin "{auth_url}"', check=False, silence=True)

    run_cmd(f'git branch -M {BRANCH_NAME}', silence=True)

def main():
    print("="*60)
    print("📘  DEV-CHRONICLE: Daily Log")
    print("="*60)

    setup_environment()

    # --- Verifica se já escreveu hoje ---
    if os.path.exists(FILE_PATH):
        print(f"\n⚠️  Log de hoje já existe.")
        if input("   Deseja sobrescrever? (s/n): ").lower() != 's':
            print("   Saindo...")
            sys.exit(0)

    # --- Coleta do Humor e Texto ---
    print("\n1. Humor (1-Produtivo, 2-Estressado, 3-Feliz, 4-Outro):")
    mood_map = {'1': 'Produtivo', '2': 'Estressado', '3': 'Feliz'}
    mood_input = input("   Opção: ").strip()
    mood = mood_map.get(mood_input, "Outro")
    
    print("\n2. Escreva seu log (Tecle ENTER duas vezes para enviar):")
    print("-" * 60)
    lines = []
    while True:
        line = input()
        if not line: break
        lines.append(line)
    
    # --- 1. Salva o Arquivo de Log ---
    os.makedirs(DIR_PATH, exist_ok=True)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(f"## {DATE_FORMATTED}\n#mood: {mood}\n\n" + "\n".join(lines))

    # --- 2. Atualiza o Dashboard (A Mágica) ---
    update_readme_stats()

    # --- 3. Sincroniza e Envia (Git) ---
    print("\n🚀 Enviando para o GitHub...")
    run_cmd('git add .', silence=True)
    
    # Commit inclui Log + README atualizado
    run_cmd(f'git commit -m "Log: {DATE_FORMATTED} - {mood}"', check=False, silence=True)
    
    # Push com Auto-Sync em caso de conflito
    success, _ = run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=True)
    
    if success:
        print("✅ Log, Dashboard e Status atualizados com sucesso!")
    else:
        print("⚠️  Sincronizando mudanças remotas...")
        pull_cmd = f"git pull origin {BRANCH_NAME} --allow-unrelated-histories --no-rebase --no-edit"
        success_pull, _ = run_cmd(pull_cmd, check=False, silence=False)
        
        if success_pull:
            # Se baixou novidades, atualiza stats de novo e reenvia
            update_readme_stats()
            run_cmd('git add README.md', silence=True)
            run_cmd('git commit -m "Update Stats after Sync"', check=False, silence=True)
            run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=False)
            print("✅ Sincronizado e Enviado!")
        else:
            print("❌ Erro de conexão.")

if __name__ == '__main__':
    main()