import os
import sqlite3
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Retrieve Groq API key
groq_api_key = os.getenv("GROQCLOUD_API_KEY")

# Connect to SQLite database
db_path = 'northwind.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def query_database(query):
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def main():
    print("Welcome to the LLM-powered SQL Query Agent!")
    
    prompt_template = (
        "You are a helpful assistant that translates English questions into SQL queries, executes them on a database, "
        "and returns the results along with a plain English explanation. Here is the conversation history: {history}\n"
        "Question: {input}\n"
        "Step-by-step SQL Query and Explanation:"
    )
    
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=prompt_template
    )
    
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name="llama3-70b-8192"  # Specify your model name here
    )
    
    conversation = ConversationChain(
        llm=groq_chat,
        prompt=prompt
    )

    print("Start asking your questions. Type 'exit' to end the session.")
    while True:
        user_question = input("Ask your question here: ")
        if user_question.lower() == "exit":
            break

        # Generate SQL query using LLM with ReAct technique
        response = conversation.invoke({"input": user_question})
        response_text = response['response']
        
        # Extract the SQL query part
        if "SQL Query:" in response_text:
            sql_query = response_text.split("SQL Query:")[1].split("Explanation:")[0].strip()
        else:
            print("Failed to generate a valid SQL query.")
            continue

        print(f"SQL Query: {sql_query}")

        try:
            # Execute the SQL query
            result = query_database(sql_query)
            print(f"Results: {result}")

            # Generate a plain English explanation of the result
            explanation = conversation.invoke({"input": f"Explain the results of the SQL query: {sql_query}"})
            explanation_text = explanation['response'].split("Explanation:")[1].strip() if "Explanation:" in explanation['response'] else explanation['response']
            print(f"Explanation: {explanation_text}")
        except Exception as e:
            print(f"Error: {str(e)}")

        print("---")

if __name__ == "__main__":
    main()
