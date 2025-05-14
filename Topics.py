from os import listdir, path, makedirs, remove
from PyPDF2 import PdfReader, PdfWriter
import yaml

with open("config.yaml", 'r') as file:
    data = yaml.safe_load(file)

bannedpages = data["reviewbanned"].lower().split(",")

class Topic:
    def __init__(self, name, tpath:str):
        self.Name = name
        if not tpath.endswith("/"): tpath += "/"
        self.path = tpath
        
        if path.exists(f"{tpath}topic.yaml"):
            with open(f"{tpath}topic.yaml", 'r') as file:
                self.data = yaml.safe_load(file)

        if path.exists(f"{tpath}icon.png"):
            self.icon = f"{tpath}icon.png"

        self.reload()
        pass

    def reload(self):
        print("reloading data")
        self.pages = []
        self.pnames = []
        self.paths = []
        failed = 0

        if path.exists(self.path):
            print("Has a path")
            dir = listdir(self.path)
            self.pages = [[]] * len(dir)
            self.pnames = [""] * len(dir)
            self.paths = [""] * len(dir)
            for a in dir:
                if not a.endswith(".pdf"):
                    self.pages.pop(-1)
                    self.pnames.pop(-1)
                    self.paths.pop(-1)
                    continue

                with open(f"{self.path}/{a}", 'rb') as file:
                    ## reads the pdf
                    reader = PdfReader(file)
                    metadata = reader.metadata

                    # Extract text from each page
                    pcont = ""
                    for page in reader.pages[2:]:

                        ## Checks if the page is set to be review questions 
                        text =page.extract_text().replace("\n","").replace("■","")

                        if text in bannedpages:
                            break

                        pcont += text

                if "/pos" in metadata:
                    pos = int(metadata["/pos"])-1
                else:
                    failed += 1
                    pos = len(self.pnames)-failed
                
                self.pages[pos] = pcont
                self.pnames[pos] = a
                self.paths[pos] = f"{self.path}/{a}"
            print(f"Amount without positions {failed}")
        else:
            print("Has no path creating one")
            makedirs(self.path)


    def Addfile(self, content, name, position, reload=True):
        if type(content) == str:
            content = open(content, "rb")


        writer = PdfWriter()
        reader = PdfReader(content)

        for page in reader.pages:
            writer.add_page(page)

        print("adding meta data")
        writer.add_metadata({"/pos": str(position)})

        with open(f"{self.path}{name}.pdf", "wb") as file:
            writer.write(file)
        if reload:
            self.reload()
        pass

    def AddFiles(self, contents, names):
        for x in range(len(names)):
            self.Addfile(contents[x], names[x], x,False)
        self.reload()
    
    def RemoveFile(self, name):
        has = False

        for x in self.pnames:
            if name == x[:x.find(".")]:
                has = True
                break

        if has:
            print(f"{name} exists")
            remove(f"{self.path}{name+'.pdf'}")
            self.reload()


topics:list[Topic] = []

def GetAllData():
    return topics

def GetTopicNames():
    return [x.Name for x in topics]

def GetTopic(name):
    for x in topics:
        if x.Name.lower() == name.lower():
            return x
        
def GetChaterNames(topic):
    topic = GetTopic(topic)
    if topic:
        return topic.pnames
    
def GetChaptersContent(topic, chapters:int|list[int]):
    topic = GetTopic(topic)
    dat = []
    if chapters == "all":
        chapters = range(len(topic.pages))
    elif type(chapters) == int:
        chapters = [chapters]
    for x in chapters:
        if x < len(topic.pages) and x > -1:
            dat.append(topic.pages[x])
    return dat

def GetMetadata(topic):
    topic = GetTopic(topic)
    if topic and hasattr(topic,"data"):
        return topic.data
    else:
        return "This Topic has no metadata"

def GetChapterPath(topic:str,chapter:str):
    topic = GetTopic(topic)
    if topic and chapter in topic.pnames:
        return topic.paths[topic.pnames.index(chapter)]
    return "failed"

def LoadData():
    global topics
    topics = []
    for x in listdir(data["topicPath"]):
        topics.append(Topic(x,f"{data['topicPath']}/{x}"))