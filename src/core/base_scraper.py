from abc import ABC, abstractmethod
from typing import List, Optional
import logging


class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Realiza o login no site.
        
        Args:
            username (str): Nome de usuário
            password (str): Senha
            
        Returns:
            bool: True se o login foi bem sucedido
        """
        pass


    @abstractmethod
    def logout(self) -> bool:
        """
        Realiza o logout do site.
        
        Returns:
            bool: True se o logout foi bem sucedido
        """
        pass