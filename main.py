import platform
import os
import pyodbc
import urllib
import openai
import sqlalchemy
import streamlit as st
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain import PromptTemplate
from langchain.llms import AzureOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent

openai.api_type = "azure"
openai.api_base = 'https://endpoint.openai.azure.com/'
openai.api_version = "2022-12-01"
openai.api_key = '487bb3c64c354640b8c30790bc62d085'


server = 'foodhealth.database.windows.net'
database = 'foodhealth'
username = 'amimukherjee'
password = 'Amit@520894'   
driver= 'ODBC Driver 17 for SQL Server'

model = 'text-davinci-003'


def db_instance():
    #Creating SQLAlchemy connection sting
    #conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    #params = urllib.parse.quote_plus('Driver={ODBC Driver 17 for SQL Server};Server=tcp:foodhealth.database.windows.net,1433;Database=foodhealth;Uid=amimukherjee;Pwd=Amit@520894;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    params = urllib.parse.quote_plus('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')

    conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)

    db_instance = SQLDatabase.from_uri(conn_str)
    return db_instance

def main():
    llm = AzureOpenAI(
    deployment_name=model, 
    model_name=model,
    openai_api_key = openai.api_key,
    temperature= 0,
    max_tokens=500,
    streaming = True)

    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {top_k} results, DO NOT use LIMIT clause in the generated sql query instead use TOP clause as per mssql. You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Use the following format:
    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here"
    Only use the tables listed below.
    {table_info}
    If someone asks for the table foobar, they really mean the employee table.
    Question: {input}"""

    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect", "top_k"],
        template=_DEFAULT_TEMPLATE,
    )


    db = db_instance()
    #db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=PROMPT, verbose=True, return_intermediate_steps=True, top_k=10)
    
    #result = db_chain("What types of inspections does the authorities conduct and how often do they occur in general? Provide both type and count in ascending order")
    #result = db_chain("Find the restaurant owners (owner_name) that own one or multiple restaurants in the city with the number of restaurants (num_restaurants) they own. Find the first top 10 owners ordered by descending order using the number of restaurants.")
    #result = db_chain("From the businesses table, select the top 10 most popular postal_code. They should be filtered to only count the restaurants owned by people/entities that own 5 or more restaurants. The final result should return a row (postal_code, count) for each 10 selection and be sorted by descending order to get the most relevant zip codes.")
    
    #print(result["intermediate_steps"])
 
    st.set_page_config('Query database in natural language', page_icon=":robot:")
    st.header('Query database in natural language')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("Often business professionals wants to intract with database without writing a SQL query. \n\n This demo \
                    will help you to demonostrate Azure OpenAI capablity to intract with Azure SQL without writing any single SQL code. \
                    This demo is powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) and [LangChain](https://langchain.readthedocs.io/en/latest/index.html)")
    with col2:
        st.image(image='pic.jpg', width=400)

    st.markdown("## Enter Your query")

    def get_text():
        input_text = st.text_area(height = 200, label="Entery your business query", label_visibility='collapsed', placeholder="Enter query...", key="query_input")
        return input_text
    
    query_input = get_text()

    if query_input:

        db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=PROMPT, verbose=True, return_intermediate_steps=True, top_k=10)
        
        result = db_chain(query_input)

        st.markdown("### Here is your Answer")
        st.write(result['result'])

        st.markdown("### Here SQL query runs agains the DB")
        st.write(result["intermediate_steps"][0])

        st.markdown("### Here SQL query output")
        st.write(result["intermediate_steps"][1])

main()