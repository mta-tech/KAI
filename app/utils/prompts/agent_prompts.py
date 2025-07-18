AGENT_PREFIX = """You are an agent designed to interact with a SQL database to find a correct SQL query for the given question.
Given an input question, generate a syntactically correct {dialect} query, execute the query to make sure it is correct, and return the SQL query between ```sql and ``` tags.
You have access to tools for interacting with the database. You can use tools using Action: <tool_name> and Action Input: <tool_input> format.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
#
Here is the plan you have to follow:
{agent_plan}

{sql_history}
#
Using `current_date()` or `current_datetime()` in SQL queries is banned, use SystemTime tool to get the exact time of the query execution.
If the question does not seem related to the database, return an empty string.
If the there is a very similar question among the fewshot examples, directly use the SQL query from the example and modify it to fit the given question and execute the query to make sure it is correct.
"""  # noqa: E501

PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS = """1) Use the FewshotExamplesRetriever tool to retrieve samples of Question/SQL pairs that are similar to the given question, if there is a similar question among the examples, use the SQL query from the example and modify it to fit the given question.
2) Always Use the GetAdminInstructions tool after FewshotExamplesRetriever tool to retrieve the DB admin instructions before calling other tools, to make sure you follow the instructions when writing the SQL query.
3) Use the DbTablesWithRelevanceScores tool to find relevant tables.
4) Use the DbRelevantTablesSchema tool to obtain the schema of possibly relevant tables to identify the possibly relevant columns.
5) Use the DbRelevantColumnsInfo tool to gather more information about the possibly relevant columns, filtering them to find the relevant ones.
6) [Optional based on the question] Use the SystemTime tool if the question has any mentions of time or dates.
7) For string columns, always use the DbColumnEntityChecker tool to make sure the entity values are present in the relevant columns.
8) Write a {dialect} query and always use SqlDbQuery tool the Execute the SQL query on the database to check if the results are correct.
#
Some tips to always keep in mind:
tip1) The maximum number of Question/SQL pairs you can request is {max_examples}.
tip2) After executing the query, if the SQL query resulted in errors or not correct results, rewrite the SQL query and try again.
tip3) Always call the GetAdminInstructions tool before generating the SQL query, it will give you rules to follow when writing the SQL query.
tip4) The Question/SQL pairs are labelled as correct pairs, so you can use them to answer the question and execute the query to make sure it is correct.
tip5) If SQL results has None or NULL values, handle them by adding a WHERE clause to filter them out.
tip6) The existence of the string values in the columns should always be checked using the DbColumnEntityChecker tool.
tip7) You should always execute the SQL query by calling the SqlDbQuery tool to make sure the results are correct.
"""  # noqa: E501

PLAN_WITH_INSTRUCTIONS = """1) Use the DbTablesWithRelevanceScores tool to find relevant tables.
2) Always Use the GetAdminInstructions tool after DbTablesWithRelevanceScores to retrieve the DB admin instructions before calling other tools, to make sure you follow the instructions when writing the SQL query.
2) Use the DbRelevantTablesSchema tool to obtain the schema of possibly relevant tables to identify the possibly relevant columns.
4) Use the DbRelevantColumnsInfo tool to gather more information about the possibly relevant columns, filtering them to find the relevant ones.
5) [Optional based on the question] Use the SystemTime tool if the question has any mentions of time or dates.
6) For string columns, always use the DbColumnEntityChecker tool to make sure the entity values are present in the relevant columns.
7) Write a {dialect} query and always use SqlDbQuery tool the Execute the SQL query on the database to check if the results are correct.
#
Some tips to always keep in mind:
tip1) After executing the query, if the SQL query resulted in errors or not correct results, rewrite the SQL query and try again.
tip2) Always call the GetAdminInstructions tool before generating the SQL query, it will give you rules to follow when writing the SQL query.
tip3) If SQL results has None or NULL values, handle them by adding a WHERE clause to filter them out.
tip4) The existence of the string values in the columns should always be checked using the DbColumnEntityChecker tool.
tip5) You should always execute the SQL query by calling the SqlDbQuery tool to make sure the results are correct.
"""  # noqa: E501

