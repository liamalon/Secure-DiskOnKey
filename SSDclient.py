__author__ = "Liam Alon"
__date__ = "25/02/2022"
import os
import threading
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.text import LabelBase    
import socket



import sys

###  To import libs from Asset folder ###
sys.path.insert(3, 'Asset')
from encrypt import encrypt,decrypt,cleanup
from zip import zip_all,unzip_all
from tcp_by_size import recv_by_size,send_with_size

###  Register font pack for labels  ###
LabelBase.register(name= "txt_font",
    fn_regular= "Asset\\orange juice 2.0.ttf")

###  Server IP (currently set to 127.0.0.1 for usage in the same computer) ###
SERVER_IP = "127.0.0.1"

###  Server PORT (currently set to 4444 if you want to change remember to do it in the server as well) ###
SERVER_PORT = 4444

###  Sock veribale for communication ###
sock = socket.socket()

###  Set thread for later usage with file unzipping ###
t= threading.Thread()

class CreateAccountWindow(Screen):
    """
        --> Create new account page <--
            --> For new users <--
    """
    namee = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        """
        --> If submit button pressed it collects all the data and sends it to the server <--
        """
        global t
        if self.namee.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password != "":

                len_data = str(len(self.email.text.encode() +b"~"+ self.password.text.encode() +b"~"+ self.namee.text.encode()+b"###")).zfill(16)

                print(len_data)

                sock.send(b"SUBM~"+len_data.encode()+b"~"+self.email.text.encode() +b"~"+ self.password.text.encode() +b"~"+ self.namee.text.encode()+b"###")

                len_data = str(len(self.email.text.encode()+b"###")).zfill(16)

                sock.send(b"GETK~"+len_data.encode()+b"~"+self.email.text.encode()+b"###")

                key = sock.recv(1024)

                key = key.decode()

                t= threading.Thread(target=encrypt, args=(key,))

                t.start()

                ziping()    

                self.reset()

                sm.current = "login"

            else:
                invalidForm()
        else:
            invalidForm()

    def login(self):
        """
        --> If login button pressed it redirects the page to the login page <--
        """
        self.reset()
        sm.current = "login"

    def reset(self):
        """
        --> Resets input fields <--
        """
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""


class LoginWindow(Screen):
    """
        --> Login account page <--
        --> For existing users <--
    """
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        global t
        """
        --> If login btn was clicked it checks if user exists with the server <--
        """
        if t.is_alive() == False:
            len_data = str(len(self.email.text.encode() + b"~" +  self.password.text.encode()+b"###")).zfill(16)

            sock.send(b"CLOG~"+len_data.encode()+b"~"+self.email.text.encode() + b"~" +  self.password.text.encode()+b"###")

            valid = sock.recv(1024)
            if valid ==b"True":
                MainWindow.current = self.email.text

                len_data = str(len(self.email.text.encode()+b"###")).zfill(16)

                sock.send(b"GETK~"+len_data.encode()+b"~"+self.email.text.encode()+b"###")

                key = sock.recv(1024)

                key = key.decode()

                t= threading.Thread(target=decrypt, args=(key,))

                t.start()

                unziping()


                self.reset()
                sm.current = "main"
            else:
                invalidLogin()
        else:
            zip_not_done()

    def createBtn(self):
        """
        --> Create a new account <--
        """
        self.reset()
        sm.current = "create"

    def reset(self):
        """
        --> Resets input fields <--
        """
        self.email.text = ""
        self.password.text = ""

