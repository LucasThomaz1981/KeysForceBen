import requests
import time
import os

def check_balance(address, proxies=None):
    """
    Verifica o saldo de um endereço Bitcoin usando a API do Blockchain.info ou similar.
    Suporta o uso de proxies rotativos.
    """
    url = f"https://blockchain.info/q/addressbalance/{address}"
    
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            balance = int(response.text)
            return balance
        else:
            print(f"Erro ao consultar saldo para {address}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição para {address}: {e}")
        return None

def get_proxy_config():
    """
    Obtém configuração de proxy das variáveis de ambiente.
    """
    proxy_url = os.getenv("PROXY_URL") # Ex: http://user:pass@host:port
    if proxy_url:
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    return None

def verify_found_keys(found_file, verified_file):
    """
    Lê chaves encontradas e verifica o saldo real.
    """
    if not os.path.exists(found_file):
        return

    proxies = get_proxy_config()
    
    with open(found_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if "Address:" in line:
            parts = line.split("|")
            address = parts[1].split(":")[1].strip()
            private_key = parts[0].split(":")[1].strip()
            
            print(f"Verificando saldo para: {address}...")
            balance = check_balance(address, proxies)
            
            if balance is not None and balance > 0:
                print(f"[!!!] SALDO CONFIRMADO: {balance} Satoshis em {address}")
                with open(verified_file, "a") as vf:
                    vf.write(f"CONFIRMADO | Private Key: {private_key} | Address: {address} | Balance: {balance}\n")
            else:
                print(f"Saldo zero ou erro para {address}")
            
            # Delay para evitar rate limit se não estiver usando proxies robustos
            if not proxies:
                time.sleep(2)

if __name__ == "__main__":
    # verify_found_keys("found.txt", "verified.txt")
    pass
