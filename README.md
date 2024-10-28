# ia-group1-health-onotology
## Demo
Since the full agent requires an API key to run the LLM check, a demo is attached with the submission. 

# The code
## Running the code
1. If you want to use the LLM check, add the following to your .env file:
```
ANTHROPIC_API_KEY=<your-key>
```

2. Run the code with:
```
python main.py
```
3. The code can be run with the following flags:
- To run the agent without the LLM check, this will remove the need for the ANTHROPIC_API_KEY but the response will only be based on the ontology.
```
python main.py --no-llm
```
- To run the agent with verbose output, this will print the SPARQL query and the response from the ontology.
```
python main.py --verbose
```
4. The agent recognizes the following query types:
- Does eating ***Recipe*** cause ***Health***?
- Can not being able to (play|perform|do) ***Sport*** be caused by (playing|performing|doing) ***Sport***?
- Does (playing|performing|doing) ***Sport*** provide any health benefit that is not provided by (playing|performing|doing) ***Sport***?
- Does ***Recipe*** provide the required nutrients for (playing|performing|doing) ***Sport***?
- Can someone with a(n) ***Allergy*** eat ***Recipe***?
- Does eating ***Recipe*** help against (a(n)) ***Symptom*** (and (a(n)) ***Symptom***)?
- Is it possible that you are able to (play|perform|do) ***Sport*** with (a(n)) ***Symptom*** (and (a(n)) ***Symptom***)?

Where the classes can be replaces with instances of the classes. Example: ***Sport*** can be replaced with ***soccer***.

### Example Queries:
- Does eating pasta bolognese cause high cholesterol?
- Does eating tagine cause high cholesterol?
- Can not being able to do walking be caused by playing field hockey?
- Can not being able to play field hockey be caused by walking?
- Does walking provide any health benefit that is not provided by weight lifting?
- Does playing field hockey provide any health benefit that is not provided by running?
- Does ramen provide the required nutrients for weight lifting?
- Does chicken curry provide the required nutrients for running?
- Can someone with an egg allergy eat ramen?
- Can someone with a gluten allergy eat pasta bolognese?
- Can someone with a lactose allergy eat pasta bolognese?
- Does eating tagine help against dizziness and a fever?
- Is it possible that you are able to play soccer with dizziness and a fever?
- Is it possible that you are able to do walking with dizziness?


## Short Overview

__llm_check.py__ is a file that contains the code for the LLM check. It is used to check the truth of a statement using an LLM.

__ontology_check.py__ is a file that contains the code for the ontology check. It matches the user query to one of the queries templates and then checks the truth of the statement using the ontology.

__utils.py__ is a file that contains the code for the utils. It is used to check the truth of a statement using the ontology.

__main.py__ is the file that is used to run the code. It is the entry point of the code and performs the checks and returns the appropriate response.

__queries.py__ is a file that contains the code for the SPARQL queries.