class MainWindow(Screen):
    """
        --> Main page <--
        --> When a user logs in <--
    """
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""

    def logOut(self):
        """
        --> If logout btn was pressed it zips all files and exits main window <--
        """
        len_data = str(len(self.current+"###")).zfill(16)

        sock.send(b"GETK~"+ len_data.encode() + b"~" + self.current.encode()+b"###")
        print("logging out")

        key = sock.recv(1024)

        key = key.decode()

        t= threading.Thread(target=encrypt, args=(key,))

        t.start()

        ziping()

        sm.current = "login"

    def create_backup(self):
        """
        --> To create backup in the server <--
        """

        print("Creating backup")

        CURRENT_DISK =  os.getcwd().split("\\")[0] +"\\"

        zip_all(CURRENT_DISK,"BACKUP")

        with open(CURRENT_DISK+"BACKUP.zip" , "rb") as zip_to_read:
            file_data = zip_to_read.read()
        
        file_data = file_data.decode("IBM437")

        len_data = str(len(b"~"+self.current.encode() + file_data.encode("IBM437") + b"###")).zfill(16)

        sock.send(b"CRTB~" + len_data.encode() + b"~"+self.current.encode()+b"~" + file_data.encode("IBM437") + b"###")

        cleanup("BACKUP.zip")

    def create_backup_zip(self):
        """
        --> Creats backup in a thread to not slow down the main thread <-- 
        """

        t= threading.Thread(target=self.create_backup, args=())

        t.start()

        creating_backup()


    
    def get_backup(self):
        """
        --> Gets backup from server <-- 
        """

        print("Getting backup")

        len_data = str(len(self.current.encode()+b"###")).zfill(16)

        sock.send(b"GETB~"+ len_data.encode() + b"~" + self.current.encode()+b"###")

        data  = recv_backup()

        with open(f"Backup.zip","wb") as write_zip:
                write_zip.write(data.encode("IBM437"))

        CURRENT_DISK =  os.getcwd().split("\\")[0] +"\\"


    def get_backup_zip(self):
        """
        --> Gets backup from server in a thread to not slow down the main thread <-- 
        """

        t= threading.Thread(target=self.get_backup, args=())

        t.start()

        getting_backup()




    def changePassword(self):
        """
        --> Changes window to change password window <--
        """
        sm.current = "cpass"
        

    def on_enter(self, *args):

        """
        --> Sets the page before it is up <--
        """

        len_data = str(len(self.current.encode()+b"###")).zfill(16)

        sock.send(b"GETU~"+len_data.encode()+b"~"+self.current.encode()+b"###")

        encoded_user_info = sock.recv(1024)

        decoded_user_info = encoded_user_info.decode()

        splited_user_info = decoded_user_info.split("~")

        password = splited_user_info[0]

        name = splited_user_info[1]

        created = splited_user_info[2]

        self.n.text = "Account Name: " + name

        self.email.text = "Email: " + self.current

        self.created.text = "Created On: " + created

def recv_backup():
    """
    --> Recvs backup from server <--
    """
    code = sock.recv(5)
    code = code.decode()[:4]
    str_data = recv_by_size(sock)
    str_data = str_data.decode("IBM437")
    str_data = str_data.split("###")[0]
    name = str_data.split("~")[0]
    backup_data = str_data.split(name+"~")[1]
    return backup_data


class ChangePassword(Screen):
    """
    --> Change password page <--
    """
    old_password = ObjectProperty(None)
    password = ObjectProperty(None)

    def changepassbtn(self):
        """
        --> If pressed check if passwords are correct with server and and if it is sends new password <--
        """

        len_data = str(len(MainWindow.current.encode()+b"~"+self.old_password.text.encode()+b"~"+self.password.text.encode()+b"###")).zfill(16)

        print(len_data)

        print(MainWindow.current)

        sock.send(b"CHNP~"+len_data.encode()+b"~"+MainWindow.current.encode()+b"~"+self.old_password.text.encode()+b"~"+self.password.text.encode()+b"###")
        
        print("sent")

        Is_oldpass_ok = sock.recv(1024)

        if Is_oldpass_ok == b"bad password":
            badPassword()

        else:
            

            self.reset()

            sm.current = "main"
        
    def reset(self):
        """
        --> Resets input fields <--
        """
        self.old_password.text = ""
        self.password.text = ""

    def back_to_main(self):
        """
        --> Redirects back to main page <--
        """
        self.reset()
        sm.current = "main"

class WindowManager(ScreenManager):
    pass

def invalidLogin():
    """
    --> Popup if login isn't good <--
    """
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()
    
def badPassword():
    """
    --> Popup if password doesn't match <--
    """
    pop = Popup(title='Invalid Password',
                  content=Label(text='Invalid password. Please try again'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def ziping():
    """
    --> Popup when zipping files<--
    """
    pop = Popup(title='Files are zipping',
                  content=Label(text='The files are zipping it might take a while...'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def unziping():
    """
    --> Popup when unzipping files<--
    """
    pop = Popup(title='Files are unziping',
                  content=Label(text='The files are unziping it might take a while...'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def invalidForm():
    """
    --> Popup when there are invild inputs <--
    """
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()

def zip_not_done():
    """
    --> Popup when it didnt finish zipping <--
    """
    pop = Popup(title='Files are not finished zipping',
                  content=Label(text='The files are not finished zipping \n Please wait'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def creating_backup():
    """
    --> Popup when creating backup <--
    """
    pop = Popup(title='Creating backup',
                  content=Label(text='Backup is being created '),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def getting_backup():
    """
    --> Popup when getting backup <--
    """
    pop = Popup(title='Getting backup',
                  content=Label(text='Backup is being restored '),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

kv = Builder.load_file("Asset\\my.kv")

sm = WindowManager()



screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"),MainWindow(name="main"),ChangePassword(name="cpass")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyMainApp(App):
    """
    --> Main app <--
    """
    def build(self):
        return sm

def connect_to_server():
    """
    --> Connetcting to server <--
    """
    global sock
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f'Connect succeeded {SERVER_IP}:{SERVER_PORT}')
        connected = True
    except:
        print(f'Error while trying to connect.  Check ip or port -- {SERVER_IP}:{SERVER_PORT}')

def startApp():
    """
    --> Starts the app <--
    """
    connect_to_server()
    MyMainApp().run()

if __name__ == "__main__":
    startApp()

     