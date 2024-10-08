# ia-group1-health-onotology
This is where the developing ontology for our health-related Intelligent Agents project is kept up-to-date.

Current state of development:
- Classes all implemented;
- Properties all implemented and
- Individuals being processed.

# The code
## Running the code
Add the following to your .env file:
```
ANTHROPIC_API_KEY=<your-key>
```

I an give you a key if you promise not to abuse it 🙏. But make sure you dont push it to the repo.

```
python main.py
```

## Short Overview

The code is split into three files:
- llm_check.py (done)
- ontology_check.py (todo)
- utils.py
- main.py (doneish)

__llm_check.py__ is a file that contains the code for the LLM check. It is used to check the truth of a statement using an LLM.

__ontology_check.py__ is a file that contains the code for the ontology check. It is used to check the truth of a statement using the ontology.

__utils.py__ is a file that contains the code for the utils. It is used to check the truth of a statement using the ontology.

__main.py__ is the file that is used to run the code. It is the entry point of the code and performs the checks and returns the appropriate response.