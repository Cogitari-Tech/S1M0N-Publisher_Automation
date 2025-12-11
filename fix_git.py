import subprocess
import sys
import logging
import os
from typing import List, Tuple, Optional

# ==========================================
# CONFIGURAÇÃO DE LOGGING & AMBIENTE
# ==========================================
# [cite: 9, 10] Não expomos stack traces brutos; usamos logging estruturado.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GitArchitectFix")

# ==========================================
# SERVIÇO DE GIT (CLEAN CODE & SOLID)
# ==========================================
class GitService:
    """
    Classe responsável por interagir com o binário do Git de forma segura.
    Segue o princípio SRP (Single Responsibility Principle).
    """

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self._validate_environment()

    def _validate_environment(self) -> None:
        """Verifica se o git está instalado e acessível."""
        try:
            self._run_command(["git", "--version"])
        except FileNotFoundError:
            logger.critical("Git não encontrado no PATH do sistema.")
            sys.exit(1)

    def _run_command(self, args: List[str]) -> Tuple[bool, str]:
        """
        Executa comandos de shell de forma segura evitando Shell Injection.
         Nunca concatenamos strings para comandos de sistema.
        """
        try:
            # shell=False é crucial para segurança (evita injeção de comandos)
            result = subprocess.run(
                args,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=False, # Tratamos o erro manualmente para não crashar
                shell=False 
            )
            
            if result.returncode != 0:
                return False, result.stderr.strip()
            
            return True, result.stdout.strip()
            
        except Exception as e:
            # [cite: 10] Logamos o erro internamente
            logger.error(f"Erro crítico ao executar comando: {str(e)}")
            return False, str(e)

    def get_status(self) -> str:
        """Retorna o status atual do repositório."""
        success, output = self._run_command(["git", "status", "--short"])
        if not success:
            raise RuntimeError(f"Falha ao obter status: {output}")
        return output

    def stage_all_changes(self) -> bool:
        """Realiza o 'git add .'"""
        logger.info("Adicionando arquivos ao stage...")
        success, output = self._run_command(["git", "add", "."])
        if not success:
            logger.error(f"Erro ao adicionar arquivos: {output}")
            return False
        return True

    def commit_bypass_editor(self, message: str) -> bool:
        """
        Realiza o commit passando a mensagem via argumento, contornando o erro de pipe do editor.
         Nome claro indicando a ação (Verbo + Substantivo).
        """
        if not message or len(message.strip()) < 5:
            logger.warning("Mensagem de commit muito curta ou vazia. Abortando.")
            return False

        # [cite: 8] Sanitização básica: garantimos que message é tratada como argumento único
        logger.info(f"Realizando commit: '{message}'")
        success, output = self._run_command(["git", "commit", "-m", message])
        
        if not success:
            # O erro do usuário (pipe quebrado) é capturado aqui e resolvido pelo método -m
            logger.error(f"Falha no commit: {output}")
            return False
            
        logger.info("Commit realizado com sucesso!")
        return True

    def push_changes(self, branch: str = "HEAD") -> bool:
        """Envia as alterações para o remoto."""
        logger.info("Enviando alterações para o remoto...")
        success, output = self._run_command(["git", "push", "origin", branch])
        
        if not success:
            logger.error(f"Falha no push: {output}")
            return False
            
        logger.info("Push realizado com sucesso.")
        return True

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
def main():
    print("=== Git Pipe Error Fixer (Architect Edition) ===")
    
    # 1. Instanciação
    git_service = GitService(os.getcwd())

    # 2. Verificação de Estado
    try:
        status = git_service.get_status()
        if not status:
            logger.info("Nenhuma alteração pendente para commitar.")
            return
        
        print(f"\nAlterações detectadas:\n{status}\n")
    except RuntimeError as e:
        logger.error(str(e))
        return

    # 3. Interação com Usuário (Input Seguro)
    # Solicitamos a mensagem aqui para passar via flag -m, evitando abrir o editor quebrado
    try:
        commit_msg = input("Digite sua mensagem de commit (Obrigatório): ").strip()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        return

    # 4. Execução do Fluxo
    if git_service.stage_all_changes():
        if git_service.commit_bypass_editor(commit_msg):
            
            should_push = input("Deseja fazer o push agora? (s/n): ").lower()
            if should_push == 's':
                git_service.push_changes()

if __name__ == "__main__":
    main()