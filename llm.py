import google.generativeai as genai
from random import shuffle
import re

# Generate a Gemini Key at https://aistudio.google.com/app/apikey
genai.configure(api_key="GEMINI Key")
model = genai.GenerativeModel('gemini-1.5-flash')

def GetGeneral(incorrect):
    if len(incorrect) == 0:
        return "You got every question correct. Couldn't generate a responce"
    text = ""
    for i in incorrect:
        text += i+"\n\n"
    res = model.generate_content("Summarize this to help understand what i need to study up on '"+text+"'")
    return res.text

def CreateQuestions(count="",exam = ""):
    response = model.generate_content(f"Create {count} test questions from the {exam} Exam useing the format 'Questions #: Question' 'Answers:\nOptions' 'Answer' 'Explanation'")
    Questions = []

    split = response.text.splitlines(False)
    answers = False
    for i in split:
        if i.startswith("**Question"):
            qu = re.search(r"\*\*Question \d+:\*\*",i).span()
            Questions.append({"Question":i[qu[1]:].strip(),"Answers":[],"Answer":"","Explanation":""})
        
        if i.startswith("**Explanation:**"):
            Questions[len(Questions)-1]["Explanation"] = i[len("**Explanation:**")-1:].strip().replace(". ",".\n")

        elif i == "**Answers:**":
            answers = True
        elif i.startswith("**Answer:**"):
            answers = False
            shuffle(Questions[len(Questions)-1]["Answers"])
            Questions[len(Questions)-1]["Answer"] = i.replace("**Answer:** ","").strip()[3:].strip()

        elif answers and len(i.strip()[3:]) > 0:
            Questions[len(Questions)-1]["Answers"].append(i.strip()[3:].strip())

    return Questions
