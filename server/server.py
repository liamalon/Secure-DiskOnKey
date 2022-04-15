from database import DataBase
import socket
import threading
import encrypt
from tcp_by_size import recv_by_size,send_with_size
import random
import hashlib
db = DataBase("users.txt")

ROOMS_PORT = 4444

def check_login(name_and_password,sock):
        """
        --> Check if user in database <--
        """
        name = name_and_password[0]
        password = name_and_password[1]
        print(password)
        if db.validate(name, password):
                sock.send(b"True")
        else:
                sock.send(b"False")
        
def submit(new_user,sock):
        """
        --> Adds user to DataBase <--
        """        
        email = new_user[0]

        password = new_user[1]

        name = new_user[2]

        key = create_key()

        salt = create_salt()
        
        db.add_user(email, password, name, key.decode(),salt)

def create_salt():
        abc = "abcdefghiklmnopqrstvxyz"
        nums = "1234567890"
        salt = ""
        for _ in range(10):
                if random.randint(1,2) ==1:
                        salt+=random.choice(abc)
                else:
                        salt+=random.choice(nums)
        return salt

def get_user(user,sock):
        """
        --> Sends user details over to client <--
        """
        password, name, created,key,salt = db.get_user(user[0])
        sock.send(password.encode() +b"~" +name.encode()  +b"~" +created.encode())

def change_pass(data,sock):
        """
        --> Checks if it is the ols password and if it is it changes the password <--
        """
        password, name, created,key,salt = db.get_user(data[0])
        print(password,data[1],salt)
        add_salt_to_real = data[1]+salt
        if password == hashlib.sha256(add_salt_to_real.encode('utf-8')).hexdigest():
                add_salt_to_change = data[2]+salt
                db.change_pass(data[0],hashlib.sha256(add_salt_to_change.encode('utf-8')).hexdigest())
                sock.send(b"succeed")
        else:
                sock.send(b"bad password")


        

def create_key():
        """
        --> Create key to encrypt and decrypt <--
        """
        return encrypt.create_key()

def get_user_key(user,sock):
        """
        --> Send key to client <--
        """
        sock.send(db.get_key(user[0]).encode())

def create_backup(data,user):
        """
        --> Create backup for the client <--
        """
        with open(f"Backups\\{user}.zip","wb") as write_zip:
                write_zip.write(data.encode("IBM437"))

def get_backup(user,sock):
        """
        --> Send backup to client <--
        """
        with open(f"Backups\\{user[0]}.zip", "rb") as zip_to_read:
            file_data = zip_to_read.read()
        
        file_data = file_data.decode("IBM437")

        len_data = str(len(file_data+ "###")).zfill(16)

        sock.send(b"CRTB~" + len_data.encode() +b"~" + file_data.encode("IBM437") + b"###")

def handle_clients(sock):
        """
        --> Handle every client that connects <--
        """
        while True:
                code = sock.recv(5)
                code = code.decode()[:4]
                str_data = recv_by_size(sock)
                if code != "CRTB":
                        str_data = str_data.decode() 
                        str_data = str_data.split("###")[0]
                        splited_str_data = str_data.split("~")
                else:
                        str_data = str_data.decode("IBM437")
                        str_data = str_data.split("###")[0]
                        name = str_data.split("~")[0]
                        backup_data = str_data.split(name+"~")[1]

                if code == "CLOG":
                        check_login(splited_str_data,sock)
                elif code == "SUBM":
                        submit(splited_str_data,sock)
                elif code == "GETU":
                        get_user(splited_str_data,sock)
                elif code == "GETK":
                        get_user_key(splited_str_data,sock)
                elif code == "CRTB":
                        create_backup(backup_data,name)
                elif code == "GETB":
                        get_backup(splited_str_data,sock)
                elif code == "CHNP":
                        change_pass(splited_str_data,sock)
                


def wait_for_clients():
        """
        connetcting with socket to client
        main server loop
        1. that accept tcp connection
        2. create thread for each connected new client
        3. wait for all threads
        4. every X clients limit will exit
        """
        threads = []
        srv_sock = socket.socket()
        srv_sock.bind(('0.0.0.0', ROOMS_PORT))
        srv_sock.listen(20)
        srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        i = 1
        while True:
                print('Main thread: before accepting ...')
                cli_sock , addr = srv_sock.accept()
                print(f"Client connected || ip --> {addr} ")
                t = threading.Thread(target = handle_clients, args=(cli_sock,))
                t.start()
                i+=1
                threads.append(t)
                if i > 100000000:     # for tests change it to 4
                        print('Main thread: going down for maintenance')
                        break

        all_to_die = True
        print('Main thread: waiting to all clints to die')
        for t in threads:
                t.join()
        srv_sock.close()
        print( 'Bye ..')


if __name__ == "__main__":
        wait_for_clients()