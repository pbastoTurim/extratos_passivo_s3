from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from typing import Optional
import chromedriver_autoinstaller
import logging
from typing import cast
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import tempfile, shutil, os

from src.core.base_scraper import BaseScraper
from configs.constants import DEFAULT_TIMEOUT

BROWSER_SETTINGS = {
    "download.default_directory": r"S:\DataAnalysis\09 PYTHON\Codigos Data Analysis\extratos_passivo_s3\documents",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_settings.popups": 0,
}

class ChaseDriver():
    def __init__(self):
        self.driver = cast(webdriver.Chrome, None)
        self.options = webdriver.ChromeOptions()

        self.options.add_experimental_option("prefs", BROWSER_SETTINGS)
        self.options.add_argument("--start-maximized")
        # self.options.add_argument("--headless=new")             # <- ative isso
        self.options.add_argument("--no-sandbox")               # WSL/root
        self.options.add_argument("--disable-dev-shm-usage")    # /dev/shm pequeno
        self.options.add_argument("--disable-gpu")              # seguro cross-env
        self.options.add_argument("--disable-features=VizDisplayCompositor")
        self.options.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Inicializa o navegador"""
        self.driver.set_window_position(1920, 0)
        self.driver.maximize_window()

    def quit(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()

    def navigate_to(self, url: str):
        """Navega para uma URL"""
        self.driver.get(url)

    def find_and_click(self, selector: str, by: By = By.XPATH) -> bool:
        """Encontra e clica em um elemento"""
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao clicar no elemento {selector}: {str(e)}")
            return False

    def find_and_send_keys(self, selector: str, text: str, by: By = By.XPATH) -> bool:
        """Encontra um elemento e envia texto"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            element.send_keys(text)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar texto para {selector}: {str(e)}")
            return False

    def switch_to_frame(self, selector: str, by: By = By.XPATH):
        """Muda para um iframe"""
        frame = self.wait.until(EC.presence_of_element_located((by, selector)))
        self.driver.switch_to.frame(frame)

    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR):
        """Encontra múltiplos elementos"""
        return self.wait.until(EC.presence_of_all_elements_located((by, selector)))

    def find_element(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[webdriver.remote.webelement.WebElement]:
        """Encontra um único elemento"""
        try:
            return self.wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            self.logger.error(f"Elemento {selector} não encontrado")
            return None
    
    
    def try_find_visible(self, selector, by=By.XPATH, timeout=3, poll_frequency=0.5):
        """Retorna WebElement visível ou None após timeout."""
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(
                EC.visibility_of_element_located((by, selector))
            )
        except TimeoutException:
            return None
        
    def click_with_retry(self, element, max_retries: int = 3) -> bool:
        """Tenta clicar em um elemento usando diferentes métodos"""
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    element.click()
                else:
                    self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
        return False

    def scroll_to_element(self, element):
        """Rola até um elemento"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});",
            element
        )

    def is_element_selected(self, element) -> bool:
        """Verifica se um elemento está selecionado"""
        return element.is_selected()

    def get_element_text(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[str]:
        """Obtém o texto de um elemento"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            return element.text.strip()
        except Exception as e:
            self.logger.error(f"Erro ao obter texto do elemento {selector}: {str(e)}")
            return None
    
    def execute_script(self, script: str, *args):
        """Executa um script JavaScript no contexto da página"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Erro ao executar script: {str(e)}")
            return None

    def switch_url(self, url: str):
        """Muda a URL do navegador"""
        try:
            self.driver.get(url)
        except Exception as e:
            self.logger.error(f"Erro ao mudar URL para {url}: {str(e)}")
            return False
        return True
        
    def wait_for_element_visible(self, by: By, selector: str, timeout: int = None) -> bool:
        """
        Espera até que um elemento esteja visível na página
        
        Args:
            by (By): Método de localização do elemento (By.XPATH, By.CSS_SELECTOR, etc.)
            selector (str): Seletor do elemento
            timeout (int, opcional): Tempo máximo de espera em segundos
            
        Returns:
            bool: True se o elemento ficar visível dentro do tempo limite, False caso contrário
        """
        try:
            wait_time = timeout if timeout else DEFAULT_TIMEOUT
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            self.logger.error(f"Elemento {selector} não ficou visível dentro do tempo limite")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao esperar pelo elemento {selector}: {str(e)}")
            return False
    
    def refresh_page(self):
        """Atualiza a página atual"""
        try:
            self.driver.refresh()
        except Exception as e:
            self.logger.error(f"Erro ao atualizar a página: {str(e)}")
    
    def select_by_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Seleciona uma opção em um elemento dropdown pelo texto visível
        
        Args:
            selector (str): Seletor do elemento dropdown
            text (str): Texto visível da opção a ser selecionada
            by (By, opcional): Método de localização do elemento (By.XPATH, By.CSS_SELECTOR, etc.)
            
        Returns:
            bool: True se a seleção foi bem-sucedida, False caso contrário
        """
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            select = Select(element)
            select.select_by_visible_text(text)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar opção '{text}' no elemento {selector}: {str(e)}")
            return False
    
    def select_by_value(self, selector: str, value: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Seleciona uma opção em um elemento dropdown pelo valor
        
        Args:
            selector (str): Seletor do elemento dropdown
            value (str): Valor da opção a ser selecionada
            by (By, opcional): Método de localização do elemento (By.XPATH, By.CSS_SELECTOR, etc.)
            
        Returns:
            bool: True se a seleção foi bem-sucedida, False caso contrário
        """
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            select = Select(element)
            select.select_by_value(value)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar valor '{value}' no elemento {selector}: {str(e)}")
            return False

    def select_by_index(self, selector: str, index: int, by: By = By.CSS_SELECTOR) -> bool:
        """
        Seleciona uma opção em um elemento dropdown pelo índice
        
        Args:
            selector (str): Seletor do elemento dropdown
            index (int): Índice da opção a ser selecionada (começando em 0)
            by (By, opcional): Método de localização do elemento (By.XPATH, By.CSS_SELECTOR, etc.)
            
        Returns:
            bool: True se a seleção foi bem-sucedida, False caso contrário
        """
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            select = Select(element)
            select.select_by_index(index)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar índice {index} no elemento {selector}: {str(e)}")
            return False

    def clear_field(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Limpa o valor de um campo de entrada de texto.

        Args:
            selector (str): Seletor do campo de entrada
            by (By, opcional): Método de localização do elemento (By.XPATH, By.CSS_SELECTOR, etc.)

        Returns:
            bool: True se o campo foi limpo com sucesso, False caso contrário
        """
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            element.clear()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao limpar campo {selector}: {str(e)}")
            return False
        
    def wait_for_new_window(self, expected_count: int, timeout: int = None) -> bool:
        """
        Aguarda até que um número específico de janelas esteja aberto
        
        Args:
            expected_count (int): Número esperado de janelas abertas
            timeout (int, opcional): Tempo máximo de espera em segundos
            
        Returns:
            bool: True se o número esperado de janelas foi atingido, False caso contrário
        """
        try:
            wait_time = timeout if timeout else DEFAULT_TIMEOUT
            WebDriverWait(self.driver, wait_time).until(
                EC.number_of_windows_to_be(expected_count)
            )
            return True
        except TimeoutException:
            self.logger.error(f"O número esperado de janelas ({expected_count}) não foi atingido dentro do tempo limite")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao aguardar por novas janelas: {str(e)}")
            return False

    def switch_to_window(self, index: int = -1) -> bool:
        """
        Muda o foco para uma janela específica
        
        Args:
            index (int, opcional): Índice da janela desejada.
                                0 para a primeira janela,
                                -1 (padrão) para a janela mais recente
                                
        Returns:
            bool: True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            if index >= len(self.driver.window_handles) or abs(index) > len(self.driver.window_handles):
                self.logger.error(f"Índice de janela inválido: {index}. Total de janelas: {len(self.driver.window_handles)}")
                return False
                
            self.driver.switch_to.window(self.driver.window_handles[index])
            return True
        except Exception as e:
            self.logger.error(f"Erro ao mudar para a janela {index}: {str(e)}")
            return False

    def close_current_window(self) -> bool:
        """
        Fecha a janela atual e muda para a janela principal (índice 0)
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True
        except Exception as e:
            self.logger.error(f"Erro ao fechar janela atual: {str(e)}")
            return False

    def get_window_count(self) -> int:
        """
        Retorna o número atual de janelas abertas
        
        Returns:
            int: Número de janelas abertas
        """
        try:
            return len(self.driver.window_handles)
        except Exception as e:
            self.logger.error(f"Erro ao obter contagem de janelas: {str(e)}")
            return 0
        
    def click_robusto(self, xpath: str, timeout: int = 2):
        driver = self.driver  # webdriver real por trás do wrapper
        for tentativa in range(2):  # tenta 2 vezes e acabou
            try:
                # Espera ficar clicável
                el = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                # Scroll até o centro
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                    el
                )
                # Clique normal
                el.click()
                return True
            except (ElementClickInterceptedException, ElementNotInteractableException):
                # Se falhar, tenta JS click
                try:
                    driver.execute_script("arguments[0].click();", el)
                    return True
                except Exception:
                    pass
            except TimeoutException:
                return False
        return False

    def click_if_visible(self, xpath: str, timeout: int = 2):
        """
        Tenta clicar no elemento APENAS se estiver visível dentro do timeout.
        Se não aparecer, retorna False.
        """
        driver = self.driver
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            el.click()
            return True
        except TimeoutException:
            return False