import os
from pybloom_live import BloomFilter
import requests

def create_bloom_filter(address_file, bloom_file, capacity=10000000, error_rate=0.001):
    """
    Cria um Bloom Filter a partir de um arquivo de endereços.
    """
    bf = BloomFilter(capacity=capacity, error_rate=error_rate)
    
    if os.path.exists(address_file):
        with open(address_file, 'r') as f:
            for line in f:
                address = line.strip()
                if address:
                    bf.add(address)
        
        with open(bloom_file, 'wb') as f:
            bf.tofile(f)
        print(f"Bloom Filter criado com sucesso em {bloom_file}")
    else:
        print(f"Arquivo de endereços {address_file} não encontrado.")

def load_bloom_filter(bloom_file):
    """
    Carrega um Bloom Filter de um arquivo.
    """
    if os.path.exists(bloom_file):
        with open(bloom_file, 'rb') as f:
            return BloomFilter.fromfile(f)
    return None

if __name__ == "__main__":
    # Exemplo de uso:
    # create_bloom_filter("addresses.txt", "addresses.bloom")
    pass