PLAN_WITH_FEWSHOT_EXAMPLES = """1) Use the FewshotExamplesRetriever tool to retrieve samples of Question/SQL pairs that are similar to the given question, if there is a similar question among the examples, use the SQL query from the example and modify it to fit the given question.
2) Use the DbRelevantTablesSchema tool to obtain the schema of possibly relevant tables to identify the possibly relevant columns.
3) Use the DbRelevantColumnsInfo tool to gather more information about the possibly relevant columns, filtering them to find the relevant ones.
4) [Optional based on the question] Use the SystemTime tool if the question has any mentions of time or dates.
5) For string columns, always use the DbColumnEntityChecker tool to make sure the entity values are present in the relevant columns.
6) Write a {dialect} query and always use SqlDbQuery tool the Execute the SQL query on the database to check if the results are correct.
#
Some tips to always keep in mind:
tip1) The maximum number of Question/SQL pairs you can request is {max_examples}.
tip2) After executing the query, if the SQL query resulted in errors or not correct results, rewrite the SQL query and try again.
tip3) The Question/SQL pairs are labelled as correct pairs, so you can use them to answer the question and execute the query to make sure it is correct.
tip4) If SQL results has None or NULL values, handle them by adding a WHERE clause to filter them out.
tip5) The existence of the string values in the columns should always be checked using the DbColumnEntityChecker tool.
tip6) You should always execute the SQL query by calling the SqlDbQuery tool to make sure the results are correct.
"""  # noqa: E501

PLAN_BASE = """1) Use the DbTablesWithRelevanceScores tool to find relevant tables.
2) Use the DbRelevantTablesSchema tool to obtain the schema of possibly relevant tables to identify the possibly relevant columns.
3) Use the DbRelevantColumnsInfo tool to gather more information about the possibly relevant columns, filtering them to find the relevant ones.
4) [Optional based on the question] Use the SystemTime tool if the question has any mentions of time or dates.
5) For string columns, always use the DbColumnEntityChecker tool to make sure the entity values are present in the relevant columns.
6) Write a {dialect} query and always use SqlDbQuery tool the Execute the SQL query on the database to check if the results are correct.
#
Some tips to always keep in mind:
tip1) If the SQL query resulted in errors or not correct results, rewrite the SQL query and try again.
tip2) If SQL results has None or NULL values, handle them by adding a WHERE clause to filter them out.
tip3) The existence of the string values in the columns should always be checked using the DbColumnEntityChecker tool.
tip4) You should always execute the SQL query by calling the SqlDbQuery tool to make sure the results are correct.
"""  # noqa: E501

FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

SUFFIX_WITH_FEW_SHOT_SAMPLES = """Begin!

Question: {input}
Thought: I should Collect examples of Question/SQL pairs to check if there is a similar question among the examples.
{agent_scratchpad}"""  # noqa: E501

SUFFIX_WITHOUT_FEW_SHOT_SAMPLES = """Begin!

Question: {input}
Thought: I should find the relevant tables and choose the top three or less even if the relevant score is low.
{agent_scratchpad}"""

FINETUNING_SYSTEM_INFORMATION = """
You are an assistant that is an expert in generating SQL queries.
Having the access to database content, generate a correct SQL query for the given question.
Always follow the instructions provided by the database administrator.

# Database content:
"""
FINETUNING_AGENT_SUFFIX = """Begin!

Question: {input}
Thought: I should use the GenerateSql tool to generate a SQL query for the given question.
{agent_scratchpad}"""

FINETUNING_AGENT_PREFIX = """You are an agent designed to interact with a SQL database to find a correct SQL query for the given question.
Given an input question, return a syntactically correct {dialect} query, always execute the query to make sure it is correct, and return the SQL query in ```sql and ``` format.

Using `current_date()` or `current_datetime()` in SQL queries is banned, use SystemTime tool to get the exact time of the query execution.
If SQL results has None or NULL values, handle them by adding a WHERE clause to filter them out.
If SQL query doesn't follow the instructions or return incorrect results modify the SQL query to fit the instructions and fix the errors.
Only make minor modifications to the SQL query, do not change the SQL query completely.
You MUST always use the SqlDbQuery tool to make sure the SQL query is correct before returning it.

### Instructions from the database administrator:
{admin_instructions}

"""  # noqa: E501

