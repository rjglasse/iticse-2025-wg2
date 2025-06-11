# Query Development

Here are three variations of the query designed to explore the intersection of computer science education and generative AI, specifically large language models (LLMs) like ChatGPT. Each query builds on the previous one, gradually increasing in complexity and specificity.

Assumptions:

1. We only take papers after 2022
2. We only search the abstract

> Note: If you run these queries and try to export the BiBTeX of the all_results, the ACM DL has a silent cutoff limit of 1000 papers! This is not really documented anywhere.

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

```
Results Summary for ONLY VALID ACM DL DOIs IN VALIDATION SET:
----------------
DOIs in input file: 28
DOIs in BibTeX file: 414
Overlapping DOIs: 22 (78.6%)
Missing DOIs: 6 (21.4%)
```

> Using: [`doi_overlap.py`](doi_overlap.py) with [`validation_set/dois_acm_dl_only.txt`](validation_set/dois_acm_dl_only.txt) and [`bibfiles/acm_slim_jim.bib`](bibfiles/acm_slim_jim.bib).


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

```
Results Summary ONLY ACM DL DOIs IN VALIDATION SET:
----------------
DOIs in input file: 28
DOIs in BibTeX file: 486
Overlapping DOIs: 24 (85.7%)
Missing DOIs: 4 (14.3%) improvement of 7.1%
```

> Using: [`doi_overlap.py`](doi_overlap.py) with [`validation_set/dois_acm_dl_only.txt`](validation_set/dois_acm_dl_only.txt) and [`bibfiles/acm_mid_journey.bib`](bibfiles/acm_mid_journey.bib).

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
```
Results Summary ONLY ACM DL DOIs IN VALIDATION SET:
----------------
DOIs in input file: 28
DOIs in BibTeX file: 1667
Overlapping DOIs: 27 (96.4%)
Missing DOIs: 1 (3.6%) further improvement of 10.7%
```

> Using: [`doi_overlap.py`](doi_overlap.py) with [`validation_set/dois_acm_dl_only.txt`](validation_set/dois_acm_dl_only.txt) and [`bibfiles/acm_fat_boy.bib`](bibfiles/acm_fat_boy.bib).

## Query 4 (Search_String)
This is the final query that combines all the elements from the previous queries, focusing on computer science education, generative AI, and pedagogical aspects. Crucially we use the search engines FULL TEXT for the domain, then the abstract for the generative AI and pedagogical aspects. We also clean up some terms that are either out of scope (data science) or too broad (computer, computing).

```sql
("computer science" OR "computing" OR "computer engineering" OR "software engineering" OR "cs education" OR "csed" OR "cse")
```

```sql
AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex")
```

```sql
AND ("education" OR "teaching" OR "pedagogy" OR "student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers" OR "curriculum" OR "course" OR "courses" OR "course design" OR "assignment" OR "homework" OR "project" OR "capstone" OR "coursework" OR "assessment" OR "grading" OR "examination" OR "exam" OR "learning outcome" OR "learning outcomes" OR "learning objective" OR "learning objectives" OR "competence" OR "competency" OR "competencies" OR "policy" or "policies")
```

*Number of hits in ACM DL: 1,000*

```
Results Summary:
----------------
DOIs in input file: 28
DOIs in BibTeX file: 913
Overlapping DOIs: 25 (89.3%)
Missing DOIs: 3 (10.7%)
```
> Using: [`doi_overlap.py`](doi_overlap.py) with [`validation_set/dois_acm_dl_only.txt`](validation_set/dois_acm_dl_only.txt) and [`bibfiles/acm_search_string.bib`](bibfiles/acm_search_string.bib).

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
("computer science" OR "cs" OR "computer engineering" OR "software engineering" OR csed OR "cs education" OR "data science" OR "information technology" OR "information systems" OR computer OR computing OR programming OR coding) AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex") AND ("education" OR "teaching" OR "learning" OR "instruction" OR "pedagogy" OR "student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers" OR "curriculum" OR "course" OR "courses" OR "course design" OR "assignment" OR "homework" OR "project" OR "capstone" OR "lab" OR "laboratory" OR "coursework" OR "assessment" OR "grading" OR "examination" OR "exam" OR "learning outcome" OR "learning outcomes" OR "learning objective" OR "learning objectives" OR "competence" OR "competency" OR "competencies")
```

Search_String:

```sql
("computer science" OR "computer engineering" OR "software engineering" OR "computing education" OR "cs education" OR "csed" OR "cse") AND ("generative" OR "large language model" OR "large language models" OR "llm" OR "llms" OR "gpt" OR "gpt-3" OR "gpt-3.5" OR "gpt-4" OR "gpt-4o" OR "o1" OR "o3" OR "chatgpt" OR "openai" OR "gemini" OR "bard" OR "claude" OR "copilot" OR "llama" OR "mixtral" OR "deepseek" OR "codex") AND ("education" OR "teaching" OR "pedagogy" OR "student" OR "students" OR "learner" OR "learners" OR "teacher" OR "teachers" OR "curriculum" OR "course" OR "courses" OR "course design" OR "assignment" OR "homework" OR "project" OR "capstone" OR "coursework" OR "assessment" OR "grading" OR "examination" OR "exam" OR "learning outcome" OR "learning outcomes" OR "learning objective" OR "learning objectives" OR "competence" OR "competency" OR "competencies" OR "policy" or "policies")
,,,