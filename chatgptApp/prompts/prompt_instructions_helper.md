
## Improve your prompt considering:
<br>

### 1. Give the model excessive information in addition to your prompt

Use delimiters to clearly indicate distinct parts of the input

```python
prompt = f"""
Summarize the text delimited by triple backticks
```{text}```
"""
```
Request specific formatting:

```python
prompt = f"""
Provide them in JSON format with the following keys: 
book_id, title, author, genre.
"""
```

Add context to the prompt:

```python
prompt = f"""
Your task is to answer in a consistent style.

<child>: Teach me about patience.

<grandparent>: The river that carves the deepest \ 
valley flows from a modest spring; the \ 
grandest symphony originates from a single note; \ 
the most intricate tapestry begins with a solitary thread.

<child>: Teach me about resilience.
"""
```

Specify a sequence of steps required to solve the task:

```python
prompt_1 = f"""
Perform the following actions: 
1 - Summarize the following text delimited by triple \
backticks with 1 sentence.
2 - Translate the summary into French.
3 - List each name in the French summary.
4 - Output a json object that contains the following \
keys: french_summary, num_names.

Separate your answers with line breaks.

Text:
```{text}```
"""
```

### 2. Use specifically provided instructions, such as the: 
- number of sentences to summarize, or the number of names to list
- write the output in a specific format, such as JSON
- provide keywords for focus or context

### 3. Provide direct instructions in the prompt, such as:

```python
prompt = f"""
What is the sentiment of the following product review, 
which is delimited with triple backticks?

Give your answer as a single word, either "positive" \
or "negative".

Review text: '''{lamp_review}'''
"""

```

### 4. Use specific instructions for extracting information from the prompt, such as:

```python 
prompt = f"""
Identify the following items from the review text: 
- Item purchased by reviewer
- Company that made the item

The review is delimited with triple backticks. \
Format your response as a JSON object with \
"Item" and "Brand" as the keys. 
If the information isn't present, use "unknown" \
as the value.
Make your response as short as possible.
  
Review text: '''{lamp_review}'''
"""
``` 

### 5. Write specific instruction for transforming the input, such as:

```python
prompt = f"""
Translate the following English text to Spanish: \ 
```Hi, I would like to order a blender```
"""
```

or 

```python
prompt = f"""
Translate the following python dictionary from JSON to an HTML \
table with column headers and title: {data_as_python_dict}
"""
```

### 6. Combine multiple instructions, such as:

```python
prompt = f"""
You are a customer service AI assistant.
Your task is to send an email reply to a valued customer.
Given the customer email delimited by ```, \
Generate a reply to thank the customer for their review.
If the sentiment is positive or neutral, thank them for \
their review.

If the sentiment is negative, apologize and suggest that \
they can reach out to customer service. 

Make sure to use specific details from the review.

Write in a concise and professional tone.

Sign the email as `AI customer agent`.
Customer review: ```{review}```
Review sentiment: {sentiment}
"""
```

