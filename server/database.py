import datetime
import hashlib

class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.users = None
        self.file = None
        self.user_key = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r")
        self.users = {}

        for line in self.file:
            if len(line) > 1:
                email, password, name, created,key,salt = line.strip().split(";")
                self.users[email] = (password, name, created,key,salt)

        self.file.close()

    def get_key(self, email):
        """
        --> Get user key <--
        """
        if email in self.users:
            return self.users[email][3]

    def get_user(self, email):
        if email in self.users:
            return self.users[email]
        else:
            return -1

    

    def add_user(self, email, password, name,key,salt):
        """
        --> Adds user to database <--
        """
        if email.strip() not in self.users:
            add_salt_to_real = password.strip()+salt
            self.users[email.strip()] = (hashlib.sha256(add_salt_to_real.encode('utf-8')).hexdigest(), name.strip(), DataBase.get_date(),key,salt)
            self.save()
            return 1
        else:
            print("Email exists already")
            return -1

    def validate(self, email, password):
        """
        --> Returns True or False if the password is correct or not <--
        """
        if self.get_user(email) != -1:
            add_salt_to_check = password+self.users[email][4]
            print(password,self.users[email][4] , add_salt_to_check,hashlib.sha256(add_salt_to_check.encode('utf-8')).hexdigest() )
            print(self.users[email][0])
            return self.users[email][0] == hashlib.sha256(add_salt_to_check.encode('utf-8')).hexdigest() 
        else:
            return False
    
    def change_pass(self, email,password):
        """
        --> Changes the password of the user <--
        """
        if email in self.users:
            print(self.users[email]) 
            to_list = list(self.users[email])
            to_list[0] = password
            self.users[email] = tuple(to_list)
            print(self.users[email])   
            self.save() 

        else:
            return -1

    def save(self):
        """
        --> Save data in the database file <--
        """
        with open(self.filename, "w") as f:
            for user in self.users:
                f.write(user + ";" + self.users[user][0] + ";" + self.users[user][1] + ";" + self.users[user][2]+";" + self.users[user][3] +";" + self.users[user][4]+ "\n")

    @staticmethod
    def get_date():
        """
        --> Get current date for date of creation <--
        """
        return str(datetime.datetime.now()).split(" ")[0]