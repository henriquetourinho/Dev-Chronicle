#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import getpass
import glob

# ==============================================================================
# ✍️  DEV CHRONICLE - ULTIMATE EDITION (With Stats Dashboard)
# ==============================================================================

NOW = datetime.datetime.now()
DATE_FORMATTED = NOW.strftime('%d/%m/%Y')
DIR_PATH = os.path.join('logs', NOW.strftime('%Y'), NOW.strftime('%m'))
FILE_PATH = os.path.join(DIR_PATH, f"{NOW.strftime('%d')}-log.md")
README_PATH = "README.md"
BRANCH_NAME = 'main'

def run_cmd(command, check=True, silence=False):
    """Executa comandos do sistema."""
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
    """Lê todos os logs, calcula estatísticas e atualiza o README."""
    print("📊 Atualizando Dashboard no README...")
    
    # 1. Coleta dados de todos os arquivos .md em logs/
    log_files = glob.glob("logs/**/*.md", recursive=True)
    total_logs = len(log_files)
    mood_counts = {"Produtivo": 0, "Estressado": 0, "Feliz": 0, "Outro": 0}
    last_log_content = "Nenhum log encontrado."
    
    if total_logs == 0:
        return

    # Lê cada arquivo para contar o #mood
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Pega o último log para o snippet
            if log_file == os.path.join(DIR_PATH, f"{NOW.strftime('%d')}-log.md") or log_file == log_files[-1]:
                # Tenta pegar um trecho do texto
                parts = content.split("#mood:")
                if len(parts) > 1:
                    last_log_content = parts[1].split("\n", 1)[1].strip()[:200] + "..."

            # Conta o humor
            for key in mood_counts:
                if f"#mood: {key}" in content:
                    mood_counts[key] += 1
                    break
    
    # 2. Gera a Tabela Markdown
    table_rows = []
    for mood, count in mood_counts.items():
        percent = (count / total_logs) * 100 if total_logs > 0 else 0
        icon_map = {"Produtivo": "🚀", "Estressado": "🤯", "Feliz": "😄", "Outro": "🔹"}
        pt_en_map = {
            "Produtivo": "**Productive / Produtivo**",
            "Estressado": "**Stressed / Estressado**",
            "Feliz": "**Happy / Feliz**",
            "Outro": "**Other / Outro**"
        }
        row = f"| {icon_map.get(mood, '')} {pt_en_map.get(mood, mood)} | {count} | {percent:.1f}% |"
        table_rows.append(row)

    new_table = \
f"""| Mood / Sentimento | Frequency / Frequência | Percentage / Percentual |
| :--- | :--- | :--- |
{chr(10).join(table_rows)}"""

    new_log_snippet = \
f"""**Date / Data:** {DATE_FORMATTED}
> {last_log_content}"""

    # 3. Injeta no README (Substituição Inteligente)
    if os.path.exists(README_PATH):
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Substitui Tabela
        if "" in readme_content and "" in readme_content:
            start = readme_content.find("") + len("")
            end = readme_content.find("")
            readme_content = readme_content[:start] + "\n" + new_table + "\n" + readme_content[end:]
        
        # Substitui Último Log
        if "" in readme_content and "" in readme_content:
            start = readme_content.find("") + len("")
            end = readme_content.find("")
            readme_content = readme_content[:start] + "\n" + new_log_snippet + "\n" + readme_content[end:]
            
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README atualizado com sucesso!")
    else:
        print("⚠️ README.md não encontrado.")

def setup_environment():
    """Configura ambiente Git (Anti-Nano e Auth)."""
    print("\n" + "="*60)
    print("⚙️  VERIFICANDO AMBIENTE / CHECKING ENVIRONMENT")
    print("="*60)
    
    run_cmd("git config --global core.mergeoptions --no-edit", silence=True)
    run_cmd("git config pull.rebase false", silence=True)

    if not subprocess.getoutput("git config user.name"):
        name = input("   Nome Completo / Full Name: ").strip()
        email = input("   E-mail: ").strip()
        run_cmd(f'git config user.name "{name}"', silence=True)
        run_cmd(f'git config user.email "{email}"', silence=True)

    if not os.path.exists('.git'):
        run_cmd('git init', silence=True)
        
    remotes = subprocess.getoutput("git remote -v")
    if "https" not in remotes or "@" not in remotes:
        print("\n🔑 Autenticação Necessária (Setup de Segurança).")
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

    # --- Verificação de Arquivo Existente ---
    if os.path.exists(FILE_PATH):
        print(f"\n⚠️  Log de hoje já existe.")
        if input("   Deseja sobrescrever? (s/n): ").lower() != 's':
            print("   Saindo...")
            sys.exit(0)

    # --- Entrada ---
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
    
    # --- Gravação ---
    os.makedirs(DIR_PATH, exist_ok=True)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(f"## {DATE_FORMATTED}\n#mood: {mood}\n\n" + "\n".join(lines))

    # --- ATUALIZAÇÃO DO DASHBOARD (A Mágica Acontece Aqui) ---
    update_readme_stats()

    # --- Envio ---
    print("\n🚀 Enviando para o GitHub...")
    run_cmd('git add .', silence=True)
    run_cmd(f'git commit -m "Log: {DATE_FORMATTED} - {mood}"', check=False, silence=True)
    
    success, _ = run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=True)
    
    if success:
        print("✅ Log e Dashboard atualizados com sucesso!")
    else:
        print("⚠️  Sincronizando...")
        pull_cmd = f"git pull origin {BRANCH_NAME} --allow-unrelated-histories --no-rebase --no-edit"
        success_pull, _ = run_cmd(pull_cmd, check=False, silence=False)
        
        if success_pull:
            # Atualiza stats novamente caso o pull tenha trazido logs novos de outro lugar
            update_readme_stats() 
            run_cmd('git add README.md', silence=True)
            run_cmd('git commit -m "Update Stats"', check=False, silence=True)
            run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=False)
            print("✅ Sincronizado e Enviado!")
        else:
            print("❌ Erro de conexão.")

if __name__ == '__main__':
    main()