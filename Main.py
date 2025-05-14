from flask import Flask,render_template, jsonify, Response, send_file, request
from os import listdir, path, geteuid
import random
from AiCom import LoadAi
import Users
import Topics
import yaml
import requests

app = Flask(__name__)
isSudo = geteuid() == 0

#Loading
with open("config.yaml", 'r') as file:
    data = yaml.safe_load(file)
    for x in data["banned_username_lists"]:
        blist = requests.get(x)
        data["banned_usernames"] += blist.text.split("\n")[:-1]

Topics.LoadData()
Users.LoadUsers()
ai = LoadAi(data["model"],data["system"],data)

# Website Look
fileredirects = {
    "home": "home.html",
    "login": "login.html",
    "questions": "questions.html",
    "settings": "settings.html",
    "usr": "usr.html",
    "leaderboard": "leaderboard.html",
    "results": "results.html",
    "reader": "reader.html",
}


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<path:web>")
def files(web=""):
    for x in data["banned_paths"]:
        if x.lower() in web.lower():
            return "YOU FAILLED"
        
    file = ""
    if web in fileredirects:
        file = fileredirects[web]
    else:
        fname,ext = path.splitext(f"{web}")
        if web.find("/") == -1:
            web = f"templates/{fname}{ext}"

        if path.exists(f"{web}"):
            file = web

    if file != "":
        _,ext = path.splitext(f"{file}")

        match ext[1:]:
            case "html":
                return render_template(file)
            case _:
                return send_file(file, as_attachment=True)
            
    return "failed"
        
@app.route("/get/<key>")
def Getdata(key:str):
    if key in data:
        return jsonify(data[key])
    return jsonify(f"{key} does not exists in the config file") 

# Login Stuff
@app.route("/login/valid/empas", methods=['POST'])
def attemptlogin() -> bool:
    jdata = request.get_json()
    email = jdata.get('email')
    password = jdata.get('pass')

    if not email.find("@") or not email[email.find("@"):] in data["validemails"] or email.find(" "):
        return "SyntaxError: Not a valid email"
    
    if len(email[:email.find("@")]) > 20:
        return "ValueError: email is to long"
    elif len(password) > 20:
        return "ValueError: Passowrd is to long"
    valid = Users.ValidateLogin(email,password)

    return jsonify(valid)

@app.route("/login/create/", methods=['POST'])
def CreateAccount() -> bool:
    jdata = request.get_json()
    name = jdata.get('name')
    email:str = jdata.get('email')
    password = jdata.get('pass')
    
    if email.find("@") == -1 or not email[email.find("@"):] in data["validemails"] or email.find(" ") != -1:
        return "SyntaxError: Not a valid email"
    
    if name in data["banned_usernames"]:
        if random.randint(1,int(data["ai_insult_chance"])) == 1:
            return ai.Insulte(f"A user is trying to make a username using not school appropriate words.")
        return data["banned_message"]
    
    if len(name) > 20:
        return "ValueError: Username is to long"
    elif len(email[:email.find("@")]) > 20:
        return "ValueError: email is to long"
    elif len(password) > 20:
        return "ValueError: Passowrd is to long"
    

    valid = Users.CreateUser(name,email,password)

    return jsonify(valid)

@app.route("/login/sesson/<email>")
def createsessionid(email:str) -> str:
    usr = Users.GensessionId(email)
    return jsonify(usr)

@app.route("/login/valid/session", methods=['POST'])
def sessionvalid() -> str:
    jdata = request.get_json()
    sess = jdata.get('sess')
    email = jdata.get('email')
    valid = Users.CheckSessionId(sess,email)
    print(jdata)
    print(valid)
    return jsonify(valid)

# Users
@app.route("/usr/getuser/<email>")
def GetUser(email:str) -> Users.User:
    return Users.FindUser(email,"User")

@app.route("/usr/update/<topic>/", methods=['POST'])
def usr_update_topic(topic:str):
    jdata = request.get_json()
    sess = jdata.get('sess')
    email = jdata.get('email')
    tpye = jdata.get('type')
    questions = jdata.get('qdata')
    answers = jdata.get('answerd')
    print(sess,email,Users.CheckSessionId(sess,email))
    if Topics.GetTopic(topic) != None and Users.CheckSessionId(sess,email):
        newdata = data["Topicdatatmp"].copy()
        newdata["Total"] = len(questions)
        for x in range(len(questions)):
            ya = chr(answers[x] + 97).upper()
            if ya == questions[x]["Answer"]:
                newdata["Correct"] += 1
            else:
                newdata["Wrong"] += 1

        if tpye == "practice":
            newdata["PractPrecent"] = int((newdata["Correct"]/newdata["Total"])*100)

        print(newdata)
        Users.UpdateTopic(email,topic,newdata)
        return "sucess"
    return "error"



# Topics
@app.route("/topic/get_names")
def GetTopics():
    return Topics.GetTopicNames()

@app.route("/topic/get_all")
def GetTopicsAll():
    topics = {}
    for x in Topics.GetTopicNames():
        topics[x] = [Topics.GetChaterNames(x),Topics.GetTopic(x).icon]
    return jsonify(topics)

@app.route("/topic/<topic>/get_names")
def GetTopicChapter(topic:str):
    return Topics.GetChaterNames(topic)

@app.route("/topic/<topic>/get_icon")
def GetTopicIcon(topic:str):
    top = Topics.GetTopic(topic)
    if "icon" in top.__dict__:
        return top.icon
    return ""

@app.route("/topic/<topic>/get_metadata")
def GetTopicMetadata(topic:str):
    top = Topics.GetTopic(topic)
    if data in top.__dict__:
        return top.data
    return {}

@app.route("/topic/get_pdf", methods=['POST'])
def GetPdf():
    jdata = request.get_json()
    topic = jdata.get('topic')
    chapter = jdata.get('chap')
    return Topics.GetChapterPath(topic,chapter)


# Ai realted things
@app.route("/Ai/Gen_Questions/", methods=['POST'])
def QuestionGen():
    jdata = request.get_json()
    topic = jdata.get('topic') if "topic" in jdata else "ITF+"
    topicdata = Topics.GetMetadata(topic)
    amount = jdata.get('amount') or str(topicdata.get("QuestionCount"))
    diff = jdata.get('cdiff') or "Exam"
    chaps = jdata.get('chaps') or "all"

    if not amount.isdigit():
        return "TypeError: amount of questions is not a number"
    elif int(amount) > 99 or int(amount) < 1:
        return "ValueError: Amount of questions not in range of 1 to 99"
    elif diff != "Exam" and not diff in data["Difficultys"]:
        return "IndexError: Not a valid difficulty"
    
    questions = ai.GenQuestions(int(amount),diff,Topics.GetChaptersContent(topic,chaps))
    return jsonify(questions)

@app.route("/Ai/Analyze", methods=['POST'])
def Analyze():
    jdata = request.get_json()
    questions = jdata.get('qdata') or ""
    answers = jdata.get('answerd') or ""

    if type(questions) != list or type(answers) != list:
        return "TypeError: Either Questions or answers is not the in proper format"
    elif len(questions) != len(answers):
        return "ValueError: The length of questions does not eual the length of answers"
    
    for x in range(len(answers)):
        questions[x]["Correct_Answer"] = questions[x]["Answer"]
        questions[x]["User_Answer"] = chr(answers[x] + 97).upper()

    responce = ai.AnalyzeData(questions)
    return responce

if __name__ == "__main__":
    # input("Start?")
    app.run(host='0.0.0.0', debug=False, port="443" if isSudo else "5000", threaded=True)