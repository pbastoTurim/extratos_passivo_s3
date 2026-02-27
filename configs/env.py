import os
from pathlib import Path
from dotenv import load_dotenv

# Caminho absoluto do arquivo .env
#ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
ENV_PATH = Path("S:/DataAnalysis/09 PYTHON/Codigos Data Analysis/extratos_passivo_s3/.env")

def load_environment():
    """Carrega variáveis de ambiente do arquivo .env."""
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        print(f"Aviso: arquivo .env não encontrado em {ENV_PATH}")

load_environment()

def get_env_var(key: str, default=None, required=False):
    """
    Recupera variável de ambiente com validação opcional.
    :param key: Nome da variável de ambiente
    :param default: Valor padrão se a variável não estiver definida
    :param required: Se True, lança um erro se a variável não estiver definida
    :return: Valor da variável de ambiente ou valor padrão
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Variável de ambiente obrigatória ausente: {key}")
    return value