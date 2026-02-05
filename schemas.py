from pydantic import BaseModel
from typing import List

class Q(BaseModel):
    type:str="mcq"
    question:str
    options:List[str]=[]
    answer:str=""
    explanation:str=""
    difficulty:str=""

class Coding(BaseModel):
    problem:str
    solution:str

class Response(BaseModel):
    technical:List[Q]=[]
    behavioral:List[Q]=[]
    coding:List[Coding]=[]
    system_design:List[Q]=[]
