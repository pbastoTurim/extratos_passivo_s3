import logging
import time 
import shutil
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from configs.constants import URL_S3
from configs.settings import (
    USER_S3, PASSWORD_S3)
from src.core.chase_driver import ChaseDriver
from src.core.base_scraper import BaseScraper
from src.bot.selectors import S3Selectors
from src.modules.user_input import input_token, input_date
from src.bot.fundos import fundos
import os
from src.core.chase_driver import BROWSER_SETTINGS
import zipfile 
import tempfile

class S3Extractor(BaseScraper):
    def __init__(self):
        """
        Inicializa o extrator da Turim.
        Args:
            date (dt.date): Data de referência para o download dos extratos.
            username (str): Nome de usuário para login.
            password (str): Senha para login.
        """
        self.driver = ChaseDriver()
        self.logger = logging.getLogger(__name__)
        self.user = USER_S3
        self.password = PASSWORD_S3
        self.ini = None
        self.fin = None
        self.download_dir = BROWSER_SETTINGS["download.default_directory"]


    def login(self) -> bool:
        """
        Realiza o login no site
        Args: 
            None
        Returns:
            bool: True se o login for bem-sucedido, False caso contrário.
        """
        try:
            self.driver.navigate_to(URL_S3)
            time.sleep(1)
            self.driver.find_and_click(selector=S3Selectors.LOGIN_BUTTON, by=By.XPATH)
            self.driver.find_and_send_keys(selector=S3Selectors.LOGIN_USERNAME, text=self.user, by=By.XPATH)
            self.driver.find_and_send_keys(selector=S3Selectors.LOGIN_PASSWORD, text=self.password, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.ENTRAR_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.EMAIL_OPTION, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.CONTINUE_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.SEND_CODE_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.TOKEN_CODE_INPUT, by=By.XPATH)
            self.driver.find_and_send_keys(selector=S3Selectors.TOKEN_CODE_INPUT, text=input_token(), by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.TOKEN_SUBMIT_BUTTON, by=By.XPATH)
            time.sleep(1)
            self.driver.find_and_click(selector=S3Selectors.CONTINUE_BUTTON, by=By.XPATH)
            time.sleep(5)
            return True

        except Exception as e:
           
            self.logger.error(f"Erro no login: {str(e)}")
            return False
    

    def navega_passivo(self) -> bool:
        """
        Navega na página do passivo.
        """
        try:
            self.driver.wait_for_element_visible(by=By.XPATH, selector=S3Selectors.PASSIVO_BUTTON)
            self.driver.find_and_click(selector=S3Selectors.PASSIVO_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.OK_BUTTON, by=By.XPATH)
            time.sleep(10)
            self.driver.switch_to_window(-1)
            print("url:", self.driver.driver.current_url)
            self.driver.wait_for_element_visible(by=By.XPATH, selector=S3Selectors.RELATORIOS_BUTTON)
            self.driver.find_and_click(selector=S3Selectors.RELATORIOS_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.EXTRATO_BUTTON, by=By.XPATH)
            self.driver.find_and_click(selector=S3Selectors.MENSAL_BUTTON, by=By.XPATH)
            time.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"Erro: {str(e)}")
            return False 
        
    def aplicar_data(self):
        time.sleep(1)
        ini = input_date()
        fin = input_date()
        self.driver.find_and_click(selector=S3Selectors.INI_DATE, by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.INI_DATE, text=Keys.CONTROL + "a", by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.INI_DATE, text=Keys.DELETE, by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.INI_DATE, text=ini, by=By.XPATH)
        time.sleep(1)
        self.driver.find_and_click(selector=S3Selectors.FIN_DATE, by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.FIN_DATE, text=Keys.CONTROL + "a", by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.FIN_DATE, text=Keys.DELETE, by=By.XPATH)
        self.driver.find_and_send_keys(selector=S3Selectors.FIN_DATE, text=fin, by=By.XPATH)
        self.driver.find_and_click(selector=S3Selectors.CHECK_BUTTON, by=By.XPATH)
        self.ini, self.fin = ini, fin
        return ini, fin
    
    
    def limpar_pasta(self, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)


    def salva_pasta(self, nome: str):
        fin = self.fin  # já deve estar definido no download()
        dia = int(fin[0:2])
        mes = int(fin[2:4])
        ano = int(fin[4:8])
        # se fin for 01MMYYYY → usar mês anterior
        if dia == 1 or dia == 2:
            mes -= 1
            if mes == 0:
                mes = 12
                ano -= 1
        # montar caminho final
        pasta_final = os.path.join(
            r"F:\Extratos_Bcos\ONSHORE",
            f"{ano}",
            f"{ano} {mes:02d}",
            "_SANTANDER",
            nome
        )
        # criar a pasta se não existir
        os.makedirs(pasta_final, exist_ok=True)
        return pasta_final    

    def mover_download(self, destino: str):
        """
        Move o ÚNICO item presente em self.download_dir para 'destino'.
        - Se for ARQUIVO comum: move direto (sobrescrevendo se existir).
        - Se for ZIP: extrai e move apenas o CONTEÚDO para 'destino' (sobrescrevendo), apaga o zip e a pasta temp.
        - Se for PASTA: move apenas o CONTEÚDO para 'destino' (sobrescrevendo) e remove a pasta vazia.
        """
        download_dir = self.download_dir
        os.makedirs(destino, exist_ok=True)
        ignorar = {"desktop.ini", ".DS_Store", "Thumbs.db"}
        itens = [x for x in os.listdir(download_dir) if x not in ignorar]
        if not itens:
            raise RuntimeError("Nenhum item encontrado na pasta de download.")
        if len(itens) > 1:
            itens.sort(key=lambda n: os.path.getmtime(os.path.join(download_dir, n)), reverse=True)
        item = itens[0]
        caminho_item = os.path.join(download_dir, item)
        # ========= CASO 1 — ARQUIVO =========
        if os.path.isfile(caminho_item):
            # 1A) ZIP → extrair e mover conteúdo
            if item.lower().endswith(".zip"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(caminho_item, 'r') as z:
                        z.extractall(tmpdir)
                    for root, dirs, files in os.walk(tmpdir):
                        rel = os.path.relpath(root, tmpdir)
                        dst_root = os.path.join(destino, rel) if rel != '.' else destino
                        os.makedirs(dst_root, exist_ok=True)
                        for f in files:
                            src_file = os.path.join(root, f)
                            dst_file = os.path.join(dst_root, f)
                            if os.path.exists(dst_file):
                                if os.path.isdir(dst_file):
                                    shutil.rmtree(dst_file)
                                else:
                                    os.remove(dst_file)
                            shutil.move(src_file, dst_file)
                    os.remove(caminho_item)
                    return destino  
            # 1B) Arquivo comum → move direto (sobrescrevendo)
            dst = os.path.join(destino, item)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(caminho_item, dst)
            return dst
        # ========= CASO 2 — PASTA =========
        if os.path.isdir(caminho_item):
            movidos = []
            for nome_interno in os.listdir(caminho_item):
                src = os.path.join(caminho_item, nome_interno)
                dst = os.path.join(destino, nome_interno)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)
                movidos.append(dst)
            try:
                os.rmdir(caminho_item)
            except OSError:
                shutil.rmtree(caminho_item, ignore_errors=True)
            return movidos
        raise RuntimeError("Item baixado não é arquivo nem pasta.")
        

    def wait_download_finish(self, timeout=250):
        """
        Espera o download terminar verificando:
        - aparece algum arquivo/pasta
        - não existe mais nenhum .crdownload
        """
        download_dir = self.download_dir
        end = time.time() + timeout
        while time.time() < end:
            itens = os.listdir(download_dir)
            # ignorar lixo do Windows
            itens = [i for i in itens if i.lower() not in ("desktop.ini", "thumbs.db")]
            if itens:
                # se apareceu algo mas ainda tem .crdownload → espera
                cr = [f for f in itens if f.lower().endswith(".crdownload")]
                if not cr:
                    return True
            time.sleep(0.3)
        raise TimeoutError("Download não finalizou no tempo esperado.")

    def download(self):
        self.limpar_pasta(r"S:\DataAnalysis\09 PYTHON\Codigos Data Analysis\extratos_passivo_s3\documents")
        ini, fin = "", ""
        for f in fundos:
            nome = f["nome"]
            code = f["codigo"]
            try:
                if ini == "" and fin == "":
                    ini, fin = self.aplicar_data()
                else:
                    if self.driver.try_find_visible(selector=S3Selectors.INI_DATE, by=By.XPATH, timeout=2) == None:
                        pass
                    else:
                        self.driver.find_and_click(selector