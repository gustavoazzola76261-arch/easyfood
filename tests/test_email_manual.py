
import sys
from pathlib import Path

# Adiciona a pasta raiz do projeto ao caminho de importação
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.modules.shared.email_service import send_email


send_email(
    to="gustavo.azzola.76261@a.fecaf.com.br",
    to_name="Gustavo",
    subject="Teste de e-mail - EasyFood",
    header="Teste de envio",
    body="Se você recebeu esta mensagem, o serviço de e-mail do EasyFood está funcionando!",
    footer="Mensagem automática do EasyFood."
)
