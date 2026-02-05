from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import json
from fpdf import FPDF

from model import generate_questions
from prompt import build_prompt
from schemas import Response

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Types(BaseModel):
    technical:int=0
    behavioral:int=0
    coding:int=0
    system:int=0

class Req(BaseModel):
    role:str
    skills:str
    resume:str=""
    difficulty:str
    experience:str
    types:Types
    num_questions:int


@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/history")
def hist():
    return FileResponse("static/history.html")

@app.post("/generate")
def gen(r: Req):

 r.num_questions = max(4, min(r.num_questions, 20))

 raw = generate_questions(build_prompt(r))

 if "technical" not in raw:
  raw = {
   "technical": raw if isinstance(raw,list) else raw.get("questions",[]),
   "behavioral": [],
   "system_design": [],
   "coding": []
  }

 def fix(section):
  out=[]
  for q in raw.get(section,[]):

   options=[str(x).strip() for x in q.get("options",[])]
   answer=str(q.get("answer","")).strip()

   try:
    correct_index=options.index(answer)
   except:
    correct_index=0

   out.append({
    "question":str(q.get("question","")),
    "options":options,
    "correct_index":correct_index,
    "answer":options[correct_index] if options else "",
    "explanation":str(q.get("explanation","")),
    "difficulty":str(q.get("difficulty",""))
   })

  return out

 def fix_coding():
  return [{
   "problem":str(q.get("problem","")),
   "solution":str(q.get("solution",""))
  } for q in raw.get("coding",[])]

 cleaned={
  "technical":fix("technical"),
  "behavioral":fix("behavioral"),
  "system_design":fix("system_design"),
  "coding":fix_coding()
 }

 validated = Response(**cleaned)

 entry={
  "time":datetime.now().strftime("%Y-%m-%d %H:%M"),
  "data":validated.dict()
 }

 try:
  h=json.load(open("history.json"))
 except:
  h=[]

 h.append(entry)
 json.dump(h,open("history.json","w"),indent=2)

 return validated.dict()



@app.get("/api/history")
def api():
    try:
        return json.load(open("history.json"))
    except:
        return []

@app.get("/generate-pdf")
def pdf():

 h=json.load(open("history.json"))
 d=h[-1]["data"]

 pdf=FPDF()
 pdf.set_auto_page_break(auto=True,margin=15)
 pdf.add_page()

 # TITLE
 pdf.set_font("Arial","B",18)
 pdf.cell(0,10,"AI Interview Questions",ln=1)
 pdf.ln(5)

 def section(title):
  pdf.set_font("Arial","B",15)
  pdf.cell(0,10,title.upper(),ln=1)
  pdf.ln(2)

 qnum=1

 # ========= TECH / BEHAV / SYSTEM =========
 for sec in ["technical","behavioral","system_design"]:

  if not d.get(sec): 
   continue

  section(sec.replace("_"," "))

  for q in d[sec]:

   pdf.set_font("Arial","B",11)
   pdf.multi_cell(0,7,f"Q{qnum}. {q['question']}")
   pdf.set_font("Arial",size=11)

   for i,opt in enumerate(q.get("options",[])):
    letter=chr(65+i)
    pdf.multi_cell(0,6,f"   {letter}. {opt}")

   pdf.ln(1)
   pdf.set_font("Arial","B",11)
   pdf.multi_cell(0,6,f"Correct Answer: {q['answer']}")

   pdf.set_font("Arial",size=11)
   pdf.multi_cell(0,6,f"Explanation: {q['explanation']}")
   pdf.ln(4)

   qnum+=1

 # ========= CODING =========
 if d.get("coding"):

  section("CODING")

  for q in d["coding"]:

   pdf.set_font("Arial","B",11)
   pdf.multi_cell(0,7,f"Q{qnum}. {q['problem']}")

   pdf.set_font("Arial",size=11)
   pdf.multi_cell(0,6,"Solution:")
   pdf.multi_cell(0,6,q["solution"])
   pdf.ln(5)

   qnum+=1

 pdf.output("questions.pdf")

 return FileResponse("questions.pdf",filename="InterviewQuestions.pdf")
