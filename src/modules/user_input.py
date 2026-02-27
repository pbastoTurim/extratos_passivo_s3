import tkinter as tk
from tkinter import simpledialog

def input_token():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    token = simpledialog.askstring("Input Token", "Digite o token (apenas números):")
    
    if token.strip():
        return token
    else:
        print("Token inválido. Certifique-se de digitar apenas números.")
        return None

def input_date():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    token = simpledialog.askstring("Input Data", "Digite a data (DDMMYYYY):")
    
    if token.strip():
        return token
    else:
        print("Token inválido. Certifique-se de digitar apenas números.")
        return None
