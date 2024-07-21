import os
import datetime
import webbrowser
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import psutil
import requests
from bs4 import BeautifulSoup

# Caminhos dos arquivos para armazenar a chave secreta e a data de instalação criptografada
local_appdata_path = os.path.join(os.environ['LOCALAPPDATA'], 'secret1.key')
install_date_file = os.path.join(os.environ['LOCALAPPDATA'], 'install_date1.enc')

def generate_key():
    if not os.path.exists(local_appdata_path):
        key = Fernet.generate_key()
        with open(local_appdata_path, 'wb') as key_file:
            key_file.write(key)
        print("Computador registrado")
    else:
        print("Este Sistema já foi utilizado por 5 dias.")

def generate_install_date():
    if not os.path.exists(install_date_file):
        install_date = datetime.datetime.now()
        encrypted_date = encrypt_data(install_date.strftime('%Y-%m-%d'))
        with open(install_date_file, 'wb') as file:
            file.write(encrypted_date)
        print(f"Data de instalação gerada e salva em '{install_date_file}'.")
    else:
        print("Data de instalação já existe.")

def encrypt_data(data):
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def load_key():
    return open(local_appdata_path, 'rb').read()

def decrypt_data(encrypted_data):
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

def get_install_date():
    if os.path.exists(install_date_file):
        with open(install_date_file, 'rb') as file:
            encrypted_date = file.read()
            date_str = decrypt_data(encrypted_date)
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    else:
        install_date = datetime.datetime.now()
        encrypted_date = encrypt_data(install_date.strftime('%Y-%m-%d'))
        with open(install_date_file, 'wb') as file:
            file.write(encrypted_date)
        return install_date

def check_expiration():
    install_date = get_install_date()
    current_date = datetime.datetime.now()
    days_used = (current_date - install_date).days

    if days_used >= 5:
        return False
    else:
        print(f"Período de avaliação: {days_used + 1} dias")
        return True

def show_expiration_window():
    window = tk.Tk()
    window.title("INSIDER Informa")
    
    message = (
        "O período de avaliação terminou.\n Agora, adquira a sua assinatura."
    )
    
    label = tk.Label(window, text=message, padx=20, pady=20, wraplength=300)
    label.pack()

    def open_link():
        webbrowser.open("https://toplivre.online/venda-do-bot/")
    
    button = tk.Button(window, text="ADQUIRIR\n ASSINATURA\n AGORA", command=open_link, padx=10, pady=5)
    button.pack(pady=10)

    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    window.mainloop()

def get_mac_address():
    try:
        addrs = psutil.net_if_addrs()
        for interface, addr_list in addrs.items():
            for addr in addr_list:
                if addr.family == psutil.AF_LINK:
                    return addr.address
        return None
    except Exception as e:
        print(f"Erro ao obter o endereço MAC: {e}")
        return None

def check_mac_in_website(mac_address):
    url = "https://toplivre.online/licenca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta um erro para respostas de erro HTTP
        soup = BeautifulSoup(response.text, 'html.parser')
        
        page_content = soup.find(class_='page-content')
        if page_content:
            mac_list_text = page_content.get_text()
            
            if mac_address in mac_list_text:
                print("EXISTE")
                return True
            else:
                print("NAO CONTA")
                return False
        else:
            print("Conteúdo da classe 'page-content' não encontrado.")
            return False
    
    except requests.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        return False

def main():
    generate_key()
    generate_install_date()

    if check_expiration():
        print("Tecle enter para Entrar no Sistema.")
        input()  # Aguarda a entrada do usuário
        print("SISTEMA INICIADO. BOA SORTE")
    else:
        mac_address = get_mac_address()
        if mac_address:
            if check_mac_in_website(mac_address):
                print("SISTEMA LIBERADO.")
                print("Tecle enter para Entrar no Sistema.")
                input()  # Aguarda a entrada do usuário
                print("SISTEMA INICIADO. BOA SORTE")
            else:
                print("SISTEMA NÃO AUTORIZADO.")
                show_expiration_window()
        else:
            print("Não foi possível obter o endereço MAC.")

if __name__ == "__main__":
    main()
