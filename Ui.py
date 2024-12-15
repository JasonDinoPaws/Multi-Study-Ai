from tkinter import Tk,Label
import threading
import keyboard
from time import sleep
import llm

topic = ""
topics = ["Comptia A+ Core 1","Comptia A+ Core 2","Comptia Network+"]

window = Tk()
window.configure(background="#000000")
window.wm_title("Shell")
xSize = window.winfo_screenwidth()
ySize = window.winfo_screenheight()
labels = []

def Clear():
    for i in labels:
        i.destroy()

def CreateLabel(Text=""):
    global window,labels

    lav = Label(window,font="Segoe 15",background="#000000",fg="#ffffff",justify="left",text=Text)
    labels.append(lav)
    lav.pack(pady=5,padx=10, anchor="w")
    return lav

def GetAnswer():
    sleep(.5)
    text = ""
    Answer = CreateLabel("Answer: ")
    while True:
        Answer.config(text=f"Answer: {text}")
        window.update()
        key = keyboard.read_key()

        if key == "enter":
            break
        elif key in ["shift","ctrl","alt"]:
            continue

        elif key == "backspace":
            text = text[0:len(text)-1]

        elif key == "space":
            text += " "

        elif key != "":
            text += key

        sleep(.15)
    return text


def Questions():
    amount = 0
    while amount <= 0:
        Clear()
        CreateLabel("How many questions do you want to do?")
        Answer = GetAnswer()
        if Answer.isdigit() and int(Answer) > 0:
            amount = int(Answer)
        else:
            CreateLabel("\nNot a int or above 0")
            sleep(2)
    Clear()
    CreateLabel("Generateing Questions.\nTHis make take a bit")
    questions = llm.CreateQuestions(amount,topic)
    cor = []
    incor = []

    for i in range(len(questions)):
        quest = questions[i]
        answer = 0
        ca = 0

        while answer <= 0:
            alab = []
            Clear()
            CreateLabel(f"Total Correct {len(cor)}/{len(questions)}").config(justify="center",anchor="center")
            CreateLabel(f"Question {i+1}")
            CreateLabel(quest["Question"].replace(". ",".\n")+"\n")

            for a in range(len(quest["Answers"])):
                if len(quest["Answers"][a]) > 1:
                    alab.append(CreateLabel(f"{a+1}: "+quest["Answers"][a]))
                    if quest["Answers"][a] == quest["Answer"][:len(quest["Answers"][a])]:
                        ca = a
            
            Answer = GetAnswer()
            if Answer.isdigit() and int(Answer) > 0 and int(Answer) <= len(quest["Answers"]):
                answer = int(Answer)
                alab[answer-1].config(fg="#0000ff")
            else:
                CreateLabel("\nNot a option try again")
                sleep(2)
        

        if quest["Answer"][:len(quest["Answers"][answer-1])] == quest["Answers"][answer-1]:
            cor.append(i)
            alab[ca].config(fg="#00ffff")
        else:
            alab[ca].config(fg="#00ff00")
            incor.append(quest["Question"])
        
        CreateLabel(f"\nExpanation\n{quest['Explanation']}")
        window.update()
        CreateLabel("\nPress enter to go to the next question")
        GetAnswer()

    Clear()
    for i in ["Results",f"Total Correct {len(cor)}",f"Total Incorrect {len(incor)}",llm.GetGeneral(incor).replace(". ",".\n")]:
        sleep(1)
        CreateLabel(i)
        window.update()
    CreateLabel("\nPress enter to choose a option")
    GetAnswer()
    ChooseTopic()

        

        

def ChooseTopic():
    global topic
    topic = ""
    while topic == "":
        Clear()
        CreateLabel("Choose a Topic\n")
        for i in range(len(topics)):
            CreateLabel(f"{i}: {topics[i]}")
        window.update()

        Answer = GetAnswer()
        if Answer.isdigit() and int(Answer) > -1 and int(Answer) < len(topics):
            topic = topics[int(Answer)]
        else:
            CreateLabel("\nNot a option try again")
            sleep(2)
    Questions()
    
    
thr = threading.Thread(target=ChooseTopic)
thr.start()
window.mainloop()