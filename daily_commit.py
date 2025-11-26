import os
import subprocess
import datetime
import sys
import getpass

# ==============================================================================
# DEV CHRONICLE - AUTO-MERGE FIX
# ==============================================================================

NOW = datetime.datetime.now()
DATE_FORMATTED = NOW.strftime('%d/%m/%Y')
DIR_PATH = os.path.join('logs', NOW.strftime('%Y'), NOW.strftime('%m'))
FILE_PATH = os.path.join(DIR_PATH, f"{NOW.strftime('%d')}-log.md")
BRANCH_NAME = 'main'

def run_cmd(command, check=True, silence=False):
    """Executa comando shell."""
    try:
        if silence:
            result = subprocess.run(command, check=check, capture_output=True, text=True, shell=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, check=check, shell=True)
            return result.returncode == 0, ""
    except subprocess.CalledProcessError as e:
        return False, str(e)

def setup_force_git():
    """Força a configuração do Git, Token e ESTRATÉGIA DE PULL."""
    print("\n" + "="*60)
    print("🔧 REPARO E CONFIGURAÇÃO / SETUP & REPAIR")
    print("="*60)
    
    # 1. Define estratégia de Merge para evitar o erro fatal
    # Isso resolve o "Need to specify how to reconcile divergent branches"
    run_cmd("git config pull.rebase false", silence=True)

    # 2. Identidade
    if not subprocess.getoutput("git config user.name"):
        name = input("   Nome Completo / Full Name: ").strip()
        email = input("   E-mail: ").strip()
        run_cmd(f'git config user.name "{name}"', silence=True)
        run_cmd(f'git config user.email "{email}"', silence=True)

    # 3. Inicialização
    if not os.path.exists('.git'):
        run_cmd('git init', silence=True)
        
    # 4. Token (Verifica se precisa reconfigurar)
    remotes = subprocess.getoutput("git remote -v")
    if "https" not in remotes or "@" not in remotes:
        print("\n📝 Autenticação Necessária (Token não detectado na URL).")
        gh_user = input("   👤 Usuário GitHub (ex: henriquetourinho): ").strip()
        gh_repo = input("   📦 Repositório (ex: Dev-Chronicle): ").strip()
        gh_token = getpass.getpass("   🔑 Cole seu TOKEN: ").strip()

        auth_url = f"https://{gh_user}:{gh_token}@github.com/{gh_user}/{gh_repo}.git"
        
        # Remove antigo e põe o novo
        run_cmd('git remote remove origin', check=False, silence=True) 
        run_cmd(f'git remote add origin "{auth_url}"', check=False, silence=True)
        print("   ✅ Token configurado.")

    run_cmd(f'git branch -M {BRANCH_NAME}', silence=True)

def main():
    print("="*60)
    print("✍️  DEV-CHRONICLE: Daily Log")
    print("="*60)

    setup_force_git()

    # --- Coleta do Log ---
    if os.path.exists(FILE_PATH):
        print(f"\n⚠️  Log de hoje já existe.")
        if input("   Sobrescrever? (s/n): ").lower() != 's':
            print("   Mantendo arquivo existente.")
        else:
            print("   Recriando arquivo...")
            # (Lógica de escrita abaixo sobrescreve)

    print("\n1. Humor (1-Produtivo, 2-Estressado, 3-Feliz, 4-Outro):")
    mood_input = input("   Opção: ").strip()
    
    print("\n2. Escreva seu log (Tecle ENTER duas vezes para enviar):")
    print("-" * 60)
    lines = []
    while True:
        line = input()
        if not line: break
        lines.append(line)
    
    # --- Salvar ---
    os.makedirs(DIR_PATH, exist_ok=True)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(f"## {DATE_FORMATTED}\n#mood: {mood_input}\n\n" + "\n".join(lines))

    # --- ENVIO INTELIGENTE ---
    print("\n🚀 Processando envio...")
    run_cmd('git add .', silence=True)
    run_cmd(f'git commit -m "Log: {DATE_FORMATTED}"', check=False, silence=True)
    
    # Tentativa 1: Push direto
    success, _ = run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=True)
    
    if success:
        print("✅ SUCESSO! Log Enviado.")
    else:
        print("⚠️  Divergência detectada. Unindo históricos (Merge)...")
        
        # A MÁGICA ACONTECE AQUI:
        # --no-rebase: Garante que o git use merge (resolve o erro fatal)
        # --allow-unrelated-histories: Permite unir Log local com README remoto
        pull_cmd = f"git pull origin {BRANCH_NAME} --allow-unrelated-histories --no-rebase"
        
        success_pull, output_pull = run_cmd(pull_cmd, check=False, silence=False)
        
        if success_pull:
            print("✅ Históricos unidos com sucesso.")
            print("☁️  Enviando versão final...")
            run_cmd(f'git push -u origin {BRANCH_NAME}', check=False, silence=False)
            print("✅ FINALIZADO! Tudo sincronizado.")
        else:
            print("❌ ERRO FINAL. O Git não conseguiu unir os arquivos automaticamente.")
            print("   Tente apagar a pasta local e clonar de novo se não tiver dados importantes.")

if __name__ == '__main__':
    main()