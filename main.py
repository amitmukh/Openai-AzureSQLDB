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
    max_tokens=500)

    prompt_template="""Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Use the following format:

    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here"

    Only use the following tables:

    {table_info}

    If someone asks for the table foobar, they really mean the employee table.

    Question: {input}"""
    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=prompt_template
    )

    db = db_instance()
    db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=PROMPT, verbose=True, return_intermediate_steps=True)

    result = db_chain("how many times restaurants in Market street (postal_code: 94103) has committed health violations and group them based on their risk category. The output should be (risk_category, count as frequency) and sorted in descending order by frequency")

    #result = db_chain("What types of inspections does the authorities conduct and how often do they occur in general? Provide both type and count in ascending order")
    #print(result["intermediate_steps"])

    st.set_page_config('Query database in natual language', page_icon=":robot:")
    st.header('Query database in natual language')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("Often business professionals wants to intract with database without writing a SQL query. \n\n This demo \
                    will help you to demonostrate Azure OpenAI capablity to intract with Azure SQL without writing any single SQL code. \
                    This demo is powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) and [LangChain](https://langchain.com/)")
    with col2:
        st.image(image='pic.jpg', width=400)

    st.markdown("## Enter Your query")

    def get_text():
        input_text = st.text_area(height = 400, label="Entery your business query", label_visibility='collapsed', placeholder="Enter query...", key="query_input")
        return input_text
    
    query_input = get_text()

    st.markdown("### Here is your Answer")
    st.write(result['result'])

    st.markdown("### Here SQL query runs agains the DB")
    st.write(result["intermediate_steps"][0])

    st.markdown("### Here SQL query output")
    st.write(result["intermediate_steps"][1])

main()