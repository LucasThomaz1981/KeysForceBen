import os
import hashlib
import binascii
import multiprocessing
import time
from ecdsa import SigningKey, SECP256k1

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def base58_encode(v):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(v, byteorder='big')
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(alphabet[r])
    res = "".join(res[::-1])
    
    # Add leading 1s for zero bytes
    pad = 0
    for b in v:
        if b == 0:
            pad += 1
        else:
            break
    return "1" * pad + res

def private_key_to_address(private_key_hex):
    # Get public key
    sk = SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()
    
    # SHA256 on public key
    sha256_pk = sha256(public_key)
    
    # RIPEMD160 on SHA256 result
    ripemd160_pk = ripemd160(sha256_pk)
    
    # Add network byte (0x00 for Mainnet)
    network_pk = b'\x00' + ripemd160_pk
    
    # Double SHA256 for checksum
    checksum = sha256(sha256(network_pk))[:4]
    
    # Binary address
    binary_address = network_pk + checksum
    
    return base58_encode(binary_address)

from bloom_manager import load_bloom_filter

def generate_worker(bloom_file, found_file):
    print(f"Worker {os.getpid()} iniciado.")
    bf = load_bloom_filter(bloom_file)
    if bf is None:
        print(f"Erro: Bloom Filter {bloom_file} não encontrado.")
        return

    count = 0
    start_time = time.time()
    
    while True:
        # Gerar chave privada aleatória
        private_key = os.urandom(32).hex()
        address = private_key_to_address(private_key)
        
        # Verificação real contra o Bloom Filter
        if address in bf:
            print(f"\n[!] POSSÍVEL MATCH ENCONTRADO: {address}")
            with open(found_file, "a") as f:
                f.write(f"Private Key: {private_key} | Address: {address} | Time: {time.ctime()}\n")
        
        count += 1
        if count % 100000 == 0: # Aumentado para 100k para não poluir demais os logs
            elapsed = time.time() - start_time
            print(f"Worker {os.getpid()}: {count} chaves geradas. Velocidade: {count/elapsed:.2f} chaves/s")

if __name__ == "__main__":
    bloom_file = "addresses.bloom"
    found_file = "found.txt"
    
    if not os.path.exists(bloom_file):
        print(f"Aviso: {bloom_file} não encontrado. Certifique-se de gerar o Bloom Filter antes de rodar.")
    
    num_cores = multiprocessing.cpu_count()
    print(f"Iniciando motor com {num_cores} núcleos...")
    processes = []
    for _ in range(num_cores):
        p = multiprocessing.Process(target=generate_worker, args=(bloom_file, found_file))
        p.start()
        processes.append(p)
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Encerrando motor...")
        for p in processes:
            p.terminate()
