def build_prompt(req):

 return f"""
You are a senior technical interviewer.

Generate EXACTLY these counts:

Technical: {req.types.technical}
Behavioral: {req.types.behavioral}
Coding: {req.types.coding}
System Design: {req.types.system}

TOTAL MUST = {req.num_questions}

Role: {req.role}
Skills: {req.skills}
Resume: {req.resume}
Difficulty: {req.difficulty}
Experience: {req.experience}

RULES:

• Technical / Behavioral / System Design → MCQ ONLY
• MCQ must contain:
  - type:"mcq"
  - 4 options
  - correct answer (must match option)
  - explanation

• Coding → descriptive ONLY:
  - problem
  - solution

RETURN PURE JSON ONLY:

{{
 "technical":[],
 "behavioral":[],
 "coding":[],
 "system_design":[]
}}

NO EXTRA TEXT.
"""
