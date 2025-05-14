from os import listdir, path, makedirs, remove
import yaml
from blake3 import blake3
from typing import Literal
import secrets
import base64

with open("config.yaml", 'r') as file:
    data = yaml.safe_load(file)

Users = []
class User:
    def __init__(self,user:str):
        if not user.endswith(".json"):
            user += ".json"

        self.path = f"{data['userPath']}/{user}"
        userdata = {}
        if path.exists(self.path):
            with open(self.path,"r") as file:
                dat = file.read()
                userdata = {}
                if len(dat) > 0:
                    userdata = eval(dat)

        for x in data["Usertemp"].keys():
            self.__dict__[x] = x in userdata and userdata[x] or data["Usertemp"][x]
        pass

    def Save(self):
        with open(self.path,"w") as file:
            file.write(str({k: v for k, v in self.__dict__.items() if k != "path"}))

    def GetData(self,name):
        if name in self.__dict__:
            return self.__dict__[name]

    def ChangeData(self,newdata:dict):
        for x in newdata.keys():
            if x in self.__dict__ and type(newdata[x]) == type(self.__dict__[x]):
                self.__dict__[x] = newdata[x]
        self.Save()
    
    def TopicData(self,topic,newdata:dict):
        if not topic in self.data:
            self.data[topic] = data["Topicdatatmp"].copy()

        for x in newdata.keys():
            if x in self.data[topic] and type(newdata[x]) == type(self.data[topic][x]):
                print(x)
                self.data[topic][x] = newdata[x]
        self.Save()
    
    def delete(self):
        remove(self.path)


def LoadUsers():
    for x in listdir(data['userPath']):
        Users.append(User(x))
    
def ListUsers():
    names = []
    for x in Users:
        names.append(x.Username)

def FindUser(email,retype:str) -> int|bool|User:
    for x in range(len(Users)):
        if Users[x].Email == email: 
            match retype:
                case "User":
                    return Users[x]
                case "pos":
                    return x
                case "bool":
                    return True
                
    return retype != "User" and False

def EncryptPass(password:str):
    pashash = blake3(password.encode())
    return pashash.hexdigest()

def CreateUser(name,email:str,passowrd):
    if not FindUser(email,"bool"):
        usr = User(email[:email.find("@")])
        usr.ChangeData({"Username":name,"Email":email,"Password":EncryptPass(passowrd)})
        usr.Save()
        Users.append(usr)
        return True
    return False

def DeleteUser(email):
    usr = FindUser(email,"pos")
    if usr > -1:
        Users.pop(usr).delete()

def ValidateLogin(email,passw) -> bool:
    usr = FindUser(email,"User")
    if usr:
        return usr.GetData("Password") == EncryptPass(passw)
    return False

def GensessionId(email):
    random_bytes = secrets.token_bytes(32)
    session_id = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode('ascii')
    usr = FindUser(email,"User")
    usr.ChangeData({"session": session_id})
    usr.Save()
    return session_id

def CheckSessionId(sessonid,email):
    usr = FindUser(email,"User")
    if usr:
        return usr.GetData("session") == sessonid
    return False

def Save(users:list[str]|str):
    if type(users) == str:
        users = [users]
    for x in users:
        usr = FindUser(x,"User")
        print(usr)
        if usr:
            usr.Save()

def UpdateTopic(email,topic,Newdata):
    usr = FindUser(email,"User")
    if usr:
        usr.TopicData(topic,Newdata)