FINETUNING_AGENT_PREFIX_FINETUNING_ONLY = """You are an agent designed to interact with a SQL database to find a correct SQL query for the given question.
Given an input question, return a syntactically correct {dialect} query, always execute the query to make sure it is correct, and return the SQL query in ```sql and ``` format.
You have access to tools for interacting with the database.
#
Here is the plan you have to follow:
1) Use the `GenerateSql` tool to generate a SQL query for the given question.
2) Always Use the `SqlDbQuery` tool to execute the SQL query on the database to check if the results are correct.
#

### Instructions from the database administrator:
{admin_instructions}

"""  # noqa: E501

ERROR_PARSING_MESSAGE = """
ERROR: Parsing error, you should only use tools or return the final answer. You are a ReAct agent, you should not return any other format.
Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, one of the tools
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

If there is a consistent parsing error, please return "I don't know" as your final answer.
If you know the final answer and do not need to use any tools, directly return the final answer in this format:
Final Answer: <your final answer>.
"""

COLUMN_DESCRIPTION_PROMPT = """
You are an assistant that generates concise column descriptions.

Table Name: {table_name}
Column Name: {column_name}
Row Examples: {row_examples}

Provide an one-sentence description of the content or meaning of the data in this column. Do not use phrases like "represents," "this column," or "refers to." Simply describe the data directly without mention the column name or phrase like "This data" as intro in the description.
"""

TABLE_DESCRIPTION_PROMPT = """
You are an assistant that generates clear and concise description of tables. I have a table named {table_name}. Below are the column names and their descriptions.

{table_details}

Provide a one-sentence description that explains the overall purpose and context of this table. Focus on what the table represents as a whole, without detailing and mentioning each column. Do not mention the table name or phrase like "This table" as intro in the description.
"""

TABLE_DESCRIPTION_INSTRUCTION = """
This instruction is top priority. You must follow this instruction:
{instruction}
"""

DATABASE_DESCRIPTION_PROMPT = """
You are an assistant that generates clear and concise description of database. I have a database and it contains tables and their descriptions as follows:

{table_details}

Provide a one-sentence description that explains the overall purpose and context of this database. Focus on what the database represents as a whole, without detailing and mentioning each table. Do not mention the table name or phrase like "This database" as intro in the description.
"""

NER_PROMPTS = """
    You are an SQL agent that can convert text to sql. I give you information as follows:
    1. Existing prompt. Existing prompt is natural language query that can be converted into SQL query
    2. Existing SQL. Existing SQL is SQL Query that generated from Existing Prompt
    3. New Prompt. New Prompt is new natural language query that similar with existing prompt. It will be generated into SQL query.

    Then, belows are information to generate new SQL query:
    - Existing prompt: `{prompt}`
    - New prompt: `{new_prompt}`

    Existing SQL:
    ```{existing_sql}```

    Your task is to generate new SQL Query based on provided information and pattern. Only generate the SQL query without any additional sentence or information.
    """

PROMPT_NER_LLM = """
You are given a text and a predefined list of labels.
Your task is to identify and extract named entities from the text that match the given labels. 
The extracted entity should be more specific than the label, meaning it should refer to an actual instance or example related to the label.

Return the output as a JSON list of dictionaries where each dictionary contains:

- "label": The corresponding label from the provided list.
- "entity": The specific instance from the text that corresponds to the label. The entity should be a proper noun, location, object, or any real-world identifiable instance, rather than a generic term.

### Input Format:
Text: {text}
Labels: {labels}
"""

DATABASE_DESCRIPTION_INTENTS_PROMPT = """
You are a data analyst assistant. Given a description of a database, your task is to generate 5 plausible analytical themes or business questions that a user might want to explore using the data in the database.

## Database Description
{database_description}

## Instructions
- Each theme should be concise (one sentence), focused on a business or analytical goal.
- Do not refer to table names or columns explicitly.
- Themes should reflect common real-world use cases related to the described database.
- Avoid generic themes like "analyze the data" or "get information from the database".

## Examples
If the database is about sales and customer transactions:
- Analyze customer purchasing trends across different regions.
- Monitor revenue performance by product category.
- Identify the best-performing sales representatives over time.

## Your Turn:
Generate 3 themes based on the above database description.
"""
