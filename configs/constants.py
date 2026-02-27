# URL S3
URL_S3 = "https://www.s3caceis.com.br/"

# tempo padrão de espera em segundos
DEFAULT_TIMEOUT = 45
DEFAULT_SLEEP = 1.85
EXTENDED_SLEEP = 15

# Configurações do navegador
CHROME_ARGUMENTS = [
    "--kiosk-printing",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--headless=new",
    "--allow-running-insecure-content",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors=yes",
    "--allow-insecure-localhost"
]