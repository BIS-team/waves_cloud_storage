from cryptography.fernet import Fernet

def generateKey():
    return Fernet.generate_key()


def getEncryptedData(file_bytes, key):
    cipher = Fernet(key)
    return cipher.encrypt(file_bytes)


def getDecryptedData(encrypted_bytes, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_bytes)
