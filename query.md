# Query Development

Here are three variations of the query designed to explore the intersection of computer science education and generative AI, specifically large language models (LLMs) like ChatGPT. Each query builds on the previous one, gradually increasing in complexity and specificity.

## Query 1 (Slim_Jim)

This is the most minimal query, focusing on the intersection of computer science education and generative AI, specifically large language models.

*Subject Domain:*

```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" 
    OR csed OR "cs education" OR "data science" OR "information technology" 
    OR "information systems" OR computer OR computing OR programming OR coding)
```

*Generative-AI:*

```sql
AND ("generative" OR "large language model" OR "large language models" 
    OR "llm" OR "llms" OR "gpt" or "chatgpt")
```

*Pedagogical:*

```sql
AND ("student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers")
```

*Number of hits in ACM DL: 448*

## Query 2 (Mid_Journey)

Here we broaden the scope to include a wider range of generative AI terms, while still focusing on computer science education.

*Subject Domain:*
```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" 
    OR csed OR "cs education" OR "data science" OR "information technology" 
    OR "information systems" OR computer OR computing OR programming OR coding)
```

*Generative-AI:*

```sql
AND ("generative" OR "large language model" OR "large language models" 
    OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" 
    OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" 
    OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex")
```

*Pedagogical:*

```sql
AND ("student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers")
```

*Number of hits in ACM DL: 527*

## Query 3 (Fat_Boy)

Here we really try to focus on the pedagogical aspects of generative AI in computer science education, including course design, assignments, and assessments.

*Subject Domain:*

```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" 
    OR csed OR "cs education"   OR "data science" OR "information technology" 
    OR "information systems" OR computer OR computing OR programming OR coding)
```

*Generative-AI:*

```sql
AND ("generative" OR "large language model" OR "large language models" 
    OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o"  
    OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" 
    OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex")
```

*Pedagogical:*

```sql
AND ("education" OR "teaching" OR "learning" OR "instruction" OR "pedagogy"
    OR "student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers"
    OR "curriculum" OR "course" OR "courses" OR "course design"
    OR "assignment" OR "homework" OR "project" OR "capstone" OR "lab" OR "laboratory" OR "coursework"
    OR "assessment" OR "grading"
    OR "examination" OR "exam"
    OR "learning outcome" OR "learning outcomes"
    OR "learning objective" OR "learning objectives"
    OR "competence" OR "competency" OR "competencies")
```

*Number of hits in ACM DL: 1,768*

## Query in One Line

Slim_Jim:

```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" OR csed OR "cs education" OR "data science" OR "information technology" OR "information systems" OR computer OR computing OR programming OR coding) AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" or "chatgpt") AND ("student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers")
```

Mid_Journey:

```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" OR csed OR "cs education" OR "data science" OR "information technology" OR "information systems" OR computer OR computing OR programming OR coding) AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex") AND ("student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers")
```

Fat_Boy:

```sql
("computer science" OR "cs" OR "computer engineering" OR "software engineering" OR csed OR "cs education"   OR "data science" OR "information technology" OR "information systems" OR computer OR computing OR programming OR coding) AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex") AND ("education" OR "teaching" OR "learning" OR "instruction" OR "pedagogy" OR "student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers" OR "curriculum" OR "course" OR "courses" OR "course design" OR "assignment" OR "homework" OR "project" OR "capstone" OR "lab" OR "laboratory" OR "coursework" OR "assessment" OR "grading" OR "examination" OR "exam" OR "learning outcome" OR "learning outcomes" OR "learning objective" OR "learning objectives" OR "competence" OR "competency" OR "competencies")
```