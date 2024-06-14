import os
import re
import sqlite3
from dotenv import load_dotenv
from groq import Groq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

load_dotenv()

groq_api_key = os.getenv("GROQCLOUD_API_KEY")
database_path = "northwind.db"

def main():
    # Initialize the LLM
    model = "Mixtral-8x7b-32768"
    memory = ConversationBufferMemory(k=5)

    prompt_template = (
        "You are a helpful assistant that translates plain English questions into SQL queries. "
        "Here is the conversation history: {history}\n Also don;t show this i just use future purpose"
        "Here is a question from the user: {input}\n Don't show this in your response"
        "Provide a detailed and comprehensive answer, including the SQL query and results from given database, if applicable."
    )

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=prompt_template
    )

    groq_chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model
    )

    conversation = ConversationChain(
        llm=groq_chat,
        memory=memory,
        prompt=prompt
    )

    print("Welcome to the SQL Query Agent. Type your question below.")

    while True:
        user_input = input(">> ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = conversation.invoke({"input": user_input})

        # Debugging: Print the full response to understand its structure
        print("Debugging: Full Response")
        print(response)

        try:
            # Extract the SQL query from the response
            sql_query_match = re.search(r'```sql\n(.*?)\n```', response['response'], re.DOTALL)
            if sql_query_match:
                sql_query = sql_query_match.group(1).strip()
                print(f"Executing SQL Query: {sql_query}")

                # Execute the SQL query
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute(sql_query)
                results = cursor.fetchall()
                conn.close()

                # Print the results
                print("Results:")
                for row in results:
                    print(row)
            else:
                print("Error: SQL query not found in the response.")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
