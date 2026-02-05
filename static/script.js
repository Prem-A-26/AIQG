function toggleTheme(){
 document.body.classList.toggle("light");
 document.body.classList.toggle("dark");
}

// distribute questions evenly
function distribute(total,selected){
 let base=Math.floor(total/selected);
 let extra=total%selected;
 return Array(selected).fill(base).map((v,i)=>i<extra?v+1:v);
}

async function generate(){

 // REQUIRED FIELD VALIDATION
 if(!role.value || !skills.value || !difficulty.value || !experience.value){
  alert("Please fill all required fields.");
  return;
 }

 const selected=[technical,behavioral,coding,system].filter(x=>x.checked);

 if(selected.length===0){
  alert("Select at least one category.");
  return;
 }

 const total=Number(num.value);

 if(total<4 || total>20){
  alert("Questions must be between 4 and 20.");
  return;
 }

 // DISTRIBUTE COUNTS
 const counts=distribute(total,selected.length);

 const types={
  technical:0,
  behavioral:0,
  coding:0,
  system:0
 };

 selected.forEach((c,i)=>types[c.id]=counts[i]);

 loader.style.display="flex";
 output.innerHTML="";
 results.style.display="none";
 pdfBtn.style.display="none";

 const payload={
  role:role.value,
  skills:skills.value,
  resume:resume.value||"",
  difficulty:difficulty.value,
  experience:experience.value,
  types:types,
  num_questions:total
 };

 const r=await fetch("/generate",{
  method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify(payload)
 });

 const data=await r.json();

 loader.style.display="none";
 results.style.display="block";

 let qCount=1;

 for(const section in data){

  if(!data[section].length) continue;

  output.innerHTML+=`<h3>${section.replace("_"," ").toUpperCase()}</h3>`;

  data[section].forEach(q=>{

// ===== MCQ QUESTIONS =====
if(q.options){

 const id=Math.random();

 const correctIndex =
  q.options.findIndex(o =>
   o.trim().toLowerCase() === q.answer.trim().toLowerCase()
  );

 output.innerHTML+=`
 <div class="result">
  <b>Q${qCount++}. ${q.question}</b>

  ${q.options.map((o,i)=>`
   <div class="option" onclick="select(this,${i},${correctIndex})">${o}</div>
  `).join("")}

  <button class="show-btn" onclick="toggleAnswer('${id}')">Show Answer</button>

  <div id="${id}" class="answer-box">
   <b>Correct:</b> ${q.answer}
   <div class="explanation">${q.explanation}</div>
  </div>
 </div>`;
}


// ===== CODING QUESTIONS =====
else if(q.problem){

 output.innerHTML+=`
 <div class="result">
  <b>Q${qCount++}. ${q.problem}</b>

  <button class="show-btn" onclick="this.nextElementSibling.style.display='block'">
   Show Solution
  </button>

  <div class="answer-box">
   <pre>${q.solution}</pre>
  </div>
 </div>`;
}

});

 }

 pdfBtn.style.display="inline-block";
 results.scrollIntoView({behavior:"smooth"});
}


// OPTION CLICK HANDLER (FINAL FIX)
function select(el, idx, correct){

 const options = el.parentElement.querySelectorAll(".option");

 // clear previous
 options.forEach(o=>o.classList.remove("correct","wrong"));

 // highlight correct
 if(correct >= 0){
  options[correct].classList.add("correct");
 }

 // mark wrong click
 if(idx !== correct){
  el.classList.add("wrong");
 }
}

function toggleAnswer(id){
 const box=document.getElementById(id);
 box.style.display=box.style.display==="block"?"none":"block";
}

function downloadPDF(){
 window.open("/generate-pdf");
}
