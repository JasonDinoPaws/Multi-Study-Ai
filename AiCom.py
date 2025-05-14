import ollama
from ast import literal_eval

class LoadAi:
    def __init__(self, Model:str,Systemprompt:str="",extradata:dict={}):
        for x in ollama.list()["models"]:
            if x["model"].startswith(Model):
                break
        else:
            raise KeyError(f"{Model} isn't installed or isn't spelt correctly. If you have the model you can run `ollama list` to view all of your models. if you don't have it, run `ollana run {Model}` to install it")
        self.model = Model
        self.system = Systemprompt
        self.extra = extradata

    
    def GenQuestions(self,amount:int,difficulty:int,content:str) -> list[dict]: 
        history = [
            {'role': 'system', 'content': self.system},
            {'role': 'user', 'content': f'''
                {content}

                Generate {int(amount)} {difficulty} questions using the above text.

                Here is a list of requirements:
                {self.extra['QuestionRequirement']}
                - It must be in the format: {self.extra['QuestionFormat']}.

                Here's an example of a question with the requrements: {self.extra['ExampleQuestion']}.
                '''},
            ]
        chat:str = ollama.chat(model=self.model, messages=history)['message']['content']
        questions = []
        for x in range(int(amount)):
            opn = chat.index("{")
            clo = chat.index("}")
            text= chat[opn:clo+1].replace("'", '"')
            print(text)
            questions.append(literal_eval(text))
            chat = chat[clo+1:]
        return questions
    
    def AnalyzeData(self,data:str|list[str]) -> str:
        history = [
                {'role': 'system', 'content': self.system},
                {'role': 'user', 'content': f'''
                    {self.extra['Analyzefromat']}
                    Data: {data}
                '''},
                ]
        return ollama.chat(model=self.model, messages=history)['message']['content']
    
    def Explanation(self,data:str|list[str]) -> str:
        history = [
                {'role': 'system', 'content': self.system},
                {'role': 'user', 'content': f'''
                    Explain this piece(s) of data.
                    {data}
                '''},
                ]
        return ollama.chat(model=self.model, messages=history)['message']['content']
    
    def Insulte(self,data:str) -> str:
        history = [
                {'role': 'system', 'content': self.system},
                {'role': 'user', 'content': f'''
                    Create a extremely uniqe Insulte based on this data.
                    {data}
                '''},
                ]
        return ollama.chat(model=self.model, messages=history)['message']['content']